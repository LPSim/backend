from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, check_usage, get_random_state, get_test_id_from_command, 
    make_respond, set_16_omni
)


def test_nilou_e_element():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "TEST 1 p1 team usage 0",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "TEST 1 p0 team usage",
            "card 1 0 15 14 13"
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
    deck1 = Deck.from_str(
        '''
        default_version:4.2
        charactor:Xingqiu
        charactor:Nilou
        charactor:Dori
        The Starry Skies Their Flowers Rain*30
        '''
    )
    deck2 = Deck.from_str(
        '''
        default_version:4.2
        charactor:Xingqiu
        charactor:Nilou
        charactor:Mona
        The Starry Skies Their Flowers Rain*30
        '''
    )
    match.set_deck([deck1, deck2])
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
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].team_status, cmd[5:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_nilou_2():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "sw_char 2 12",
            "skill 1 11 10 9",
            "sw_char 1 8",
            "TEST 2 p1 team 0",
            "sw_char 0 7",
            "skill 1 6 5 4",
            "TEST 2 p1 team 0",
            "TEST 3 p1 summon 2",
            "TEST 3 p0 summon 1",
            "sw_char 2 3",
            "skill 1 2 1 0",
            "end",
            "skill 0 15 14 13",
            "skill 1 12 11 10",
            "TEST 3 p0 summon 1 1",
            "TEST 3 p1 summon 1",
            "sw_char 1 9",
            "card 2 0 8 7 6",
            "card 2 1 5",
            "skill 2 4 3 2",
            "TEST 1 38 34 32 38 35 23",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "TEST 3 p0 summon 1",
            "TEST 2 p0 team 0",
            "sw_char 1 9",
            "skill 1 8 7 6",
            "sw_char 2 5",
            "skill 1 4 3 2",
            "end",
            "TEST 1 38 34 34 40 40 25",
            "sw_char 1 15",
            "sw_char 0 14",
            "skill 1 13 12 11",
            "sw_char 1 10",
            "sw_char 2 9",
            "TEST 3 p0 summon 1 3",
            "end",
            "TEST 1 38 32 32 38 35 12",
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
        default_version:4.2
        charactor:Xingqiu
        charactor:Nilou
        charactor:Tighnari
        The Starry Skies Their Flowers Rain*15
        Quick Knit*15
        '''
    )
    for charactor in deck.charactors:
        charactor.hp = 40
        charactor.max_hp = 40
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
                check_usage(match.player_tables[pidx].team_status, cmd[4:])
            elif test_id == 3:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].summons, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_nilou_3():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 3 0 15 14 13",
            "sw_char 1 12",
            "skill 1 11 10 9",
            "skill 0 8 7 6",
            "skill 2 5 4 3 2",
            "end",
            "sw_char 2 15",
            "skill 0 14 13 12",
            "skill 0 11 10 9",
            "skill 1 8 7 6",
            "skill 2 5 4 3",
            "end",
            "sw_char 0 15",
            "skill 0 14 13 12",
            "skill 2 11 10 9"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "sw_char 0 12",
            "card 0 0 11 10 9",
            "sw_char 1 8",
            "end",
            "sw_char 2 15",
            "skill 1 14 13 12",
            "end",
            "sw_char 1 15",
            "sw_char 0 14",
            "sw_char 2 13",
            "choose 0",
            "TEST 1 10 10 7 7 3 0",
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
        default_version:4.2
        charactor:Nilou
        charactor:Yaoyao
        charactor:Barbara
        The Starry Skies Their Flowers Rain*15
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
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_nilou_e_element()
    test_nilou_2()
    test_nilou_3()
