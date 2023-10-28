from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, check_usage, get_random_state, get_test_id_from_command, 
    make_respond, set_16_omni
)


def test_dehya():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 15 14 13",
            "TEST 1 10 10 10 10 10 9",
            "skill 0 12 11 10",
            "TEST 1 9 10 10 10 10 8",
            "sw_char 1 9",
            "sw_char 0 8",
            "skill 0 7 6 5",
            "skill 0 4 3 2",
            "TEST 1 9 10 10 10 9 7",
            "end",
            "skill 2 15 14 13",
            "sw_char 1 12",
            "skill 0 11 10 9",
            "sw_char 0 8",
            "end",
            "TEST 1 7 10 10 10 2 7",
            "skill 0 15 14 13",
            "sw_char 1 12",
            "TEST 1 7 9 10 9 2 6",
            "TEST 2 p1 summon 3",
            "sw_char 2 11",
            "sw_char 1 10",
            "skill 1 9 8 7",
            "TEST 1 7 4 10 9 2 5",
            "sw_char 2 6",
            "skill 1 5 4 3",
            "sw_char 0 2",
            "TEST 1 6 4 9 9 2 5",
            "end",
            "sw_char 1 15",
            "sw_char 0 14",
            "skill 0 13 12 11",
            "card 8 0",
            "skill 0 10 9 8",
            "skill 2 7 6 5",
            "TEST 1 6 4 9 2 2 1",
            "end",
            "sw_char 2 15",
            "skill 0 14 13 12",
            "sw_char 1 11",
            "skill 0 10 9 8",
            "end",
            "card 8 1",
            "skill 0 15 14 13",
            "sw_char 2 12",
            "card 3 0 11 10 9 8",
            "TEST 1 6 2 6 2 1 0",
            "sw_char 0 7",
            "card 2 0",
            "end",
            "sw_char 2 15",
            "card 7 2",
            "sw_char 0 14",
            "end",
            "sw_char 2 15",
            "sw_char 0 14",
            "TEST 1 7 2 7 2 1 0",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "skill 1 15 14 13",
            "TEST 1 10 10 10 10 10 8",
            "skill 1 12 11 10",
            "sw_char 1 9",
            "TEST 1 9 10 10 10 10 7",
            "end",
            "sw_char 0 15",
            "sw_char 1 14",
            "TEST 1 8 10 10 10 3 6",
            "end",
            "card 6 1",
            "sw_char 0 15",
            "sw_char 1 14",
            "TEST 1 7 10 10 9 2 6",
            "sw_char 2 13",
            "skill 1 12 11 10",
            "skill 2 9 8 7 6",
            "sw_char 0 5",
            "TEST 1 7 4 10 9 2 5",
            "sw_char 2 4",
            "skill 0 3 2 1",
            "end",
            "card 6 2",
            "sw_char 0 15",
            "card 2 1",
            "card 3 0",
            "end",
            "sw_char 2 15",
            "skill 1 14 13 12",
            "choose 0",
            "card 0 0",
            "card 3 0",
            "sw_char 1 11",
            "skill 0 10 9 8",
            "TEST 1 6 2 6 2 2 0",
            "sw_char 0 7",
            "end",
            "card 7 0",
            "sw_char 1 15",
            "TEST 1 6 2 6 2 1 0",
            "sw_char 0 14",
            "end",
            "TEST 1 7 2 8 1 1 0",
            "card 9 0",
            "sw_char 1 15",
            "skill 0 14 13 12",
            "sw_char 0 11",
            "end",
            "TEST 1 7 2 8 1 1 0",
            "sw_char 1 15",
            "skill 0 14 13 12",
            "sw_char 0 11",
            "card 9 0",
            "end",
            "TEST 1 7 2 7 1 1 0",
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
        default_version:4.1
        charactor:Wanderer
        charactor:Mona
        charactor:Dehya
        # Gales of Reverie*10
        # Beneficent*10
        Stalwart and True*10
        Sweet Madame*10
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
            cmd = agent.commands[0].strip().split(' ')
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
                summon = match.player_tables[pidx].summons
                check_usage(summon, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_dehya_2():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "sw_char 2 12",
            "skill 1 11 10 9",
            "skill 1 8 7 6",
            "sw_char 0 5",
            "TEST 2 p1 team usage",
            "skill 1 4 3 2",
            "end",
            "skill 1 15 14 13",
            "end",
            "skill 1 15 14 13",
            "end",
            "sw_char 2 15",
            "skill 1 14 13 12",
            "sw_char 1 11",
            "sw_char 0 10",
            "skill 1 9 8 7",
            "sw_char 2 6",
            "skill 0 5 4 3",
            "sw_char 0 2",
            "TEST 1 10 10 9 10 3 4",
            "TEST 2 p0 team usage 2",
            "sw_char 2 1",
            "TEST 1 10 10 8 10 3 4",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "sw_char 0 11",
            "sw_char 1 10",
            "TEST 1 10 10 10 10 10 8",
            "sw_char 2 9",
            "skill 1 8 7 6",
            "sw_char 1 5",
            "end",
            "end",
            "end",
            "TEST 2 p0 team usage 1 2",
            "sw_char 2 15",
            "sw_char 1 14",
            "sw_char 2 13",
            "sw_char 1 12",
            "skill 0 11 10 9",
            "sw_char 0 8",
            "sw_char 2 7",
            "skill 1 6 5 4",
            "skill 2 3 2 1 0"
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
        default_version:4.1
        charactor:Noelle
        charactor:Mona
        charactor:Dehya
        # Gales of Reverie*10
        # Beneficent*10
        Stalwart and True*10
        Sweet Madame*10
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
            cmd = agent.commands[0].strip().split(' ')
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
                status = match.player_tables[pidx].team_status
                check_usage(status, cmd[5:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    # test_dehya()
    test_dehya_2()
