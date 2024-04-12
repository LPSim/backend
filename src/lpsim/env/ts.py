"""
Modifications for tianshou.
"""
import warnings
import gymnasium as gym
from gymnasium import Space
import numpy as np
from typing import Any, Callable, Dict, Optional, Union
from tianshou.data import Collector as TianshouCollector, Batch, ReplayBuffer
from tianshou.env import (
    PettingZooEnv as TianshouPettingZooEnv,
    DummyVectorEnv,
    BaseVectorEnv,
)
from tianshou.policy import MultiAgentPolicyManager, BasePolicy
from tianshou.utils import MultipleLRSchedulers
from torch.optim.lr_scheduler import LambdaLR

from lpsim.agents.nothing_agent import NothingAgent
from lpsim.agents.random_agent import RandomAgent
from lpsim.env.env import LPSimBaseV0Env
from lpsim.agents import Agents

# from pettingzoo.classic import rps_v2
from pettingzoo.utils.wrappers import BaseWrapper

from lpsim.server.deck import Deck
from lpsim.server.match import MatchConfig


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
        responses = []
        for obs in batch.obs:
            resp = self.agent.generate_response(obs)
            assert resp is not None
            responses.append(resp)
        return Batch(act=np.array(responses))

    def learn(self, batch: Batch, **kwargs: Any) -> dict[str, float]:
        """currently the agent learns nothing, it returns an empty dict."""
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
    reset_args = get_env_args()
    env = PettingZooEnv(original_env, gym_reset_kwargs=reset_args)
    return env


if __name__ == "__main__":
    # env = rps_v2.env(render_mode="human")
    # env = PettingZooEnv(env)

    # Step 2: Wrap the environment for Tianshou interfacing
    env = get_lpsim_env()

    # Step 3: Define policies for each agent
    policies = MultiAgentPolicyManager(
        policies=[
            LPSimAgent2TianshouPolicy(RandomAgent(player_idx=0)),
            LPSimAgent2TianshouPolicy(NothingAgent(player_idx=1)),
        ],
        env=env,
    )

    # Step 4: Convert the env to vector format
    env = DummyVectorEnv(
        # [lambda: PettingZooEnv(original_env, gym_reset_kwargs=reset_args)]
        [get_lpsim_env] * 2
    )

    reset_args = get_env_args()

    # Step 5: Construct the Collector, which interfaces the policies with the
    # vectorised environment
    collector = Collector(policies, env, gym_reset_kwargs=reset_args)

    # Step 6: Execute the environment with the agents playing for 1 episode, and render
    # a frame every 0.1 seconds
    result = collector.collect(n_episode=3, render=0.1, gym_reset_kwargs=reset_args)
    print("done")
