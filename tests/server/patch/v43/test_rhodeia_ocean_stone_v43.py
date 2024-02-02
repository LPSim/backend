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


def test_rhodeia_ocean_stone_v43():
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
            "card 2 0 7 6 5",
            "sw_char 1 4",
            "TEST 3 p0 hand 4",
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
            "TEST 3 p0 hand 7",
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
            elif test_id == 3:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].hands) == int(cmd[4])
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == "__main__":
    test_rhodeia_ocean_stone_v43()
