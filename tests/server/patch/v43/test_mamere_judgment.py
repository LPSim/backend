import json
from typing import Dict
from lpsim.agents import InteractionAgent
from lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp,
    check_usage,
    get_random_state,
    get_test_id_from_command,
    make_respond,
    remove_ids,
    set_16_omni,
)


def get_mamere_judgment_match():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "card 2 0",
            "card 3 0",
            "TEST 2 p0 hand 3",
            "card 1 0",
            "TEST 2 p0 hand 4",
            "card 2 0 15 14",
            "TEST 2 p0 hand 3",
            "skill 0 13 12 11",
            "end",
            "card 3 0",
            "card 2 3 15",
            "TEST 2 p0 hand 8",
            "end",
            "card 7 0",
            "card 8 0",
            "end",
            "card 11 0",
            "card 11 2",
            "card 11 1",
            "card 6 0",
            "card 0 0 15",
            "skill 1 14 13 12",
            "end",
            "sw_char 1 15",
            "sw_char 0 14",
            "card 0 1 13 12",
            "TEST 3 p0 support 1 1 2 2",
            "TEST 2 p0 hand 16",
            "TEST 5 p0 team 3",
            "card 1 0",
            "TEST 5 p0 team 2",
            "card 1 0 11",
            "TEST 5 p0 team 1",
            "card 2 0 10",
            "TEST 5 p0 team",
            "TEST 4 p0 dice 10",
            "card 0 0",
            "TEST 1 10 8 7 9 8 10",
            "end",
        ],
        [
            "sw_card",
            "choose 0",
            "card 4 0",
            "card 1 0 15",
            "TEST 2 p1 hand 5",
            "card 2 0",
            "TEST 2 p1 hand 5",
            "card 3 0",
            "card 1 0",
            "TEST 2 p1 hand 4",
            "end",
            "card 3 0 15",
            "end",
            "card 1 0",
            "card 8 0",
            "card 7 0",
            "end",
            "card 12 0",
            "card 12 0",
            "card 12 1",
            "sw_char 1 15",
            "card 5 1",
            "card 4 1",
            "TEST 1 10 10 10 9 8 10",
            "end",
            "card 0 0 15",
            "skill 1 14 13 12",
            "skill 1 11 10 9",
            "card 2 0 8",
            "TEST 2 p1 hand 17",
            "sw_char 0 7",
        ],
    ]
    agent_0 = InteractionAgent(
        player_idx=0, verbose_level=0, commands=cmd_records[0], only_use_command=True
    )
    agent_1 = InteractionAgent(
        player_idx=1, verbose_level=0, commands=cmd_records[1], only_use_command=True
    )
    # initialize match. It is recommended to use default random state to make
    # replay unchanged.
    match = Match(random_state=get_random_state())
    # deck information
    deck = Deck.from_str(
        """
        default_version:4.3
        character:Baizhu
        character:Nilou
        character:Tighnari
        Mamere*10
        Strategize*3
        Sweet Madame*3
        Liben*3
        Wangshu Inn*3
        Passing of Judgment*1
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    match.config.max_hand_size = 999
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
    # check whether in rich mode (16 omni each round)
    set_16_omni(match)
    return agent_0, agent_1, match


def test_mamere_judgment():
    """
    Mamare: 3 usage, Judgment: 3 usage
    Judgment can judge arcane, food, and event card.
    """
    agent_0, agent_1, match = get_mamere_judgment_match()
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
                # a sample of HP check based on the command string.
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                pidx = int(cmd[2][1])
                assert int(cmd[-1]) == len(match.player_tables[pidx].hands)
            elif test_id == 3:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].supports, cmd[4:])
            elif test_id == 4:
                assert len(match.player_tables[0].dice.colors) == 10
            elif test_id == 5:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].team_status, cmd[4:])
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_judgment_one_round():
    cmd_records = [
        ["sw_card", "choose 0", "card 0 0 0", "end", "TEST 3 p1 usage", "end"],
        [
            "sw_card",
            "choose 1",
            "TEST 3 p1 usage 3",
            "end",
            "card 1 0 15",
            "TEST 2 p1 hand 8",
            "end",
        ],
    ]
    agent_0 = InteractionAgent(
        player_idx=0, verbose_level=0, commands=cmd_records[0], only_use_command=True
    )
    agent_1 = InteractionAgent(
        player_idx=1, verbose_level=0, commands=cmd_records[1], only_use_command=True
    )
    # initialize match. It is recommended to use default random state to make
    # replay unchanged.
    match = Match(random_state=get_random_state())
    # deck information
    deck = Deck.from_str(
        """
        default_version:4.3
        character:Baizhu
        character:Nilou
        character:Tighnari
        Mamere*10
        Strategize*3
        Sweet Madame*3
        Liben*3
        Wangshu Inn*3
        Passing of Judgment*1
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    match.config.max_hand_size = 999
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
    # check whether in rich mode (16 omni each round)
    set_16_omni(match)
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
            elif test_id == 2:
                pidx = int(cmd[2][1])
                assert int(cmd[-1]) == len(match.player_tables[pidx].hands)
            elif test_id == 3:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].team_status, cmd[4:])
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_judge_arcane():
    cmd_records = [
        ["sw_card", "choose 0", "card 0 0 0", "end", "end", "TEST 3 p1 usage", "end"],
        [
            "sw_card",
            "choose 1",
            "card 0 0 15",
            "TEST 3 p1 usage 2",
            "TEST 3 p0 usage",
            "end",
            "end",
        ],
    ]
    agent_0 = InteractionAgent(
        player_idx=0, verbose_level=0, commands=cmd_records[0], only_use_command=True
    )
    agent_1 = InteractionAgent(
        player_idx=1, verbose_level=0, commands=cmd_records[1], only_use_command=True
    )
    # initialize match. It is recommended to use default random state to make
    # replay unchanged.
    match = Match(random_state=get_random_state())
    # deck information
    deck = Deck.from_str(
        """
        default_version:4.3
        character:Baizhu
        character:Nilou
        character:Tighnari
        Mamere*10
        Strategize*3
        Sweet Madame*3
        Liben*3
        Wangshu Inn*3
        Passing of Judgment*1
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    match.config.max_hand_size = 999
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
    # check whether in rich mode (16 omni each round)
    set_16_omni(match)
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
            elif test_id == 3:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].team_status, cmd[4:])
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_mamere_no_default():
    """
    When mamere generate card, then success. No need to check or use the card,
    as we don't know the newest version of cards.
    """
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "card 2 0",
            "card 3 0",
            "TEST 2 p0 hand 3",
            "card 1 0",
            "TEST 2 p0 hand 4",
            "end",
        ],
        [
            "sw_card",
            "choose 0",
            "end",
        ],
    ]
    agent_0 = InteractionAgent(
        player_idx=0, verbose_level=0, commands=cmd_records[0], only_use_command=True
    )
    agent_1 = InteractionAgent(
        player_idx=1, verbose_level=0, commands=cmd_records[1], only_use_command=True
    )
    # initialize match. It is recommended to use default random state to make
    # replay unchanged.
    match = Match(random_state=get_random_state())
    # deck information
    deck = Deck.from_str(
        """
        character:Baizhu
        character:Nilou
        character:Tighnari
        Mamere*10
        Strategize*3
        Sweet Madame*3
        Liben*3
        Wangshu Inn*3
        Passing of Judgment*1
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    match.config.max_hand_size = 999
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
    # check whether in rich mode (16 omni each round)
    set_16_omni(match)
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
            elif test_id == 2:
                pidx = int(cmd[2][1])
                assert int(cmd[-1]) == len(match.player_tables[pidx].hands)
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_mamere_judgment_2():
    """
    When food card is disabled by judgment, it still can call mamere to draw
    card.
    """
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "card 0 0 15",
            "card 1 0",
            "card 2 0",
            "skill 1 14 13 12",
            "card 0 0",
            "TEST 1 10 8 10 10 7 10",
            "TEST 2 p0 hand 3",
            "TEST 2 p1 hand 0",
            "end",
        ],
        [
            "sw_card",
            "choose 1",
            "card 0 0 15",
            "card 1 0",
            "card 2 0",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "card 0 0 14",
            "skill 1 13 12 11",
        ],
    ]
    agent_0 = InteractionAgent(
        player_idx=0, verbose_level=0, commands=cmd_records[0], only_use_command=True
    )
    agent_1 = InteractionAgent(
        player_idx=1, verbose_level=0, commands=cmd_records[1], only_use_command=True
    )
    # initialize match. It is recommended to use default random state to make
    # replay unchanged.
    match = Match(random_state=get_random_state())
    # deck information
    deck = Deck.from_str(
        """
        default_version:4.3
        character:Kaedehara Kazuha
        character:Klee
        character:Kaeya
        Passing of Judgment
        Mamere*10
        Sweet Madame*10
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    match.config.max_hand_size = 999
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
    # check whether in rich mode (16 omni each round)
    set_16_omni(match)
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
                # a sample of HP check based on the command string.
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                pidx = int(cmd[2][1])
                assert int(cmd[-1]) == len(match.player_tables[pidx].hands)
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def remove_ellin_information(match_dict: Dict):
    # remove Ellin information
    h = match_dict
    eh = h["event_handlers"]
    if len(eh) < 3:
        return json.dumps(match_dict)
    ellin_handler = h["event_handlers"][2]
    assert ellin_handler["name"] == "Ellin"
    ellin_handler["recorded_skill_ids"] = {}
    return json.dumps(h)


def test_mamere_load_and_save():
    agent_0, agent_1, match = get_mamere_judgment_match()
    assert match.start()[0]
    match.step()
    histories = [remove_ellin_information(match.dict())]
    while True:
        if match.need_respond(0):
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError("No need respond.")
        while agent.commands[0].startswith("TEST"):
            agent.commands = agent.commands[1:]
        # respond
        make_respond(agent, match)
        histories.append(remove_ellin_information(match.dict()))
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break
    agent_0, agent_1, match = get_mamere_judgment_match()
    assert match.start()[0]
    match.step()
    for idx, old_match_json in enumerate(histories):  # pragma: no branch
        match_copy = match.copy(deep=True)
        assert remove_ids(match_copy) == remove_ids(
            Match(**json.loads(match_copy.json()))
        )
        assert remove_ids(
            Match(**json.loads(remove_ellin_information(match_copy.dict())))
        ) == remove_ids(Match(**json.loads(old_match_json)))
        match = Match(**json.loads(match.json()))
        if match.need_respond(0):
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError("No need respond.")
        while agent.commands[0].startswith("TEST"):
            agent.commands = agent.commands[1:]
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break
    assert match.state != MatchState.ERROR


if __name__ == "__main__":
    # test_mamere_judgment()
    # test_judgment_one_round()
    # test_judge_arcane()
    # test_mamere_no_default()
    # test_mamere_judgment_2()
    test_mamere_load_and_save()
