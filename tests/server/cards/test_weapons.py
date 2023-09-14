from agents.interaction_agent import InteractionAgent
from server.match import Match, MatchState
from server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_vanilla_weapons():
    # use frontend and FastAPI server to perform commands, and test commands 
    # that start with TEST. NO NOT put TEST at the end of command list!
    # If a command is succesfully performed, frontend will print history 
    # commands in console. Note that frontend cannot distinguish if a new
    # match begins, so you need to refresh the page before recording a new
    # match, otherwise the history commands will be mixed.
    #
    # for tests, it starts with TEST and contains a test id, which is used to
    # identify the test. Other texts in the command are ignored, but you can
    # parse them if you want. Refer to the following code.
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "end",
            "end",
            "end",
            "TEST 2 weapon target right",
            "card 0 0 0 1",
            "skill 1 0 1 2",
            "TEST 1 10 10 90 10 10 8 10 90 10 10",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "end",
            "TEST 1 10 10 85 10 10 8 10 90 10 9",
            "end",
            "card 1 0 0 1",
            "card 3 0 0 1",
            "sw_char 1 0",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "end",
            "end",
            "end",
            "TEST 1 10 10 90 10 10 8 10 90 10 10",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "TEST 1 10 10 89 10 10 8 10 90 10 10",
            "sw_char 1 0",
            "sw_char 0 0",
            "card 5 0 0 1",
            "skill 0 0 1",
            "TEST 1 10 10 89 10 10 8 10 90 10 10",
            "sw_char 4 0",
            "skill 1 0 1 2",
            "end",
            "sw_char 0 0",
            "skill 2 0 1 2",
            "TEST 1 10 10 78 10 10 8 10 90 10 9",
            "end",
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
        charactor:Arataki Itto
        charactor:Barbara
        charactor:Noelle
        charactor:PhysicalMob
        charactor:Fischl
        Magic Guide*2
        Raven Bow*2
        Traveler's Handy Sword*2
        White Iron Greatsword*2
        White Tassel*2
        '''
    )
    deck.charactors[2].hp = 90
    deck.charactors[2].max_hp = 90
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
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
                cards = match.player_tables[0].hands
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        card = cards[req.card_idx]
                        targets = req.targets
                        for target in targets:
                            assert target.charactor_idx != 3  # 3 is mob
                        if card.name == 'Magic Guide':
                            assert len(targets) == 1
                            assert targets[0].charactor_idx == 1
                        elif card.name == 'White Iron Greatsword':
                            assert len(targets) == 2
                            assert targets[0].charactor_idx == 0
                            assert targets[1].charactor_idx == 2
                        elif card.name == 'Raven Bow':
                            assert len(targets) == 1
                            assert targets[0].charactor_idx == 4
                        else:
                            raise AssertionError('Other weapon cannot use')
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_the_bell():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 0 1 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 p1 status 1 usage 1",
            "end",
            "end",
            "end",
            "sw_char 1 0",
            "TEST 1 p1 status 1 usage 2",
            "skill 1 0 1 2",
            "TEST 1 p1 status 1 usage 2",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "TEST 1 p0 status 0 usage 0",
            "card 0 0 0 1 2",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 p1 status 1 usage 1",
            "end",
            "skill 1 0 1 2",
            "TEST 1 p1 status 1 usage 2",
            "end",
            "end",
            "skill 1 0 1 2",
            "card 0 0 0 1 2",
            "skill 1 0 1 2"
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
        charactor:Arataki Itto
        charactor:Barbara
        charactor:Noelle
        The Bell*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
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
                cmd = cmd.strip().split()
                pid = int(cmd[2][1])
                snum = int(cmd[4])
                usage = int(cmd[6])
                status = match.player_tables[pid].team_status
                assert len(status) == snum
                if snum:
                    assert status[0].usage == usage
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_a_thousand():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "end",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "sw_char 1 0",
            "sw_char 2 0",
            "choose 1",
            "sw_char 0 0",
            "sw_char 1 0",
            "TEST 1 3 7 0 10 10 4",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "card 0 0 0 1 2",
            "skill 1 0",
            "skill 0 0 1 2",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "TEST 1 10 10 6 10 10 6",
            "end",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 0 0 1 2"
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
        charactor:Venti
        charactor:Xingqiu
        charactor:Noelle
        Mondstadt Hash Brown*30
        '''
    )
    deck2 = Deck.from_str(
        '''
        charactor:Nahida
        charactor:Maguu Kenki
        charactor:Yoimiya
        A Thousand Floating Dreams*30
        '''
    )
    match.set_deck([deck1, deck2])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
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
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_vortex_vanquisher():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 1 0 15 14 13",
            "skill 1 12 11 10",
            "sw_char 3 9",
            "skill 0 8 7 6",
            "sw_char 0 5",
            "skill 0 4 3 2",
            "TEST 1 8 10 10 10 10 10 10 2",
            "TEST 2 p0 usage 1",
            "end",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "TEST 1 7 10 10 10 10 10 0 2",
            "end",
            "skill 1 15 14 13",
            "TEST 1 2 10 10 10 10 7 0 2",
            "sw_char 3 12",
            "skill 0 11 10 9",
            "sw_char 0 8",
            "skill 1 7 6 5",
            "end",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "TEST 1 2 10 10 8 1 0 0 2",
            "end"
        ],
        [
            "sw_card 3 2",
            "choose 3",
            "skill 1 15 14 13",
            "TEST 1 10 10 10 10 10 10 10 6",
            "skill 1 12 11 10",
            "end",
            "sw_char 2 15",
            "skill 1 14 13 12",
            "TEST 1 8 10 10 10 10 10 5 2",
            "TEST 2 p0 usage 1",
            "sw_char 1 11",
            "sw_char 2 10",
            "choose 1",
            "TEST 1 8 10 10 10 10 10 0 2",
            "skill 0 9 8 7",
            "end",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "sw_char 0 9",
            "sw_char 1 8",
            "sw_char 0 7",
            "end",
            "sw_char 1 15",
            "TEST 2 p0 usage 3",
            "end",
            "choose 0"
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
        charactor:Candace*2
        charactor:Diluc
        charactor:Ningguang
        Sweet Madame*15
        Vortex Vanquisher*15
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
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
                assert len(match.player_tables[pidx].team_status) == 1
                assert match.player_tables[pidx].team_status[
                    0].usage == int(cmd[-1])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_vortex_2():
    cmd_records = [
        [
            "sw_card",
            "choose 3",
            "sw_char 2 15",
            "skill 1 14 13 12",
            "sw_char 3 11",
            "TEST 1 10 10 10 7 10 7 10 10",
            "card 3 2 10 9 8",
            "card 2 0",
            "skill 1 7 6",
            "skill 0 5 4 3"
        ],
        [
            "sw_card",
            "choose 2",
            "sw_char 1 15",
            "sw_char 2 14",
            "skill 1 13 12 11",
            "sw_char 1 10",
            "TEST 1 10 10 10 8 10 1 10 10",
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
        charactor:Candace*2
        charactor:Chongyun
        charactor:Hu Tao
        Sweet Madame*15
        Vortex Vanquisher*15
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
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
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_vanilla_weapons()
    test_the_bell()
    test_vortex_vanquisher()
    test_vortex_2()
