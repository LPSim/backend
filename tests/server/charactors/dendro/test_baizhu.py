from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_baizhu():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "card 1 0 9",
            "skill 2 8 7 6 5",
            "end",
            "sw_char 1 15",
            "skill 1 14 13 12",
            "sw_char 0 11",
            "TEST 1 40 40 40 39 40 37",
            "skill 0 10 9 8",
            "skill 0 7 6 5",
            "skill 2 4 3 2 1",
            "TEST 1 40 40 40 39 40 35",
            "end",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7 6",
            "end",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7 6",
            "TEST 1 40 40 40 39 40 27",
            "end"
        ],
        [
            "sw_card 1 2 3",
            "choose 0",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "card 1 0 9 8 7 6",
            "end",
            "sw_char 2 15",
            "TEST 2 p1 dice 16",
            "TEST 2 p0 dice 12",
            "end",
            "end",
            "TEST 1 40 40 40 39 40 30",
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
        charactor:Baizhu
        charactor:Nilou
        charactor:Tighnari
        All Things Are of the Earth*15
        Lotus Flower Crisp*15
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
                assert len(match.player_tables[
                    pidx].dice.colors) == int(cmd[4])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_baizhu_2():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "sw_char 2 9",
            "skill 0 8 7 6",
            "skill 0 5 4 3",
            "skill 2 2 1 0",
            "end",
            "sw_char 0 15",
            "skill 2 14 13 12 11",
            "skill 0 10 9 8",
            "skill 1 7 6 5",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "sw_char 2 9",
            "skill 0 8 7 6",
            "skill 0 5 4 3",
            "end",
            "sw_char 0 15",
            "card 1 0 14 13 12 11",
            "sw_char 2 10",
            "TEST 2 p1 dice 11",
            "skill 2 10 9 8",
            "sw_char 0 7",
            "skill 0 6 5 4",
            "TEST 2 p1 dice 4",
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
        charactor:Baizhu
        charactor:Nilou
        charactor:Xingqiu
        All Things Are of the Earth*15
        Lotus Flower Crisp*15
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
            elif test_id == 2:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[
                    pidx].dice.colors) == int(cmd[4])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_baizhu_3():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "skill 2 6 5 4 3",
            "sw_char 1 2",
            "end",
            "sw_char 0 15",
            "choose 1",
            "TEST 1 0 8 10 10 7 8",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "skill 1 9 8 7",
            "sw_char 2 6",
            "skill 1 5 4 3",
            "skill 1 2 1 0",
            "end",
            "skill 0 15 14 13"
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
        charactor:Baizhu
        charactor:Nilou
        charactor:Tighnari
        All Things Are of the Earth*15
        Lotus Flower Crisp*15
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
    test_baizhu()
    test_baizhu_2()
    test_baizhu_3()
