from lpsim.agents.interaction_agent import InteractionAgent
from lpsim.server.match import Match, MatchState
from lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp,
    get_random_state,
    get_test_id_from_command,
    make_respond,
    set_16_omni,
)


def test_yoimiya_3_3():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 0",
            "skill 0 0 1 2",
            "skill 1 0",
            "card 0 0 0 1",
            "skill 1 0",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "end",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "TEST 1 8 10 10 3 6 7",
            "TEST 2 p1 all pyro app",
            "skill 2 0 1 2",
            "TEST 1 8 10 10 0 6 7",
            "skill 0 0 1 2",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "TEST 1 8 10 10 0 6 2",
            "TEST 3 p0 status usage 2",
            "end",
            "skill 1 0 1 2",
        ],
        [
            "sw_card",
            "choose 2",
            "sw_char 1 0",
            "sw_char 2 0",
            "TEST 1 10 10 10 10 10 7",
            "sw_char 1 0",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "sw_char 1 0",
            "TEST 1 8 10 10 10 6 7",
            "sw_char 0 0",
            "end",
            "end",
            "choose 2",
            "skill 1 0 1 2",
            "choose 1",
            "TEST 1 8 9 10 0 5 0",
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
        default_version:4.0
        character:Yoimiya@3.3
        character:Nahida@3.7
        character:Mona@3.3
        Naganohara Meteor Swarm*30
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
            cmd = agent.commands[0]
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                # a sample of HP check based on the command string.
                hps = cmd.strip().split(" ")[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                for character in match.player_tables[1].characters:
                    assert character.element_application == ["PYRO"]
            elif test_id == 3:
                assert len(match.player_tables[0].team_status) == 1
                assert match.player_tables[0].team_status[0].usage == 2
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_yoimiya_different_version_generate():
    cmd_records = [["TEST 1 3.3 3.4 3.8 Yoimiya", "sw_card"], ["sw_card"]]
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
        default_version:4.0
        character:Yoimiya@3.3
        character:Yoimiya@3.4
        character:Yoimiya
        Send Off@3.3*15
        Send Off*15
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
                characters = match.player_tables[0].characters
                assert characters[0].version == "3.3"
                assert characters[1].version == "3.4"
                assert characters[2].version == "3.8"
                assert characters[0].skills[2].cost.charge == 2
                assert characters[1].skills[2].cost.charge == 3
                assert characters[2].skills[2].cost.charge == 3
                assert characters[0].skills[2].cost.elemental_dice_number == 3
                assert characters[1].skills[2].cost.elemental_dice_number == 4
                assert characters[2].skills[2].cost.elemental_dice_number == 3
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == "__main__":
    test_yoimiya_3_3()
    test_yoimiya_different_version_generate()
