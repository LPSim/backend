from lpsim.agents import InteractionAgent
from lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    get_random_state,
    get_test_id_from_command,
    make_respond,
    set_16_omni,
)


def test_fishchip_gilded():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "TEST 1 p0 dice 12",
            "card 1 1 11 10 9",
            "TEST 2 p0 hand 4",
            "TEST 1 p0 dice 11",
            "skill 1 10 9 8",
            "sw_char 2 7",
            "card 2 2 6 5 4",
            "skill 0 5 4 3",
            "skill 0 2 1 0",
            "end",
            "TEST 2 p0 hand 7",
            "skill 0 15 14 13",
            "sw_char 1 12",
            "card 4 1",
            "card 4 0",
            "skill 1 11 10 9",
            "end",
        ],
        [
            "sw_card 2",
            "choose 0",
            "card 2 0",
            "card 1 0 15 14",
            "skill 1 13 12 11",
            "sw_char 1 10",
            "skill 1 9 8",
            "sw_char 0 7",
            "TEST 2 p0 hand 4",
            "skill 0 6 5 4",
            "TEST 2 p0 hand 5",
            "sw_char 2 3",
            "skill 0 2 1",
            "end",
            "TEST 2 p0 hand 8",
            "sw_char 1 15",
            "card 2 2 14 13 12",
            "TEST 1 p1 dice 13",
            "TEST 3 p1 omni*12 dendro*1",
            "end",
            "TEST 2 p0 hand 9",
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
    deck_str_1 = """
        default_version:4.3
        character:Fischl
        character:Mona
        character:Nahida
        Fish and Chips*10
        Sweet Madame*10
        Gilded Dreams*10
    """
    deck_str_2 = """
        default_version:4.3
        character:Barbara
        character:Mona
        character:Nahida
        Fish and Chips*10
        Sweet Madame*10
        Gilded Dreams*10
    """
    match.set_deck([Deck.from_str(deck_str_1), Deck.from_str(deck_str_2)])
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
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].dice.colors) == int(cmd[4])
            elif test_id == 2:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].hands) == int(cmd[4])
            elif test_id == 3:
                pidx = int(cmd[2][1])
                colors = {}
                for c in cmd[3:]:
                    c, n = c.strip().split("*")
                    colors[c] = int(n)
                for c in match.player_tables[pidx].dice.colors:
                    c = c.value.lower()
                    assert c in colors
                    colors[c] -= 1
                    if colors[c] == 0:
                        del colors[c]
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == "__main__":
    test_fishchip_gilded()
