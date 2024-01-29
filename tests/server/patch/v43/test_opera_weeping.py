from lpsim.agents import InteractionAgent
from lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_usage,
    get_random_state,
    get_test_id_from_command,
    make_respond,
    set_16_omni,
)


def test_opera_weeping():
    cmd_records = [
        [
            "sw_card",
            "choose 3",
            "card 0 0 15",
            "TEST 1 p0 dice 16",
            "card 2 4 15 14 13",
            "TEST 1 p0 dice 13",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "skill 2 6 5 4",
            "TEST 1 p1 dice 6",
            "end",
            "TEST 2 p1 hand 6",
            "TEST 3 p1 support 2 1 1 2",
            "TEST 3 p0 support 1",
            "sw_char 2 15",
            "card 2 5 14 13 12",
            "card 2 1 1 11 10",
            "card 2 0 1",
            "card 1 0 1",
            "end",
            "sw_char 0 15",
            "card 4 0 14",
            "card 2 0 14",
            "card 2 4 13 12 11",
            "end",
            "TEST 3 p0 support 1 2",
            "end",
        ],
        [
            "sw_card",
            "choose 4",
            "card 0 0 15",
            "TEST 1 p1 dice 15",
            "skill 0 14 13 12",
            "skill 0 11 10 9",
            "card 2 0 8 7 6",
            "TEST 1 p1 dice 7",
            "card 0 0 6",
            "card 0 0 5",
            "card 0 0 4",
            "end",
            "TEST 3 p1 support 1 1 1 2",
            "sw_char 3 15",
            "end",
            "TEST 3 p0 support 1 1",
            "card 2 2 15 14 13",
            "TEST 1 p1 dice 13",
            "card 4 5 12 11 10",
            "TEST 1 p1 dice 11",
            "TEST 3 p1 support 1 1 2",
            "end",
            "TEST 2 p0 hand 6",
            "TEST 3 p0 support 1 2 2",
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
        character:Eula@3.8*6
        Wellspring of War-Lust@3.5*3
        Sacrificial Greatsword@3.3*5
        Weeping Willow of the Lake@4.3*5
        Opera Epiclese@4.3*5
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
    match.config.initial_dice_number = 16
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
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].dice.colors) == int(cmd[4])
            elif test_id == 2:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].hands) == int(cmd[4])
            elif test_id == 3:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].supports, cmd[4:])
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == "__main__":
    test_opera_weeping()
