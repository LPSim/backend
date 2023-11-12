import numpy as np
from typing import List, Any
from src.lpsim.agents.interaction_agent import (
    InteractionAgent, InteractionAgent_V1_0
)
from src.lpsim.server.match import Match
from src.lpsim.server.event_handler import OmnipotentGuideEventHandler_3_3
from src.lpsim.agents.agent_base import AgentBase
from src.lpsim.server.struct import ObjectPosition
from src.lpsim.utils import BaseModel
from tests.default_random_state import get_default_random_state


def set_16_omni(match: Match):
    match.config.initial_dice_number = 16
    match.event_handlers.append(OmnipotentGuideEventHandler_3_3())


def make_respond(agent: AgentBase, match: Match, assertion: bool = True):
    """
    Make response once, and step the match until new request or
    game end, regardless of the target of requests.
    If not requesting this agent and nees assetion, raise AssertionError.
    Otherwise, do nothing.
    """
    resp = agent.generate_response(match)
    if assertion:
        assert resp is not None
    if resp is None:
        return
    match.respond(resp)
    match.step()


def check_hp(match: Match, hp: List[List[int]]):
    """
    input hps for each player and check
    """
    hps = [[x.hp for x in t.charactors] for t in match.player_tables]
    assert hps == hp


def check_name(name: str, lists: List[Any], exist: bool = True):
    """
    check the existence of name in lists
    """
    real_exist = name in [x.name for x in lists]
    assert real_exist == exist


def remove_ids(model: BaseModel) -> BaseModel:
    """
    remove ids of all objects in-place.
    """
    for key in model.__fields__.keys():
        value = getattr(model, key)
        if isinstance(value, ObjectPosition):
            model.__setattr__(key, value.set_id(0))
        elif isinstance(value, BaseModel):
            remove_ids(value)
        elif isinstance(value, list) or isinstance(value, tuple):
            assert isinstance(value, list)
            for num, v in enumerate(value):
                if isinstance(v, ObjectPosition):
                    value[num] = v.set_id(0)
                elif isinstance(v, BaseModel):
                    remove_ids(v)
    if 'id' in model.__fields__.keys():
        model.id = 0
    return model


def get_random_state(offset: int = 0):
    """
    get random state tuple for test. it will use a fixed random state and
    random offset times as the result random state.
    """
    state: List = get_default_random_state()
    if offset > 0:
        random_state = np.random.RandomState()
        state[1] = np.array(state[1], dtype = 'uint32')
        random_state.set_state(state)  # type: ignore
        for _ in range(offset):
            random_state.random()
        state = list(random_state.get_state(legacy = True))  # type: ignore
        state[1] = state[1].tolist()
    return state


def get_test_id_from_command(agent: InteractionAgent | InteractionAgent_V1_0):
    """
    from commands to get test number. return test number and remove this
    test message from commands if success. otherwise return 0.
    A command should like: `TEST 1 other information about this test`,
    and will return 1.
    """
    if len(agent.commands) == 0:  # pragma: no cover
        return 0
    command = agent.commands[0]
    if command.startswith('TEST'):
        agent.commands = agent.commands[1:]
        return int(command.split(' ')[1])
    return 0


def enable_logging():  # pragma: no cover
    import logging
    logging.basicConfig(level = logging.INFO)


def get_pidx_cidx(cmd):
    return int(cmd[2][1]), int(cmd[2][3])


def check_usage(data, usage_strs):
    usage = [int(x) for x in usage_strs]
    assert len(data) == len(usage)
    for u, d in zip(usage, data):
        assert u == d.usage
