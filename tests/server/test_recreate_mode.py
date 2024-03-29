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


def test_recreate_mode():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "reroll",
            "card 0 0",
            "card 0 0 7",
            "skill 1 6 5 4",
            "sw_char 2 3",
            "skill 1 2 1 0",
            "end",
            "reroll",
            "skill 2 7 6 5",
            "sw_char 1 4",
            "card 0 2 3 2",
            "sw_char 0 1",
            "end",
            "reroll",
            "card 0 0",
            "skill 0 8 7 6",
            "card 0 0 5 4",
            "skill 2 3 2 1 0",
            "choose 1",
            "card 0 0",
            "sw_char 2 0",
            "end",
            "choose 1",
            "reroll",
            "card 0 0",
            "skill 2 7 6 5",
            "skill 0 4 3 2",
        ],
        [
            "sw_card",
            "choose 1",
            "reroll",
            "card 3 0 7",
            "tune 3 6",
            "skill 1 6 5 4",
            "card 2 0",
            "card 1 0",
            "card 1 0",
            "card 0 0",
            "end",
            "TEST 1 10 10 10 9 8 9",
            "reroll",
            "card 3 0 10",
            "card 1 2",
            "card 0 1 9",
            "skill 1 9 8 7",
            "TEST 2 p1 summon frog squirrel",
            "sw_char 2 6",
            "skill 1 5 4 3",
            "tune 1 2",
            "card 1 2",
            "tune 0 0",
            "end",
            "TEST 1 6 9 10 8 6 5",
            "reroll",
            "card 3 2 11",
            "skill 1 11 10 9",
            "card 0 1 8",
            "sw_char 1 7",
            "choose 2",
            "card 0 0",
            "skill 2 7 6 5",
            "sw_char 0 4",
            "card 1 0 3 2",
            "skill 1 3 2 1",
            "card 0 0 0",
            "end",
            "TEST 1 0 6 0 5 0 2",
            "reroll",
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
    deck1 = Deck.from_str(
        """
        default_version:4.1
        character:Raiden Shogun
        character:Chongyun
        character:Shenhe
        Timmie
        Liu Su
        Send Off
        Vanarana
        Adeptus' Temptation
        Elemental Resonance: Woven Ice
        Fresh Wind of Freedom
        Sweet Madame*10
        """
    )
    deck2 = Deck.from_str(
        """
        default_version:4.1
        character:Nahida
        character:Rhodeia of Loch
        character:Fischl
        Vanarana
        Timmie
        Liben
        Strategize
        Calx's Arts
        Timmie
        Mushroom Pizza
        Chef Mao
        Leave It to Me!
        Dunyarzad
        Adeptus' Temptation
        Liben
        Mondstadt Hash Brown
        I Haven't Lost Yet!
        Mushroom Pizza
        Mondstadt Hash Brown
        The Bestest Travel Companion!
        Dunyarzad
        The Bestest Travel Companion!
        Send Off
        Toss-Up
        Sweet Madame*10
        """
    )
    match.set_deck([deck1, deck2])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
    # recreate mode and random object information
    match.config.recreate_mode = True
    match.config.random_object_information = [
        "Oceanic Mimic: Frog",
        "Oceanic Mimic: Squirrel",
    ]
    match.config.player_go_first = 1
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
                summons = match.player_tables[1].summons
                assert len(summons) == 2
                assert "frog" in summons[0].name.lower()
                assert "squirrel" in summons[1].name.lower()
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_recreate_mode_v43_rhodeia():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "TEST 2 p0 summon 1",
            "TEST 2 p1 summon 2 1",
            "skill 2 12 11 10 9 8",
            "TEST 2 p0 summon 1 2",
            "TEST 2 p1 summon 2 1",
            "sw_char 1 4",
            "end",
            "TEST 1 10 8 10 9 10 10",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "sw_char 2 9",
            "TEST 1 10 8 3 7 10 10",
            "end",
        ],
        [
            "sw_card",
            "choose 0",
            "TEST 2 p0 summon 1",
            "skill 2 15 14 13 12 11",
            "TEST 2 p0 summon 1 2",
            "TEST 2 p1 summon 2 1",
            "skill 1 10 9 8",
            "card 0 0 7 6 5",
            "end",
            "card 0 0 15 14 13",
            "skill 0 12 11 10",
            "sw_char 1 9",
            "card 1 1 8 7 6",
            "sw_char 0 5",
            "skill 3 4 3 2",
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
        character:Rhodeia of Loch
        character:Fischl
        character:Chongyun
        Ocean-Hued Clam*10
        Stone and Contracts*10
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.character_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
    match.config.recreate_mode = True
    match.config.random_object_information = [
        "Oceanic Mimic: Frog",
        "Oceanic Mimic: Squirrel",
        "Oceanic Mimic: Frog",
        "Oceanic Mimic: Squirrel",
        "Oceanic Mimic: Frog",
        "Oceanic Mimic: Frog",
    ]
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
                check_usage(match.player_tables[pidx].summons, cmd[4:])
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == "__main__":
    test_recreate_mode()
    test_recreate_mode_v43_rhodeia()
