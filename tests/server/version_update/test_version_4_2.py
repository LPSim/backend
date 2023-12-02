from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, check_usage, get_pidx_cidx, get_random_state, 
    get_test_id_from_command, make_respond, set_16_omni
)


def test_joy_4_2_and_cost_change_cards():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 0 0 1",
            "skill 0 1 14 13",
            "skill 0 1 11 10",
            "end",
            "end",
            "end",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "sw_char 2 15",
            "end",
            "end",
            "end",
            "end",
            "TEST 1 p0c0 app",
            "TEST 1 p0c1 app",
            "TEST 1 p0c2 app",
            "card 0 0 1",
            "TEST 1 p1c0 app",
            "TEST 1 p1c1 app",
            "TEST 1 p1c2 app",
            "TEST 2 p0 hand cost 3 3 4 4 2 4 4 3 3 4",
            "TEST 2 p1 hand cost 3 3 3 3 4 4 3 4 4",
            "TEST 3 p0 hand 5 charge 2",
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
        charactor:Nahida
        charactor:Xiangling
        charactor:Mona
        Joyous Celebration
        Mirror Cage
        Mirror Cage@4.1
        Glorious Season
        Glorious Season@4.1
        Absorbing Prism
        Absorbing Prism@4.1
        Crossfire
        Crossfire@4.1
        The Overflow
        The Overflow@4.1
        Lands of Dandelion
        Lands of Dandelion@4.1
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
                pidx, cidx = get_pidx_cidx(cmd)
                assert match.player_tables[pidx].charactors[
                    cidx].element_application == []
            elif test_id == 2:
                pidx = int(cmd[2][1])
                hands = match.player_tables[pidx].hands
                costs = cmd[5:]
                assert len(hands) == len(costs)
                for h, c in zip(hands, costs):
                    c = int(c)
                    assert h.cost.total_dice_cost == c
            elif test_id == 3:
                assert match.player_tables[0].hands[5].cost.charge == 2
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_chongyun_yoimiya_beidou():
    cmd_records = [
        [
            "sw_card 0 2",
            "choose 0",
            "card 1 0 15 14 13 12",
            "TEST 2 p0 status 3",
            "TEST 2 p1 status 2",
            "skill 0 11 10 9",
            "TEST 1 4 10 10 4 10 10",
            "sw_char 1 8",
            "card 1 0 7 6",
            "TEST 3 p0c1 usage 3",
            "TEST 3 p1c1 usage 2",
            "skill 0 5 4 3",
            "TEST 1 4 6 10 4 6 10",
            "sw_char 2 2",
            "end",
            "end",
            "card 5 0 15 14 13",
            "sw_char 1 12",
            "skill 0 11 10",
            "skill 0 9 8",
            "skill 0 7 6 5",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "card 2 0 15 14 13",
            "skill 0 12 11 10",
            "sw_char 1 9",
            "card 3 0 8 7",
            "skill 0 6 5 4",
            "sw_char 2 3",
            "end",
            "end",
            "sw_char 1 1",
            "card 3 0 11 10 9",
            "skill 0 11 10 9",
            "skill 1 8 7 6",
            "skill 0 5 4",
            "TEST 1 4 1 3 4 1 3",
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
        charactor:Chongyun
        charactor:Yoimiya
        charactor:Beidou
        Steady Breathing*2
        Steady Breathing@4.1*2
        Lightning Storm*2
        Lightning Storm@4.1*2
        Naganohara Meteor Swarm*2
        Naganohara Meteor Swarm@4.1*2
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
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].team_status, cmd[4:])
            elif test_id == 3:
                pidx, cidx = get_pidx_cidx(cmd)
                check_usage(match.player_tables[pidx].charactors[
                    cidx].status, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_razor_sara_cyno():
    cmd_records = [
        [
            "sw_card 1 2",
            "choose 0",
            "card 0 0 15 14 13",
            "skill 1 12 11 10",
            "TEST 2 p0c1 charge 0",
            "TEST 2 p1c1 charge 1",
            "sw_char 1 9",
            "card 1 0 8 7 6",
            "sw_char 2 5",
            "card 0 0 4 3 2",
            "end",
            "skill 1 15 14 13",
            "sw_char 0 12",
            "end",
            "sw_char 1 15",
            "end",
            "TEST 1 2 2 2 4 5 4",
            "sw_char 2 15",
            "skill 0 14 13 12",
            "skill 1 11 10 9",
            "skill 1 8 7 6",
            "TEST 1 2 2 2 4 2 0",
            "end"
        ],
        [
            "sw_card 3 2",
            "choose 0",
            "card 1 0 15 14 13 12",
            "skill 1 11 10 9",
            "sw_char 1 8",
            "skill 0 7 6 5",
            "card 0 0 4 3 2 1",
            "TEST 1 4 8 9 4 5 10",
            "sw_char 2 0",
            "end",
            "card 1 0 15 14 13",
            "TEST 1 4 8 2 4 5 4",
            "end",
            "end",
            "skill 1 15 14 13",
            "end",
            "choose 1"
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
        charactor:Razor
        charactor:Kujou Sara
        charactor:Cyno
        Awakening
        Awakening@4.1
        Sin of Pride
        Sin of Pride@4.1
        Featherfall Judgment
        Featherfall Judgment@4.1
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
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                pidx, cidx = get_pidx_cidx(cmd)
                assert match.player_tables[pidx].charactors[
                    cidx].charge == int(cmd[4])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_jean_kokomi_amber():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7 6",
            "end",
            "TEST 1 10 10 5 10 10 10 10 8",
            "sw_char 1 15",
            "card 2 0 14 13 12",
            "sw_char 2 11",
            "skill 0 10 9 8",
            "sw_char 1 7",
            "skill 0 6 5 4",
            "TEST 1 10 5 5 10 10 4 10 8",
            "sw_char 0 3",
            "skill 0 2 1 0",
            "end",
            "skill 1 15 14 13",
            "card 1 0 12 11 10",
            "TEST 2 p1 summon 2",
            "end",
            "TEST 1 6 3 5 10 7 2 10 8",
            "sw_char 3 15",
            "end",
            "end",
            "sw_char 0 15",
            "skill 0 14 13 12",
            "skill 0 11 10 9",
            "skill 2 8 7 6",
            "TEST 2 p1 summon",
            "TEST 2 p0 summon 1",
            "end"
        ],
        [
            "sw_card",
            "choose 3",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "skill 2 6 5 4 3",
            "end",
            "sw_char 1 15",
            "card 2 0 14 13 12",
            "sw_char 3 11",
            "skill 0 10 9 8",
            "sw_char 1 7",
            "skill 0 6 5 4",
            "sw_char 0 3",
            "skill 0 2 1 0",
            "end",
            "skill 1 15 14 13",
            "TEST 2 p0 summon 3",
            "TEST 2 p1 summon 2",
            "card 2 0 12 11 10",
            "end",
            "sw_char 2 15",
            "end",
            "end",
            "sw_char 0 15",
            "skill 0 14 13 12",
            "skill 0 11 10 9",
            "skill 2 8 7 6"
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
        charactor:Sangonomiya Kokomi
        charactor:Amber
        charactor:Jean
        charactor:Jean@3.3
        Tamakushi Casket
        Tamakushi Casket@4.1
        Bunny Triggered
        Bunny Triggered@4.1
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
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:4], hps[4:]]
                check_hp(match, hps)
            elif test_id == 2:
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


def test_yanfei_4_2():
    cmd_records = [
        [
            "sw_card 0 1 3",
            "choose 0",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "TEST 1 p0c0 status 2",
            "TEST 1 p1c1 status 1",
            "sw_char 1 9",
            "card 1 0 8 7 6",
            "end",
            "sw_char 0 15",
            "card 5 0 14 13 12",
            "TEST 2 p0 hand 5",
            "skill 0 11 10 9",
            "TEST 2 p0 hand 5",
            "skill 0 8 7 6",
            "card 4 0 5 4 3",
            "TEST 2 p0 hand 5",
            "end"
        ],
        [
            "sw_card 1 2 3 4",
            "choose 1",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "sw_char 0 9",
            "sw_char 1 8",
            "card 3 0 7 6 5",
            "TEST 2 p1 hand 5",
            "sw_char 0 4",
            "end",
            "end",
            "choose 1"
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
        charactor:Yanfei
        charactor:Yanfei@4.1
        Right of Final Interpretation*5
        Right of Final Interpretation@4.1*5
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
                pidx, cidx = get_pidx_cidx(cmd)
                check_usage(match.player_tables[pidx].charactors[
                    cidx].status, cmd[4:])
            elif test_id == 2:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].hands) == int(cmd[4])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_rhodeia_shenhe_itto():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "TEST 2 p0 usage 2",
            "TEST 2 p1 usage 3",
            "sw_char 1 12",
            "skill 0 11 10 9",
            "skill 0 8 7 6",
            "skill 0 5 4 3",
            "skill 3 2 1 0",
            "TEST 1 8 5 10 8 3 10",
            "end",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "sw_char 2 6",
            "sw_char 0 5",
            "end",
            "sw_char 1 15",
            "skill 3 14 13 12",
            "sw_char 2 11",
            "skill 1 10 9 8",
            "skill 1 7 6 5",
            "skill 1 4 3 2",
            "end",
            "TEST 1 1 3 1 3 0 10",
            "card 3 2 15",
            "card 2 1 14",
            "card 1 0 13",
            "skill 2 12 11 10",
            "end",
            "skill 0 15 14",
            "card 3 2 13",
            "card 3 1 12",
            "card 2 0 11",
            "sw_char 1 10",
            "TEST 1 5 1 5 3 0 10",
            "skill 0 9 8 7",
            "skill 1 6 5 4",
            "skill 1 3 2 1",
            "end",
            "skill 3 15 14 13",
            "TEST 1 5 1 5 3 0 3",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "skill 0 11 10 9",
            "skill 0 8 7 6",
            "skill 0 5 4 3",
            "skill 3 2 1 0",
            "end",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "sw_char 0 6",
            "sw_char 1 5",
            "skill 3 4 3 2",
            "end",
            "choose 0",
            "skill 0 15 14 13",
            "TEST 1 1 3 10 3 0 10",
            "sw_char 2 12",
            "skill 1 11 10 9",
            "skill 1 8 7 6",
            "skill 1 5 4 3",
            "end",
            "skill 2 15 14 13",
            "TEST 1 3 5 3 3 0 6",
            "card 0 0 12",
            "card 3 0 11",
            "end",
            "sw_char 0 15",
            "card 5 1 14",
            "card 0 0 13",
            "TEST 1 3 5 3 3 0 10",
            "sw_char 2 12",
            "skill 0 11 10",
            "end",
            "card 9 1 15",
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
    deck1 = Deck.from_str(
        '''
        default_version:4.2
        charactor:Shenhe
        charactor:Rhodeia of Loch
        charactor:Arataki Itto
        Mondstadt Hash Brown*30
        '''
    )
    deck2 = Deck.from_str(
        '''
        default_version:4.1
        charactor:Shenhe
        charactor:Rhodeia of Loch
        charactor:Arataki Itto
        Mondstadt Hash Brown*30
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
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].team_status, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_kokomi_2():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "sw_char 2 12",
            "skill 1 11 10 9",
            "sw_char 0 8",
            "skill 0 7 6 5",
            "skill 0 4 3 2",
            "end",
            "card 5 0 15 14 13",
            "TEST 1 p0 summon 1 1",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "sw_char 0 12",
            "skill 1 11 10 9",
            "skill 1 8 7 6",
            "skill 2 5 4 3",
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
        default_version:4.2
        charactor:Sangonomiya Kokomi
        charactor:Fischl
        charactor:Arataki Itto
        Tamakushi Casket*30
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


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level = logging.INFO)
    test_joy_4_2_and_cost_change_cards()
    # test_chongyun_yoimiya_beidou()
    # test_razor_sara_cyno()
    # test_jean_kokomi_amber()
    # test_yanfei_4_2()
    # test_rhodeia_shenhe_itto()
    test_kokomi_2()
