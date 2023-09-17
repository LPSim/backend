from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
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
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_lithic_spear():
    cmd_records = [
        [
            "sw_card 1 3",
            "choose 1",
            "card 1 0 15 14 13",
            "TEST 2 p0c1 usage 3",
            "skill 1 12 11 10",
            "skill 0 9 8 7",
            "skill 0 6 5 4",
            "skill 1 3 2 1",
            "end",
            "card 1 0 15 14 13",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "card 0 0",
            "card 4 0 6",
            "TEST 2 p0c1 usage 3",
            "skill 0 5 4 3",
            "skill 1 2 1 0",
            "end",
            "skill 1 15 14 13",
            "choose 4",
            "TEST 1 10 0 10 10 10 10 10 0 0 3",
            "end",
            "card 3 1 15 14 13",
            "skill 1 12 11 10",
            "skill 0 9 8 7",
            "skill 2 6 5 4",
            "skill 1 3 2 1",
            "end"
        ],
        [
            "sw_card 1 2 4",
            "choose 3",
            "TEST 2 p0c1 usage 3 2",
            "skill 1 15 14 13",
            "TEST 2 p0c1 usage",
            "TEST 1 10 10 10 10 10 10 10 10 6 10",
            "end",
            "choose 2",
            "skill 1 15 14",
            "sw_char 4 13",
            "skill 1 12 11 10",
            "sw_char 2 9",
            "skill 0 8 7 6",
            "choose 4",
            "card 0 1 5 4 3",
            "TEST 2 p1c4 usage 3",
            "skill 0 2 1 0",
            "end",
            "skill 2 15 14 13",
            "TEST 1 10 5 10 10 10 10 10 0 0 3",
            "card 0 1 12 11 10",
            "TEST 2 p1c4 usage 2",
            "skill 1 9 8 7",
            "end",
            "end",
            "choose 0",
            "choose 1",
            "card 4 0 15 14 13",
            "TEST 2 p1c1 usage",
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
        charactor:Xingqiu
        charactor:Candace
        charactor:Hu Tao
        charactor:Chongyun
        charactor:Shenhe
        Lithic Spear*10
        Lithic Spear@3.3*10
        Where Is the Unseen Razor?*10
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
                cidx = int(cmd[2][3])
                usages = [int(x) for x in cmd[4:]]
                status = match.player_tables[pidx].charactors[cidx].status
                assert len(usages) == len(status)
                for u, s in zip(usages, status):
                    assert u == s.usage
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_kings_squire():
    cmd_records = [
        [
            "sw_card 3 1 2",
            "choose 2",
            "card 2 1 15 14 13",
            "skill 0 12 11 10",
            "sw_char 0 9",
            "card 1 0",
            "card 1 0 8",
            "skill 1 7",
            "end"
        ],
        [
            "sw_card 1 2 3",
            "choose 0",
            "card 1 0 15 14 13",
            "skill 1 12",
            "sw_char 2 11",
            "card 0 0",
            "card 3 1 10",
            "card 1 0 9 8",
            "TEST 1 6 10 8 7 10 8",
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
        charactor:Fischl
        charactor:Nahida
        charactor:Collei
        Where Is the Unseen Razor?*10
        King's Squire*10
        Floral Sidewinder*10
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
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_kings_squire_2():
    cmd_records = [
        [
            "sw_card 4 2",
            "choose 2",
            "card 1 0 15 14 13",
            "card 1 0",
            "card 3 1 12",
            "skill 1 11",
            "sw_char 1 10",
            "end"
        ],
        [
            "sw_card 2 1",
            "choose 0",
            "card 1 0 15 14 13",
            "card 2 0",
            "card 3 1 12",
            "sw_char 2 11",
            "skill 1 10",
            "TEST 2 card 0 cost 2",
            "TEST 2 card 1 cost 4",
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
        charactor:Fischl
        charactor:Kamisato Ayaka
        charactor:Collei
        Where Is the Unseen Razor?*10
        King's Squire*10
        Floral Sidewinder*10
        Kanten Senmyou Blessing*10
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
            elif test_id == 2:
                cmd = cmd.split()
                cidx = int(cmd[3])
                cost = int(cmd[5])
                card = match.player_tables[1].hands[cidx]
                assert card.cost.total_dice_cost == cost
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_amos():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 0 0 15 14 13",
            "skill 1 12 11 10",
            "sw_char 1 9",
            "TEST 1 8 7 10 10 10 8",
            "card 0 0",
            "card 0 1 8",
            "skill 2 7 6 5 4 3",
            "TEST 1 8 2 10 7 7 2",
            "sw_char 2 2",
            "end",
            "sw_char 1 15",
            "skill 2 14 13 12 11 10",
            "TEST 1 8 2 8 4 4 0",
            "skill 2 9 8 7 6 5",
            "TEST 1 8 2 8 1 2 0",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "skill 0 15 14 13",
            "card 0 2 12 11 10",
            "skill 0 9 8 7",
            "TEST 1 8 7 10 7 7 2",
            "skill 2 6 5 4",
            "sw_char 0 3",
            "sw_char 2 2",
            "end",
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
        charactor:Fischl
        charactor:Ganyu
        charactor:Collei
        Where Is the Unseen Razor?*10
        Amos' Bow*10
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
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_fruit_of_fullfillment():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "card 2 2 15 14 13",
            "card 0 2 12 11 10",
            "card 2 0",
            "card 5 2 9",
            "TEST 1 p0 hand 8",
            "card 4 0",
            "card 4 2 8",
            "card 5 0",
            "card 4 2 7",
            "TEST 1 p0 hand 10",
            "card 4 2 6 5 4",
            "TEST 1 p0 hand 10",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "card 0 0 15 14 13",
            "TEST 1 p1 hand 6",
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
        charactor:Nahida
        charactor:Mona
        charactor:Klee
        Where Is the Unseen Razor?*10
        Fruit of Fulfillment*10
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
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                hand = match.player_tables[pidx].hands
                assert len(hand) == int(cmd[4])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_sacrificial():
    cmd_records = [
        [
            "sw_card 2 3",
            "choose 0",
            "card 1 0 15 14 13",
            "sw_char 1 12",
            "skill 1 11 10 9",
            "TEST 2 p1 dice 9",
            "skill 1 9 8 7",
            "TEST 2 p1 dice 7",
            "end",
            "skill 1 15 14 13",
            "skill 2 13 12 11",
            "TEST 1 9 2 9 2 8 4",
            "end"
        ],
        [
            "sw_card 1 2",
            "choose 1",
            "card 2 0 15 14 13",
            "sw_char 2 12",
            "TEST 2 p0 dice 10",
            "skill 0 11 10 9",
            "TEST 2 p0 dice 7",
            "skill 1 8 7 6",
            "card 3 0",
            "card 1 0 6",
            "sw_char 0 5",
            "skill 1 4 3 2",
            "TEST 2 p1 dice 3",
            "end",
            "TEST 2 p0 dice 14",
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
        charactor:Chongyun
        charactor:Fischl
        charactor:Yae Miko
        Where Is the Unseen Razor?*10
        Sacrificial Greatsword*10
        Sacrificial Sword*10
        Sacrificial Bow*10
        Sacrificial Fragments*10
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
                pidx = int(cmd[2][1])
                num = int(cmd[-1])
                assert len(match.player_tables[pidx].dice.colors) == num
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_wolf_gravestone():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 0 0 15 14 13",
            "skill 1 12 11 10",
            "skill 1 9 8 7",
            "sw_char 1 6",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "choose 0",
            "card 0 0 12 11 10",
            "skill 1 9 8 7",
            "skill 0 6 5 4",
            "skill 0 3 2 1",
            "TEST 1 4 1 9 10 0 10",
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
        charactor:Chongyun
        charactor:Fischl
        charactor:Yae Miko
        Where Is the Unseen Razor?*10
        Wolf's Gravestone*10
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
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_aquila_favonia():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 15 14 13",
            "sw_char 1 12",
            "skill 0 11 10 9",
            "sw_char 0 8",
            "card 0 0 7 6 5",
            "skill 1 4 3 2",
            "end",
            "TEST 1 7 7 9 8 8 7",
            "skill 2 15 14 13",
            "TEST 1 8 7 9 8 8 5",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "TEST 1 2 6 8 8 7 0",
            "sw_char 1 6",
            "end",
            "sw_char 0 15",
            "choose 2",
            "TEST 1 0 2 8 8 9 0",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 0 15 14 13",
            "sw_char 0 12",
            "skill 0 11 10 9",
            "sw_char 2 8",
            "end",
            "skill 0 15 14 13",
            "skill 1 12 11 10",
            "skill 2 9 8 7",
            "choose 1",
            "skill 1 6 5 4",
            "end",
            "card 1 1 15 14 13",
            "skill 0 12 11 10",
            "skill 0 9 8 7"
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
        charactor:Xingqiu
        charactor:Qiqi
        charactor:Yae Miko
        Aquila Favonia*20
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
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_skyward():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 0 0 15 14 13",
            "skill 1 12 11 10",
            "TEST 1 10 10 10 10 10 7",
            "skill 0 9 8 7",
            "skill 0 6 5 4"
        ],
        [
            "sw_card",
            "choose 2",
            "card 0 0 15 14 13",
            "skill 1 12 11 10",
            "TEST 1 10 10 10 10 10 3",
            "sw_char 1 9",
            "TEST 1 10 10 10 10 7 3",
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
        charactor:Xingqiu
        charactor:Kamisato Ayaka
        charactor:Yae Miko
        Skyward Atlas*3
        Skyward Blade*3
        Skyward Harp*3
        Skyward Pride*3
        Skyward Spine*3
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
    # test_the_bell()
    # test_vortex_vanquisher()
    # test_vortex_2()
    # test_lithic_spear()
    # test_kings_squire()
    # test_kings_squire_2()
    # test_amos()
    # test_fruit_of_fullfillment()
    # test_sacrificial()
    # test_wolf_gravestone()
    # test_aquila_favonia()
    test_skyward()
