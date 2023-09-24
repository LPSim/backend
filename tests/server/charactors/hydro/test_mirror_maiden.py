from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, check_usage, get_pidx_cidx, get_random_state, 
    get_test_id_from_command, make_respond, set_16_omni
)


def test_mirror_maiden():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "TEST 1 7 10 10 10 8 10",
            "skill 0 12 11 10",
            "TEST 1 5 10 10 10 6 10",
            "sw_char 1 9",
            "skill 1 8 7 6",
            "card 1 0 5 4 3 2",
            "end",
            "sw_char 2 15",
            "sw_char 0 14",
            "sw_char 2 13",
            "sw_char 1 12",
            "sw_char 2 11",
            "skill 1 10 9 8",
            "end",
            "card 1 1",
            "sw_char 1 15",
            "skill 0 14 13 12",
            "skill 1 11 10 9",
            "end",
            "card 3 1",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "TEST 1 5 5 9 3 3 0",
            "end"
        ],
        [
            "sw_card 1 2",
            "choose 1",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "sw_char 2 9",
            "TEST 2 p0c0 usage 2",
            "TEST 2 p1c2 usage 2",
            "TEST 2 p1c1 usage",
            "skill 1 8 7 6",
            "TEST 1 5 9 10 10 6 4",
            "TEST 2 p1c2 usage 3",
            "sw_char 1 5 4",
            "sw_char 2 3",
            "sw_char 0 2",
            "sw_char 2 1",
            "end",
            "sw_char 0 15 14",
            "card 2 1",
            "TEST 1 5 8 10 10 6 5",
            "TEST 2 p1c2 usage 2 1",
            "sw_char 2 13",
            "sw_char 1 12",
            "sw_char 2 11",
            "skill 1 10 9 8",
            "end",
            "TEST 1 5 8 9 10 6 2",
            "end",
            "choose 1",
            "sw_char 0 15 14",
            "skill 1 13 12 11",
            "skill 1 10 9 8"
        ]
    ]
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = cmd_records[0],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = cmd_records[1],
        only_use_command = True
    )
    # initialize match. It is recommended to use default random state to make
    # replay unchanged.
    match = Match(random_state = get_random_state())
    # deck information
    deck = Deck.from_str(
        '''
        default_version:4.0
        charactor:Mirror Maiden
        charactor:Mirror Maiden@3.3
        charactor:Mona
        Sweet Madame*15
        Mirror Cage*15
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
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
            raise AssertionError('No need respond.')
        # do tests
        while True:
            cmd = agent.commands[0]
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                # a sample of HP check based on the command string.
                hps = cmd.strip().split(' ')[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                cmd = cmd.split()
                pidx, cidx = get_pidx_cidx(cmd)
                status = match.player_tables[pidx].charactors[cidx].status
                check_usage(status, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_mirror_maiden()
