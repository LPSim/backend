# tests that test corner cases to improve coverage

from lpsim.agents import InteractionAgent
from lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp,
    check_usage,
    get_random_state,
    get_test_id_from_command,
    make_respond,
    set_16_omni,
)


def test_lynette_single():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 2 0 15 14 13",
            "skill 1 12 11 10",
            "TEST 1",
            "end",
        ],
        ["sw_card", "choose 0", "skill 1 15 14 13", "skill 1 12 11 10"],
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
        character:Lynette
        A Cold Blade Like a Shadow*15
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
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
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                assert match.player_tables[0].characters[0].hp == 4
                assert match.player_tables[1].characters[0].hp == 4
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_gorou_alhaitham_layla():
    cmd_records = [
        [
            "sw_card 1 2",
            "choose 2",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "card 3 0",
            "skill 2 9 8 7",
            "end",
            "choose 1",
            "end",
            "choose 0",
            "end",
            "end",
        ],
        [
            "sw_card 2 3",
            "choose 1",
            "card 1 0 15 14 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7",
            "sw_char 0 6",
            "skill 0 5 4 3",
            "skill 0 2 1 0",
            "end",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7",
            "end",
            "end",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "skill 1 11 10 9",
            "TEST 1",
            "TEST 2",
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
        character:Layla
        character:Gorou
        character:Alhaitham
        Rushing Hound: Swift as the Wind*10
        Sweet Madame*10
        Changing Shifts*10
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
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
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                for s in match.player_tables[1].team_status:
                    assert s.usage == 2
            elif test_id == 2:
                check_hp(match, [[5, 0, 0], [10, 2, 10]])
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_dvalin_2():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "sw_char 0 12",
            "skill 1 11 10 9",
            "TEST 1 10 10 10 6 10 10",
            "skill 0 8 7 6",
            "TEST 1 10 10 10 2 10 10",
            "sw_char 1 5",
            "skill 0 4 3 2",
            "end",
            "skill 5 15 14 13 12",
            "card 3 0 11 10 9",
            "end",
            "skill 1 15 14 13",
            "TEST 1 10 4 10 0 1 6",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "TEST 1 10 4 10 0 0 2",
            "end",
        ],
        [
            "sw_card",
            "choose 0",
            "end",
            "choose 1",
            "card 1 0 15 14 13",
            "sw_char 2 12",
            "sw_char 1 11",
            "skill 1 10 9 8",
            "end",
            "end",
            "choose 2",
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
        character:Gorou
        character:Dvalin
        character:Alhaitham
        Rending Vortex*10
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
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
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_eremite_2():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 15 14 13",
            "end",
            "sw_char 1 15",
            "skill 0 14 13 12",
            "skill 0 11 10 9",
            "skill 0 8 7 6",
            "sw_char 0 5",
            "end",
            "choose 1",
            "end",
            "TEST 2 p0c0 charge 0",
            "sw_char 2 15",
            "end",
            "end",
            "TEST 1 0 2 0 10 4 9",
            "choose 1",
        ],
        [
            "sw_card",
            "choose 2",
            "skill 0 15 14 13",
            "sw_char 1 12",
            "end",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "end",
            "skill 2 15 14 13",
            "sw_char 0 12",
            "skill 0 11 10 9",
            "skill 0 8 7 6",
            "end",
            "card 7 0 15 14 13",
            "sw_char 2 12",
            "skill 0 11 10 9",
            "TEST 3 p1 summon damage 1",
            "sw_char 0 8",
            "skill 0 7 6 5",
            "skill 0 4 3 2",
            "end",
            "skill 2 15 14 13",
            "TEST 3 p1 summon damage 1",
            "TEST 1 0 2 1 10 4 9",
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
        character:Eremite Scorching Loremaster
        character:Chongyun
        character:Klee
        Scorpocalypse*10
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
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
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                assert match.player_tables[0].characters[0].charge == 0
            elif test_id == 3:
                assert match.player_tables[1].summons[0].damage == 1
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_signora_2():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 15 14 13",
            "skill 2 12 11 10",
            "TEST 2 p1c0 usage 1 1",
            "skill 4 9 8 7",
            "TEST 2 p1c0 usage 1 1",
            "skill 3 6 5 4",
            "TEST 2 p1c0 usage 1",
            "end",
        ],
        ["sw_card", "choose 0", "end"],
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
        character:Signora
        character:Chongyun
        character:Klee
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
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
                status = match.player_tables[1].characters[0].status
                check_usage(status, cmd[4:])
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_thunder_2():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 1 0",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "skill 0 11 10 9",
            "TEST 1 10 6 10 10 7 7",
            "TEST 2 p0 hand 5",
            "end",
        ],
        [
            "sw_card",
            "choose 1",
            "TEST 1 10 10 10 10 7 10",
            "sw_char 2 15",
            "skill 0 14 13 12",
            "skill 1 11 10 9",
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
        character:Thunder Manifestation
        character:Raiden Shogun
        character:Lyney
        Grieving Echo*10
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
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
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                assert len(match.player_tables[0].hands) == 5
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_jade_razor():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 1 0 15 14 13",
            "skill 0 12 11 10",
            "card 1 0",
            "card 1 0 9",
            "skill 0 8 7 6",
            "TEST 1 10 10 10 10 4 10",
            "skill 0 5 4 3",
        ],
        ["sw_card", "choose 1", "TEST 1 10 10 10 10 7 10", "end", "choose 0"],
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
        character:Shenhe
        character:Raiden Shogun
        character:Lyney
        Primordial Jade Winged-Spear*10
        Where Is the Unseen Razor?*10
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
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
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == "__main__":
    # test_lynette_single()
    test_gorou_alhaitham_layla()
    # test_dvalin_2()
    # test_eremite_2()
    # test_signora_2()
    # test_thunder_2()
