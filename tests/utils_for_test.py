import json
import numpy as np
from typing import Callable, Dict, List, Any, Tuple
from lpsim.agents.interaction_agent import InteractionAgent, InteractionAgent_V1_0
from lpsim.server.match import Match, MatchConfig, MatchState
from lpsim.server.deck import Deck
from lpsim.server.event_handler import OmnipotentGuideEventHandler_3_3
from lpsim.agents.agent_base import AgentBase
from lpsim.server.struct import ObjectPosition
from lpsim.utils import BaseModel
from tests.default_random_state import get_default_random_state


def set_16_omni(match: Match):
    match.config.initial_dice_number = 16
    match.event_handlers.append(OmnipotentGuideEventHandler_3_3())


def make_respond(agent: AgentBase, match: Match, assertion: bool = True):
    """
    Make response once, and step the match until new request or
    game end, regardless of the target of requests.
    If not requesting this agent and needs assetion, raise AssertionError.
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
    hps = [[x.hp for x in t.characters] for t in match.player_tables]
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
    if "id" in model.__fields__.keys():
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
        state[1] = np.array(state[1], dtype="uint32")
        random_state.set_state(state)  # type: ignore
        for _ in range(offset):
            random_state.random()
        state = list(random_state.get_state(legacy=True))  # type: ignore
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
    if command.startswith("TEST"):
        agent.commands = agent.commands[1:]
        return int(command.split(" ")[1])
    return 0


def enable_logging():  # pragma: no cover
    import logging

    logging.basicConfig(level=logging.INFO)


def get_pidx_cidx(cmd):
    return int(cmd[2][1]), int(cmd[2][3])


def check_usage(data, usage_strs: List[str]):
    usage = [int(x) for x in usage_strs]
    assert len(data) == len(usage)
    for u, d in zip(usage, data):
        assert u == d.usage


def read_from_log_json(path: str) -> Tuple[Match, InteractionAgent, InteractionAgent]:
    """
    read from log json file, return Match instance and two agents.
    """
    data = json.load(open(path, "r", encoding="utf-8"))
    decks = [Deck.from_str(data["start_deck"][0]), Deck.from_str(data["start_deck"][1])]
    config = MatchConfig(**data["match_config"])
    random_state = data["match_random_state"]
    commands = data["command_history"]
    if isinstance(commands[0][0], (list, tuple)):  # pragma: no cover
        # new version, extract only string
        commands = [[y[1] for y in x] for x in commands]
    agent_0 = InteractionAgent(
        player_idx=0, verbose_level=0, commands=commands[0], only_use_command=True
    )
    agent_1 = InteractionAgent(
        player_idx=1, verbose_level=0, commands=commands[1], only_use_command=True
    )
    match = Match(random_state=random_state, config=config)
    match.set_deck(decks)
    return match, agent_0, agent_1


def do_log_tests(
    json_path,
    hp_modify: int = -1,
    omnipotent: bool = True,
    other_tests: Dict[int, Callable] = {},
    match_version: str | None = None,
):
    """
    Do tests on log data generated by HTTPServer, and modified by adding test commands
    with test template.
    """
    match, agent_0, agent_1 = read_from_log_json(json_path)
    match.config.history_level = 0
    if match_version is not None:
        match.version = match_version  # type: ignore
    # modify hp
    if hp_modify > 0:
        for i in range(2):
            characters = match.player_tables[i].player_deck_information.characters  # noqa: E501
            for c in characters:
                c.hp = c.max_hp = hp_modify
    # add omnipotent guide
    if omnipotent:
        match.event_handlers.append(OmnipotentGuideEventHandler_3_3())
    match.start()
    match.step()
    while True:
        if match.need_respond(0):
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError("No need respond.")
        # do tests
        while True:
            cmd = agent.commands[0].strip().split(" ")
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                half = len(hps) // 2
                hps = [hps[:half], hps[half:]]
                check_hp(match, hps)
            elif test_id == 2:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].summons, cmd[3:])
            elif test_id == 3:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].supports, cmd[3:])
            elif test_id == 4:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].team_status, cmd[3:])
            elif test_id == 5:
                pidx, cidx = get_pidx_cidx(cmd)
                check_usage(match.player_tables[pidx].characters[cidx].status, cmd[3:])
            elif test_id == 6:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].hands) == int(cmd[3])
            elif test_id == 7:
                pidx = int(cmd[2][1])
                d = {}
                for c in match.player_tables[pidx].dice.colors:
                    d[c.value] = d.get(c.value, 0) + 1
                for c in cmd[3:]:
                    d[c] -= 1
                    if d[c] == 0:
                        del d[c]
                assert len(d) == 0
            elif test_id == 8:
                charges = []
                for table in match.player_tables:
                    for c in table.characters:
                        charges.append(c.charge)
                assert charges == [int(x) for x in cmd[2:]]
            elif test_id == 9:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].summons) == len(cmd[3:])
                for i, s in enumerate(match.player_tables[pidx].summons):
                    assert s.damage_elemental_type.value == cmd[3 + i]
            elif test_id == 10:
                pidx, cidx = get_pidx_cidx(cmd)
                desc = match.player_tables[pidx].characters[cidx].desc
                cmd_desc = " ".join(cmd[3:])[1:-1]
                assert desc == cmd_desc
            elif test_id == 11:
                card_idxs = [int(x) for x in cmd[2:]]
                card_idxs.sort()
                current = []
                for req in match.requests:
                    if req.name == "UseCardRequest":
                        current.append(req.card_idx)
                current.sort()
                assert current == card_idxs
            elif test_id == 12:
                pidx, cidx = get_pidx_cidx(cmd)
                ele_app = match.player_tables[pidx].characters[cidx].element_application
                now_ele = [x.value for x in ele_app]
                assert now_ele == cmd[3:]
            else:
                if test_id in other_tests:
                    other_tests[test_id](match, cmd)
                else:
                    raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR
