from lpsim.agents import InteractionAgent
from lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp,
    get_random_state,
    get_test_id_from_command,
    make_respond,
    set_16_omni,
)


def test_diona():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "sw_char 0 12",
            "skill 1 11 10 9",
            "card 0 0 8 7 6 5",
            "skill 0 4 3 2",
            "end",
            "skill 2 15 14 13",
            "sw_char 1 12",
            "end",
            "TEST 1 10 8 10 8 5 10",
            "end",
        ],
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "TEST 2 p0 team 2",
            "TEST 1 10 9 10 7 8 10",
            "card 1 0",
            "card 1 0",
            "end",
            "sw_char 0 15",
            "card 0 0 14 13 12 11",
            "sw_char 1 10",
            "skill 1 9 8 7",
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
        character:Diona
        character:Mona
        character:Sucrose
        Shaken, Not Purred*30
        Sweet Madame*15
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
                status = match.player_tables[0].team_status
                assert len(status) == 1
                assert status[0].usage == 2
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == "__main__":
    test_diona()
