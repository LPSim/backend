"""
Modifications for tianshou.
"""

import types
from torch import nn
import warnings
import gymnasium as gym
from gymnasium import Space
import numpy as np
from typing import Any, Callable, Dict, Optional, Union
from tianshou.data import (
    Collector as TianshouCollector,
    AsyncCollector as TianshouAsyncCollector,
    Batch,
    ReplayBuffer,
)
from tianshou.env import (  # noqa
    PettingZooEnv as TianshouPettingZooEnv,
    DummyVectorEnv,
    BaseVectorEnv,
    SubprocVectorEnv,  # noqa
)
from tianshou.policy import MultiAgentPolicyManager, BasePolicy
from tianshou.utils import MultipleLRSchedulers
from torch.optim.lr_scheduler import LambdaLR

from lpsim.agents.nothing_agent import NothingAgent
from lpsim.agents.random_agent import RandomAgent
from lpsim.env.env import LPSimBaseV0Env
from lpsim.env.wrappers import (
    ArrayActionWrapper,
    ArrayLikeObservationWrapper,
    AutoDiceWrapper,
)
from lpsim.agents import Agents

# from pettingzoo.classic import rps_v2
from pettingzoo.utils.wrappers import BaseWrapper

from lpsim.server.deck import Deck
from lpsim.server.interaction import (
    ChooseCharacterResponse,
    DeclareRoundEndResponse,
    ElementalTuningResponse,
    Requests,
    RerollDiceResponse,
    Responses,
    SwitchCardResponse,
    SwitchCharacterResponse,
    UseCardResponse,
    UseSkillResponse,
)
from lpsim.server.match import Match, MatchConfig


class LPSimAgent2TianshouPolicy(BasePolicy):
    """
    Wraps LPSim agent to tianshou policy, and can be used in tianshou multi-agent
    learning.
    """

    def __init__(
        self,
        agent: Agents,
        observation_space: Space | None = None,
        action_space: Space | None = None,
        action_scaling: bool = False,
        action_bound_method: str = "",
        lr_scheduler: LambdaLR | MultipleLRSchedulers | None = None,
    ) -> None:
        super().__init__(
            observation_space,
            action_space,
            action_scaling,
            action_bound_method,
            lr_scheduler,
        )
        self.agent = agent

    def forward(
        self,
        batch: Batch,
        state: Optional[Union[dict, Batch, np.ndarray]] = None,
        **kwargs: Any,
    ) -> Batch:
        """
        Extract action from agent.
        """
        # print('forward batch', len(batch))
        responses = []
        for obs in batch.obs:
            if isinstance(obs, Match):
                resp = self.agent.generate_response(obs)
            elif isinstance(obs, Batch) and "requests" in obs:
                # requests are set
                fake_match = Match()
                fake_match.requests = [x for x in obs["requests"] if x is not None]
                resp = self.agent.generate_response(fake_match)
            else:
                raise ValueError(f"Unknown obs type {type(obs)}")
            assert resp is not None
            responses.append(resp)
        return Batch(act=np.array(responses))

    def learn(self, batch: Batch, **kwargs: Any) -> dict[str, float]:
        """currently the agent learns nothing, it returns an empty dict."""
        print("learn batch", len(batch))
        return {}


class CommandActionPolicy(LPSimAgent2TianshouPolicy):
    """
    Convert action to command. When add_dice_in_output is False, dice information
    will not included in the output, and output is in length 3. Otherwise, output is in
    length 4.
    Note if add_dice_in_output is False, SwitchCardResponse cannot be performed, as it
    uses dice to represent card index. TODO: maybe we can use target to represent?
    """

    def __init__(self, *args, add_dice_in_output: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_dice_in_output = add_dice_in_output

    def _request_idx_in_list(self, request: Requests, req_list: list[Requests]) -> int:
        return req_list.index(request)

    def _idx_list_to_number(self, idx_list: list[int]) -> int:
        return sum([1 << i for i in idx_list])

    def forward(
        self,
        batch: Batch,
        state: Dict | Batch | np.ndarray | types.NoneType = None,
        **kwargs: Any,
    ) -> Batch:
        resp_batch = super().forward(batch, state, **kwargs)
        requests: list[list[Requests]] = []
        for obs in batch.obs:
            if isinstance(obs, Match):
                requests.append(obs.requests)
            elif isinstance(obs, Batch) and "requests" in obs:
                requests.append([x for x in obs["requests"] if x is not None])
        results = []
        for resp, reqs in zip(resp_batch.act, requests):
            rr: Responses = resp
            pidx = rr.player_idx
            ridx = self._request_idx_in_list(rr.request, reqs)
            target = 0
            dice = 0
            if isinstance(rr, SwitchCardResponse):
                dice = self._idx_list_to_number(rr.card_idxs)
            elif isinstance(rr, ChooseCharacterResponse):
                target = rr.character_idx
            elif isinstance(rr, RerollDiceResponse):
                dice = self._idx_list_to_number(rr.reroll_dice_idxs)
            elif isinstance(rr, SwitchCharacterResponse):
                dice = self._idx_list_to_number(rr.dice_idxs)
            elif isinstance(rr, ElementalTuningResponse):
                target = rr.card_idx
                dice = self._idx_list_to_number([rr.dice_idx])
            elif isinstance(rr, DeclareRoundEndResponse):
                pass
            elif isinstance(rr, UseSkillResponse):
                dice = self._idx_list_to_number(rr.dice_idxs)
            elif isinstance(rr, UseCardResponse):
                if rr.target is not None:
                    targets = rr.request.targets
                    target = targets.index(rr.target)
                dice = self._idx_list_to_number(rr.dice_idxs)
            else:
                raise ValueError(f"Unknown response type {type(rr)}")
            if self._add_dice_in_output:
                results.append((pidx, ridx, target, dice))
            else:
                results.append((pidx, ridx, target))
        return Batch(act=np.array(results))


class TableAttnFCNet(nn.Module):
    """
    Use Attention on multiple instance infos (e.g. status, character, summons),
    then cat same level data, until all table info is used.
    TODO: not implemented yet.
    """

    def __init__(
        self,
        observation_space: Space | None = None,
        action_space: Space | None = None,
    ) -> None:
        super().__init__()
        self.observation_space = observation_space
        self.action_space = action_space

    def forward(
        self,
        batch: Batch,
        state: Optional[Union[dict, Batch, np.ndarray]] = None,
        **kwargs: Any,
    ) -> Batch:
        """
        Input batch, output embedding for current status
        """
        # print('forward batch', len(batch))
        responses = []
        for obs in batch.obs:
            if isinstance(obs, Match):
                resp = self.agent.generate_response(obs)
            elif isinstance(obs, Batch) and "requests" in obs:
                # requests are set
                fake_match = Match()
                fake_match.requests = [x for x in obs["requests"] if x is not None]
                resp = self.agent.generate_response(fake_match)
            else:
                raise ValueError(f"Unknown obs type {type(obs)}")
            assert resp is not None
            responses.append(resp)
        return Batch(act=np.array(responses))

    def learn(self, batch: Batch, **kwargs: Any) -> dict[str, float]:
        """currently the agent learns nothing, it returns an empty dict."""
        print("learn batch", len(batch))
        return {}


class PettingZooEnv(TianshouPettingZooEnv):
    """The interface for petting zoo environments.

    Multi-agent environments must be wrapped as
    :class:`~tianshou.env.PettingZooEnv`. Here is the usage:
    ::

        env = PettingZooEnv(...)
        # obs is a dict containing obs, agent_id, and mask
        obs = env.reset()
        action = policy(obs)
        obs, rew, trunc, term, info = env.step(action)
        env.close()

    The available action's mask is set to True, otherwise it is set to False.
    Further usage can be found at :ref:`marl_example`.
    """

    def __init__(
        self,
        env: BaseWrapper,
        gym_reset_kwargs: dict[str, Any] = {},
    ):
        self.env = env
        # agent idx list
        self.agents = self.env.possible_agents
        self.agent_idx = {}
        for i, agent_id in enumerate(self.agents):
            self.agent_idx[agent_id] = i

        self.rewards = [0] * len(self.agents)  # type: ignore

        # Get first observation space, assuming all agents have equal space
        self.observation_space: Any = self.env.observation_space(self.agents[0])

        # Get first action space, assuming all agents have equal space
        self.action_space: Any = self.env.action_space(self.agents[0])

        assert all(
            self.env.observation_space(agent) == self.observation_space
            for agent in self.agents
        ), (
            "Observation spaces for all agents must be identical. Perhaps "
            "SuperSuit's pad_observations wrapper can help (usage: "
            "`supersuit.aec_wrappers.pad_observations(env)`"
        )

        assert all(
            self.env.action_space(agent) == self.action_space for agent in self.agents
        ), (
            "Action spaces for all agents must be identical. Perhaps "
            "SuperSuit's pad_action_space wrapper can help (usage: "
            "`supersuit.aec_wrappers.pad_action_space(env)`"
        )

        self.reset(**gym_reset_kwargs)


class Collector(TianshouCollector):
    def __init__(
        self,
        policy: BasePolicy,
        env: Union[gym.Env, BaseVectorEnv],
        buffer: Optional[ReplayBuffer] = None,
        preprocess_fn: Optional[Callable[..., Batch]] = None,
        exploration_noise: bool = False,
        gym_reset_kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        When initialize, can pass gym_reset_args.
        """
        if isinstance(env, gym.Env) and not hasattr(env, "__len__"):
            warnings.warn("Single environment detected, wrap to DummyVectorEnv.")
            self.env = DummyVectorEnv([lambda: env])  # type: ignore
        else:
            self.env = env  # type: ignore
        self.env_num = len(self.env)  # type: ignore
        self.exploration_noise = exploration_noise
        self._assign_buffer(buffer)
        self.policy = policy
        self.preprocess_fn = preprocess_fn
        self._action_space = self.env.action_space
        # avoid creating attribute outside __init__

        # used to cache gym_reset_kwargs
        self._last_gym_reset_kwargs = None

        self.reset(False, gym_reset_kwargs=gym_reset_kwargs)

    def reset_env(self, gym_reset_kwargs: Dict[str, Any] | None = None) -> None:
        if gym_reset_kwargs is None:
            gym_reset_kwargs = self._last_gym_reset_kwargs
        self._last_gym_reset_kwargs = gym_reset_kwargs
        return super().reset_env(gym_reset_kwargs)


class AsyncCollector(TianshouAsyncCollector, Collector):
    def __init__(self, *argv, **kwargs):
        Collector.__init__(self, *argv, **kwargs)


def get_env_args():
    mo_ying_cao_4_5 = (
        "2BPTnM7QxlTU+xjW2EMTuFrSzSQEy/PT1kTE/vbWznQDD4TTz2TUzvnT1nQj1JjU0PPD"
    )
    lin_ma_long_4_5 = (
        "4+Izp+vf5iPzG/zm5GJyq2nf5WPTCgLl5VLjrQXh5RMC2pvi3lNiDZzl3oNyHqPm35LS"
    )
    decks = [Deck.from_deck_code(mo_ying_cao_4_5), Deck.from_deck_code(lin_ma_long_4_5)]
    reset_args = {"options": {"decks": decks}}
    return reset_args


def get_lpsim_env():
    match_config = MatchConfig(max_round_number=999)
    original_env = LPSimBaseV0Env(match_config=match_config)
    original_env = ArrayLikeObservationWrapper(original_env)
    original_env = ArrayActionWrapper(original_env)
    original_env = AutoDiceWrapper(original_env)
    reset_args = get_env_args()
    env = PettingZooEnv(original_env, gym_reset_kwargs=reset_args)
    return env


def async_render(self, **kwargs: Any) -> list[Any]:
    """
    Render all of the environments. Will replace VectorEnv default render.
    It will not raise RuntimeError when env is still stepping, instead, it will output
    None.
    """
    self._assert_is_not_closed()
    res = []
    for idx, worker in enumerate(self.workers):
        if idx in self.waiting_id:
            res.append(None)
        else:
            res.append(worker.render(**kwargs))
    return res


if __name__ == "__main__":
    # env = rps_v2.env(render_mode="human")
    # env = PettingZooEnv(env)

    # Step 2: Wrap the environment for Tianshou interfacing
    env = get_lpsim_env()

    # Step 3: Define policies for each agent
    policies = MultiAgentPolicyManager(
        policies=[
            CommandActionPolicy(RandomAgent(player_idx=0), add_dice_in_output=False),
            CommandActionPolicy(NothingAgent(player_idx=1), add_dice_in_output=False),
        ],
        env=env,
    )

    # Step 4: Convert the env to vector format
    VectorEnv = DummyVectorEnv
    VectorEnv = SubprocVectorEnv
    VectorEnv = DummyVectorEnv
    env = VectorEnv(
        # [lambda: PettingZooEnv(original_env, gym_reset_kwargs=reset_args)]
        [get_lpsim_env] * 2,
        # wait_num=2,
        # timeout=None,
    )
    env.render = types.MethodType(async_render, env)

    reset_args = get_env_args()

    # Step 5: Construct the Collector, which interfaces the policies with the
    # vectorised environment
    collector = AsyncCollector(policies, env, gym_reset_kwargs=reset_args)

    # Step 6: Execute the environment with the agents playing for 1 episode, and render
    # a frame every 0.1 seconds
    result = collector.collect(n_episode=100, render=0.1, gym_reset_kwargs=reset_args)
    print("done")
