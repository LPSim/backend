import logging
from typing import Any, Sequence
import gymnasium
from pydantic import BaseModel

import lpsim
from lpsim.agents.random_agent import RandomAgent
from lpsim.server.deck import Deck
from lpsim.server.interaction import Responses
from lpsim.server.match import Match, MatchConfig
from lpsim.agents import Agents, InteractionAgent


try:
    from pettingzoo import AECEnv
    from pettingzoo.utils import agent_selector
    from pettingzoo.utils.wrappers import BaseWrapper
except ImportError:
    logging.warning(
        "pettingzoo is not installed, install it with `pip install lpsim[rl]`."
    )


# def env(render_mode=None):
#     """
#     The env function often wraps the environment in wrappers by default.
#     You can find full documentation for these methods
#     elsewhere in the developer documentation.
#     """
#     internal_render_mode = render_mode if render_mode != "ansi" else "human"
#     env = LPSimBaseV0Env(render_mode=internal_render_mode)
#     # This wrapper is only for environments which print results to the terminal
#     if render_mode == "ansi":
#         env = wrappers.CaptureStdoutWrapper(env)
#     # this wrapper helps error handling for discrete action spaces
#     env = wrappers.AssertOutOfBoundsWrapper(env)
#     # Provides a wide variety of helpful user errors
#     # Strongly recommended
#     env = wrappers.OrderEnforcingWrapper(env)
#     return env


class LPSimObservationSpace(gymnasium.Space):
    def __init__(self):
        pass

    @property
    def is_np_flattenable(self):
        return False

    def sample(self):
        raise NotImplementedError

    def contains(self, x: Any) -> bool:
        return isinstance(x, LPSimObservationSpace)

    def to_jsonable(self, sample_n: Sequence) -> list[Any]:
        return [x.json() for x in sample_n]

    def from_jsonable(self, sample_n: list[Any]) -> list:
        return [Match(**x) for x in sample_n]

    def __eq__(self, other):
        return isinstance(other, LPSimObservationSpace)


class ResponseParseClass(BaseModel):
    """
    This class is used to parse a response json to response instance.
    """

    resp: Responses


class LPSimActionSpace(gymnasium.Space):
    def __init__(self):
        pass

    @property
    def is_np_flattenable(self):
        return False

    def sample(self):
        raise NotImplementedError

    def contains(self, x: Any) -> bool:
        return isinstance(x, LPSimObservationSpace)

    def to_jsonable(self, sample_n: Sequence) -> list[Any]:
        return [x.json() for x in sample_n]

    def from_jsonable(self, sample_n: list[Any]) -> list:
        return [ResponseParseClass(resp=x).resp for x in sample_n]

    def __eq__(self, other):
        return isinstance(other, LPSimActionSpace)


class LPSimAgentSelector(agent_selector):
    """
    Outputs an agent when agent_select is called for LPSim environments.
    It will check match.requests to decide which agent should be selected.
    """

    def __init__(self, agent_order: list[str]):
        self._agent_order = agent_order

    def reinit(self, agent_order: list[str]) -> None:
        self._agent_order = agent_order

    def reset(self) -> Any:
        pass

    def next(self, match: Match) -> str:
        """Get the valid agent. There should be at least one valid request."""
        assert len(match.requests) > 0, "There should be at least one request."
        return self._agent_order[match.requests[0].player_idx]

    def is_last(self) -> bool:
        """Check if the current agent is the last agent in the cycle."""
        raise NotImplementedError

    def is_first(self) -> bool:
        """Check if the current agent is the first agent in the cycle."""
        raise NotImplementedError

    def __eq__(self, other: "LPSimAgentSelector") -> bool:
        raise NotImplementedError


class LPSimBaseV0Env(AECEnv[str, Any, Any]):  # type: ignore
    """
    The base environment of LPSim, which inherits AECEnv. The observation is
    the match instance, and accept Responses as action. observation space and action
    space is defined as LPSimObservationSpace and LPSimActionSpace, which will not
    contain useful information now, but they will return some samples when sampled from
    it.

    It will create two agents, 0 and 1. They will fight against each other.
    All actions receive 0 reward, except when anyone is defeated, and the winner
    receives 1 reward, and the loser receives -1 reward. The game will end after at most
    max_steps steps (count both agents' actions as one step).

    The card deck of each agent is defined when reset the environment.

    The metadata holds environment constants. From gymnasium, we inherit the
    "render_modes",
    metadata which specifies which modes can be put into the render() method.
    At least human mode should be supported.
    The "name" metadata allows the environment to be pretty printed.
    """

    metadata = {
        "render_modes": ["human"],
        "name": "LPSimBase_v0",
        "lpsim_version": "0.4.5.0",
    }

    def __init__(
        self,
        match_config: MatchConfig | None = None,
        observe_without_copy: bool = True,
        max_steps: int = 300,
        render_mode=None,
    ):
        """
        Initialize the environment.

        Args:
            match_config (MatchConfig | None): The configuration of the match.
            observe_without_copy (bool): Whether the observation should be a reference
                to the internal state of the environment.
            max_steps (int): The maximum steps of the game.
            render_mode (str): The render mode of the environment.

        The init method takes in environment arguments and
         should define the following attributes:
        - possible_agents
        - render_mode

        These attributes should not be changed after initialization.
        """
        self.possible_agents: list[str] = ["player_1", "player_2"]

        # optional: a mapping between agent name and ID
        # self.agent_name_mapping = dict(
        #     zip(self.possible_agents, list(range(len(self.possible_agents))))
        # )

        # optional: we can define the observation and action spaces here as attributes
        # to be used in their corresponding methods
        # self._action_spaces = {agent: Discrete(3) for agent in self.possible_agents}
        # self._observation_spaces = {
        #     agent: Discrete(4) for agent in self.possible_agents
        # }
        self.observe_without_copy = observe_without_copy
        self.max_steps = max_steps
        self.render_mode = render_mode

        # initialize match with config
        self.match_config = match_config
        self.match = None

        # check lpsim version
        if lpsim.__version__ != self.metadata["lpsim_version"]:
            logging.warning(
                f"lpsim version mismatch: {lpsim.__version__} "
                f"!= {self.metadata['lpsim_version']}. "
                "Environment may work incorrectly."
            )

    # Observation space should be defined here.
    # lru_cache allows observation and action spaces to be memoized, reducing clock
    # cycles required to get each agent's space.
    # If your spaces change over time, remove this line (disable caching).
    # @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        # gymnasium spaces are defined and documented here:
        # https://gymnasium.farama.org/api/spaces/
        # TODO can change during step.
        return LPSimObservationSpace()

    # Action space should be defined here.
    # If your spaces change over time, remove this line (disable caching).
    # @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        # TODO same above
        return LPSimActionSpace()

    def render(self):
        """
        Renders the environment. In human mode, it can print to terminal, open
        up a graphical window, or open up some other display that a human can see and
        understand.
        """
        assert self.match is not None
        round = self.match.round_number
        hps = [[y.hp for y in x.characters] for x in self.match.player_tables]
        print(f"Round: {round}, HPs: {hps}")

    def observe(self, agent: int):
        """
        When observe, full Match as observation is given. Note when
        self.observe_without_copy is True, the observation should be a reference to the
        internal state of the environment, and is possible to be modified by the agent.
        When disable copying, make sure it is not modified by the agent.
        """
        # observation of one agent is the previous state of the other
        # return np.array(self.observations[agent])
        assert (
            self.match is not None
        ), "Match is not initialized, please reset environment first."
        if self.observe_without_copy:
            return self.match
        return self.match.copy(deep=True)

    def state(self):
        """
        State and observation are the same.
        """
        return self.observe(0)

    def close(self):
        """
        Close should release any graphical displays, subprocesses, network connections
        or any other environment data which should not be kept around after the
        user is no longer using the environment.
        """
        pass

    def reset(
        self,
        seed=None,
        options: dict[str, Any] | None = None,
    ):
        """
        Initialize the environment. Will set self.match with specified decks and
        match_config, and other related attributes for AECEnv.

        Reset needs to initialize the following attributes
        - agents
        - rewards
        - _cumulative_rewards
        - terminations
        - truncations
        - infos
        - agent_selection
        And must set up the environment so that render(), step(), and observe()
        can be called without issues.
        Here it sets up the state dictionary which is used by step() and the
        observations dictionary which is used by step() and observe()
        """
        # if options is None:
        #     logging.warning("No options specified, use default options.")
        #     c = 'Mn8/BmRCMM/QI18+Qm8wJGI+Qo9wJ2M/O7BPN/E/O9CPOvU/O+C/PPg/PBA/PQBAPD8v'
        #     decks = [
        #         Deck.from_deck_code(c, version = '4.4'),
        #         Deck.from_deck_code(c, version = '4.4')
        #     ]
        #     options = {
        #         'decks': decks
        #     }
        assert options is not None, "The options should be specified."
        assert "decks" in options, "The decks should be specified."
        decks = options["decks"]
        self.agents = self.possible_agents[:]
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.history: dict[str, list[Responses]] = {agent: [] for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.total_step = 0
        self._agent_selector = LPSimAgentSelector(self.agents)

        self.match = Match(config=self.match_config)
        self.match.set_deck(decks)
        res, info = self.match.start()
        assert res, f"Failed to start match: {info}"
        self.match.step()
        self.agent_selection = self._agent_selector.next(self.match)

    def step(self, action: Responses):
        """
        step(action) takes in an action for the current agent (specified by
        agent_selection) and needs to update
        - rewards
        - _cumulative_rewards (accumulating the rewards)
        - terminations
        - truncations
        - infos
        - agent_selection (to the next agent)
        And any internal state used by observe() or render()
        """
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            # handles stepping an agent which is already dead
            # accepts a None action for the one agent, and moves the agent_selection to
            # the next dead agent,  or if there are no more dead agents, to the next
            # live agent
            self._was_dead_step(action)
            return

        agent = self.agent_selection
        agent_idx = self.agents.index(agent)
        assert agent_idx == action.player_idx, "Action is not for the current agent."

        # the agent which stepped last had its _cumulative_rewards accounted for
        # (because it was returned by last()), so the _cumulative_rewards for this
        # agent should start again at 0
        # self._cumulative_rewards[agent] = 0

        # stores action of current agent
        self.history[self.agent_selection].append(action)

        assert (
            self.match is not None
        ), "Match is not initialized, please reset environment first."
        self.match.respond(action)
        if len(self.match.requests) == 0:
            self.match.step()

        self.total_step += 1

        if self.match.is_game_end():
            # when game end, set rewards
            for agent in self.agents:
                self.rewards[agent] = -1
            if self.match.winner != -1:
                # anyone wins
                self.rewards[self.agents[self.match.winner]] = 1
            self.terminations = {agent: True for agent in self.agents}
        elif self.total_step >= self.max_steps:
            # when reach max steps, set rewards
            for agent in self.agents:
                self.rewards[agent] = -1
            self.truncations = {agent: True for agent in self.agents}
        else:
            # selects the next agent.
            self.agent_selection = self._agent_selector.next(self.match)

        # Adds .rewards to ._cumulative_rewards
        self._accumulate_rewards()

        if self.render_mode == "human":
            self.render()


class LPSimAgentWrapper(BaseWrapper[str, Any, Any]):  # type: ignore
    """
    This wrapper will use two lpsim agent to response to the environment. When agent
    is InteractionAgent, it will replace the response type in step from Responses to
    string. Otherwise, it will respond directly use specified agent, and do next step
    until it need InteractionAgent to respond or game end.
    """

    def __init__(self, env: AECEnv, agents: list[Agents]):
        super().__init__(env)
        assert "lpsim" in env.unwrapped.metadata["name"].lower(), (
            "The environment should be LPSim environment, "
            f"but got {env.unwrapped.metadata['name']}."
        )
        self.lpsim_agents = agents
        assert len(self.lpsim_agents) == 2, "The agents should be two."
        last_interactive_agent_idx = None
        for idx, agent in enumerate(self.lpsim_agents):
            assert (
                agent.player_idx == idx
            ), "The player_idx of agent should be the same as index."
            if type(agent) is InteractionAgent:
                if last_interactive_agent_idx is not None:
                    raise ValueError(
                        "There should be only one InteractionAgent in the agents."
                    )
                last_interactive_agent_idx = idx
        assert (
            last_interactive_agent_idx is not None
        ), "At least one agent should be InteractionAgent."
        self.last_interactive_agent = env.possible_agents[last_interactive_agent_idx]

    def _non_interactive_step(self) -> bool:
        """
        If currently requests a non-interactive agent, it will respond directly.

        If a non-interactive step is done, return True, otherwise return False.
        """
        agent = self.env.agent_selection
        agent_idx = self.env.agents.index(agent)
        if type(self.lpsim_agents[agent_idx]) is InteractionAgent:
            return False
        if self.env.terminations[agent] or self.env.truncations[agent]:
            # game has ended
            return False
        resp = self.lpsim_agents[agent_idx].generate_response(self.env.match)  # type: ignore  # noqa: E501
        self.env.step(resp)
        return True

    def reset(self, *argv, **kwargs):
        super().reset(*argv, **kwargs)

        # do non-interactive steps until we need to interact
        while self._non_interactive_step():
            pass

    def step(self, action: str) -> None:
        self.last_interactive_agent = self.env.agent_selection
        agent_idx = self.env.agents.index(self.last_interactive_agent)
        agent = self.lpsim_agents[agent_idx]
        assert type(agent) is InteractionAgent
        agent.commands = [action]
        resp = agent.generate_response(self.env.match)  # type: ignore
        self.env.step(resp)

        # do non-interactive steps until we need to interact
        while self._non_interactive_step():
            pass

    def last(
        self, observe: bool = True
    ) -> tuple[Any | None, float, bool, bool, dict[str, Any]]:
        """
        Different from the last method of AECEnv, it will return the observation
        of last interactive agent.
        """
        agent = self.last_interactive_agent
        assert agent is not None
        observation = self.observe(agent) if observe else None
        return (
            observation,
            self._cumulative_rewards[agent],
            self.terminations[agent],
            self.truncations[agent],
            self.infos[agent],
        )


class ModelAgent(InteractionAgent):
    """
    This agent will use a model to response to the environment. It will use the model
    to predict the response, and use the response to response to the environment.
    """

    def __init__(self, player_idx: int, model: Any):
        super().__init__(player_idx=player_idx)
        self.model = model

    def generate_response(self, match: Match) -> Responses:
        """
        Generate response for the match.

        Args:
            match (Match): The match instance.

        Returns:
            Responses: The response instance.
        """
        raise NotImplementedError


if __name__ == "__main__":
    match_config = MatchConfig(max_round_number=999)
    env = LPSimBaseV0Env(match_config=match_config)
    random_agent = RandomAgent(player_idx=0)
    interact_agent = InteractionAgent(player_idx=1)
    env = LPSimAgentWrapper(env, [random_agent, interact_agent])
    mo_ying_cao_4_5 = (
        "2BPTnM7QxlTU+xjW2EMTuFrSzSQEy/PT1kTE/vbWznQDD4TTz2TUzvnT1nQj1JjU0PPD"
    )
    lin_ma_long_4_5 = (
        "4+Izp+vf5iPzG/zm5GJyq2nf5WPTCgLl5VLjrQXh5RMC2pvi3lNiDZzl3oNyHqPm35LS"
    )
    decks = [Deck.from_deck_code(mo_ying_cao_4_5), Deck.from_deck_code(lin_ma_long_4_5)]
    env.reset(options={"decks": decks})
    while True:
        obs, rew, term, trunc, info = env.last()
        print(env.total_step)
        if term or trunc:
            break
        requests = env.match.requests
        agent_idx = env.agents.index(env.agent_selection)
        requests = [x for x in requests if x.player_idx == agent_idx]
        assert len(requests) > 0
        if requests[0].name == "ChooseCharacterRequest":
            cmd = f"choose {requests[0].available_character_idxs[0]}"
        elif requests[0].name == "SwitchCardRequest":
            cmd = "sw_card"
        elif requests[0].name == "RerollDiceRequest":
            cmd = "reroll"
        else:
            cmd = "end"
        env.step(cmd)
    print(f"Game end. Winner: {env.match.winner}")
