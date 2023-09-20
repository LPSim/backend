from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, check_usage, get_random_state, get_test_id_from_command, 
    make_respond, set_16_omni
)


def test_zhongli():
    cmd_records = [
        [
            "sw_card 1 2 4",
            "choose 1",
            "card 1 0 15 14 13 12 11",
            "sw_char 2 10",
            "skill 1 9 8 7",
            "end",
            "skill 1 15 14 13",
            "sw_char 3 12",
            "skill 1 11 10 9",
            "sw_char 2 8",
            "skill 1 7 6 5",
            "TEST 1 10 10 10 9 7 10 8 8",
            "end",
            "TEST 1 10 10 10 9 7 10 8 6",
            "card 0 2 15 14 13",
            "skill 1 12 11 10",
            "end",
            "TEST 2 p1 team 1 1 2",
            "TEST 1 10 10 7 9 7 10 8 5",
            "skill 1 15 14 13",
            "end",
            "TEST 2 p1 usage 1",
            "card 1 0 15 14 13",
            "sw_char 1 12",
            "skill 2 11 10 9 8 7",
            "skill 0 6 5 4",
            "TEST 1 10 10 7 9 7 6 5 5",
            "skill 3 3 2 1",
            "end",
            "TEST 3 no skill can use",
            "sw_char 0 15",
            "skill 1 14 13 12",
            "sw_char 2 11",
            "end",
            "card 6 1 15 14 13",
            "end",
            "sw_char 1 15",
            "skill 1 15 14 13",
            "sw_char 0 12",
            "skill 1 11 10 9",
            "sw_char 1 8",
            "end",
            "TEST 1 7 5 7 9 1 3 2 3",
            "end"
        ],
        [
            "sw_card 1 2",
            "choose 0",
            "sw_char 2 15",
            "skill 1 14 13 12",
            "end",
            "TEST 1 10 10 10 10 7 10 8 10",
            "sw_char 3 15",
            "skill 1 14 13 12",
            "skill 1 11 10 9",
            "sw_char 2 8",
            "sw_char 3 7",
            "skill 1 6 5 4",
            "end",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "skill 2 11 10 9 8 7",
            "end",
            "skill 1 15 14 13",
            "end",
            "sw_char 2 15",
            "TEST 1 10 10 7 9 7 10 5 5",
            "TEST 2 p0 usage 3",
            "sw_char 1 14",
            "skill 2 13 12 11 10 9",
            "TEST 3 no skill can use",
            "card 7 1",
            "TEST 1 10 10 7 9 7 4 5 5",
            "end",
            "skill 3 15 14 13",
            "skill 2 12 11 10 9 8",
            "sw_char 3 7",
            "end",
            "TEST 1 7 5 7 9 7 3 5 3",
            "sw_char 0 15",
            "end",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "sw_char 0 11",
            "sw_char 1 10",
            "sw_char 0 9",
            "sw_char 2 8",
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
        charactor:Fischl
        charactor:Zhongli
        charactor:Arataki Itto
        charactor:Ganyu
        Dominance of Earth*10
        Sweet Madame*10
        Vortex Vanquisher*10
        Tenacity of the Millelith*10
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
                hps = [hps[:4], hps[4:]]
                check_hp(match, hps)
            elif test_id == 2:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                team_status = match.player_tables[pidx].team_status
                check_usage(team_status, cmd[4:])
            elif test_id == 3:
                for req in match.requests:
                    assert req.name != 'UseSkillRequest'
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_zhongli()
