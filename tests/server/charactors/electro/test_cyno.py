from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, check_usage, get_pidx_cidx, get_random_state, 
    get_test_id_from_command, make_respond, set_16_omni
)


def test_cyno():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "skill 1 15 14 13",
            "TEST 2 p0 status 1",
            "sw_char 3 12",
            "TEST 1 10 10 10 8 10 9 10 10 10 10",
            "end",
            "TEST 3 p0c0 status 1",
            "skill 1 15 14 13",
            "TEST 1 10 10 10 6 10 9 10 10 10 10",
            "skill 1 12 11 10",
            "TEST 2 p0 status",
            "skill 1 9 8 7",
            "TEST 1 10 10 10 4 10 7 10 10 10 10",
            "end",
            "skill 1 15 14 13",
            "TEST 1 10 10 10 1 10 7 10 10 10 10",
            "sw_char 4 12",
            "end",
            "TEST 1 10 10 10 1 4 7 10 10 10 10",
            "sw_char 3 15",
            "sw_char 2 14",
            "skill 1 13 12 11",
            "TEST 1 10 10 6 1 4 7 10 10 10 10",
            "sw_char 4 10",
            "TEST 1 10 10 6 1 2 7 10 10 10 10",
            "TEST 3 p1c0 usage 3 1",
            "sw_char 1 9",
            "end",
            "TEST 1 10 5 6 1 2 7 10 10 10 10",
            "skill 1 15 14 13"
        ],
        [
            "sw_card 2 1",
            "choose 0",
            "skill 0 15 14 13",
            "skill 1 12 11 10",
            "end",
            "card 3 0",
            "skill 2 15 14 13 12",
            "skill 0 11 10 9",
            "card 0 0 8 7 6",
            "end",
            "card 2 0",
            "skill 1 15 14 13",
            "end",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "sw_char 0 11",
            "card 4 0",
            "skill 2 10 9 8 7",
            "skill 0 6 5 4",
            "end",
            "skill 1 15 14 13",
            "TEST 1 10 5 6 1 2 2 10 10 10 10",
            "end"
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
        charactor:Cyno
        charactor:Cyno
        charactor:Noelle
        charactor:Noelle
        charactor:Noelle
        Featherfall Judgment*15
        Sweet Madame*15
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
                hps = [hps[:5], hps[5:]]
                check_hp(match, hps)
            elif test_id == 2:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                team_status = match.player_tables[pidx].team_status
                check_usage(team_status, cmd[4:])
            elif test_id == 3:
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
    test_cyno()
