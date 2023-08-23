from typing import List, Any
from server.match import Match
from server.event_handler import OmnipotentGuideEventHandler
from agents.agent_base import AgentBase
from utils import BaseModel


def set_16_omni(match: Match):
    match.match_config.initial_dice_number = 16
    match.event_handlers.append(OmnipotentGuideEventHandler())


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
        if isinstance(value, BaseModel):
            remove_ids(value)
        elif isinstance(value, list) or isinstance(value, tuple):
            for v in value:
                if isinstance(v, BaseModel):
                    remove_ids(v)
    if 'id' in model.__fields__.keys():
        model.id = 0
    return model
