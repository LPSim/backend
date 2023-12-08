from src.lpsim.agents.interaction_agent import (
    InteractionAgent_V1_0, InteractionAgent
)
from src.lpsim.agents.nothing_agent import NothingAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_usage, get_pidx_cidx, get_test_id_from_command, set_16_omni, 
    check_hp, make_respond, get_random_state
)


def test_rana():
    """
    first: test one round one time, can use imeediately, only elemental skill
    will trigger, can trigger multiple Rana.
    """
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent_V1_0(
        version = '1.0',
        player_idx = 1,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 0',
            'reroll 1 2 3 4 5 6 7',
            'card 0 0 omni geo',
            'skill 1 dendro dendro omni',
            'card 0 0 hydro hydro',
            'tune pyro 0',
            'card 0 0 dendro dendro',
            'end',
            'reroll 0 1 2 3 4 5 6 7',
            'skill 0 dendro pyro anemo',
            'tune hydro 0',
            'tune hydro 0',
            'skill 2 dendro dendro omni',
            'end',
            'reroll 3 4 5 6 7',
            'skill 1 dendro dendro dendro',
            'card 0 0 dendro dendro',
            'skill 1 dendro dendro dendro',
            'skill 0 dendro geo anemo'
        ],
        only_use_command = True
    )
    match = Match(version = '0.0.1', random_state = get_random_state())
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
                'hp': 99,
                'max_hp': 99,
            },
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
            },
            {
                'name': 'ElectroMobMage',
                'element': 'ELECTRO',
            },
        ],
        'cards': [
            {
                'name': 'Rana',
            }
        ] * 30,
    }
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    assert match.start()[0]
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            if len(agent_1.commands) == 6:
                # should only have two electro dice
                assert len(match.player_tables[1].dice.colors) == 2
                assert match.player_tables[1].dice.colors == ['ELECTRO', 
                                                              'ELECTRO']
                assert match.player_tables[1].dice.colors[0] == 'ELECTRO'
                assert match.player_tables[1].dice.colors[1] == 'ELECTRO'
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 3
    check_hp(match, [[83, 10, 10], [99, 10, 10]])
    assert len(match.player_tables[1].dice.colors) == 1
    assert match.player_tables[1].dice.colors[0] == 'PYRO'
    assert len(match.player_tables[1].supports) == 4
    for support in match.player_tables[1].supports:
        assert support.name == 'Rana'

    assert match.state != MatchState.ERROR

    """
    second: next one is other people; cannot generate when only one charactor;
    TODO: if overcharged self, will generate next of next?
    """
    agent_0 = InteractionAgent_V1_0(
        version = '1.0',
        player_idx = 0,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 2',
            'skill 0 omni omni omni',
            'end',
            'skill 0 omni omni omni',
            'end',
        ],
        only_use_command = True
    )
    agent_1 = InteractionAgent_V1_0(
        version = '1.0',
        player_idx = 1,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 0',
            'choose 2',
            'card 0 0 omni omni',
            'card 1 0 omni omni',
            'skill 1 omni omni omni',
            'sw_char 1 omni',
            'end',
            'choose 2',
            'skill 1 omni omni omni',
            'end',
        ],
        only_use_command = True
    )
    match = Match(version = '0.0.1', random_state = get_random_state())
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'PyroMobMage',
                'element': 'PYRO',
                'hp': 1,
                'max_hp': 1,
            },
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
                'hp': 1,
                'max_hp': 1,
            },
            {
                'name': 'ElectroMobMage',
                'element': 'ELECTRO',
            },
        ],
        'cards': [
            {
                'name': 'Rana',
            }
        ] * 30,
    }
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.random_first_player = False
    set_16_omni(match)
    assert match.start()[0]
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            if len(agent_1.commands) == 4:
                # should be 8 omni and 2 dendro
                assert len(match.player_tables[1].dice.colors) == 10
                omni_num = 8
                dendro_num = 2
                for die in match.player_tables[1].dice.colors:
                    if die == 'OMNI':
                        omni_num -= 1
                    else:
                        assert die == 'DENDRO'
                        dendro_num -= 1
                assert omni_num == 0
                assert dendro_num == 0
            elif len(agent_1.commands) == 1:
                # should be 13 omni
                assert len(match.player_tables[1].dice.colors) == 13
                for die in match.player_tables[1].dice.colors:
                    assert die == 'OMNI'
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert len(agent_0.commands) == 0
    assert match.round_number == 3
    check_hp(match, [[1, 1, 4], [0, 0, 10]])
    assert len(match.player_tables[1].supports) == 2
    for support in match.player_tables[1].supports:
        assert support.name == 'Rana'

    assert match.state != MatchState.ERROR


def test_timmie():
    """
    """
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "reroll",
            "card 0 0",
            "end",
            "reroll",
            "card 0 0",
            "card 4 0 6 7",
            "end",
            "TEST 11 record current dice color",
            "reroll",
            "TEST 1 all have 1 omni, compare with previous.0 tm2 1 tm2*3",
            "end",
            "reroll"
        ],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "reroll",
            "card 0 0",
            "card 2 0",
            "end",
            "reroll",
            "card 1 0 1",
            "card 1 0",
            "card 2 0",
            "card 2 1",
            "end",
            "reroll",
            "end",
            "TEST 22 record current dice color",
            "reroll",
            "TEST 2 check hand card number",
            "end"
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        default_version:4.0
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        Wine-Stained Tricorne*2
        Timmie*2
        Rana*2
        Strategize*2
        # not implement use timmie fill
        Timmie*22
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    assert match.start()[0]
    match.step()

    last_colors = [[], []]
    while True:
        if match.need_respond(0):
            while True:
                test_id = get_test_id_from_command(agent_0)
                if test_id == 1:
                    current_colors = [
                        match.player_tables[0].dice.colors.copy(),
                        match.player_tables[1].dice.colors.copy()
                    ]
                    assert len(current_colors[0]) == 9
                    assert len(current_colors[1]) == 9
                    assert current_colors[0][0] == 'OMNI'
                    assert current_colors[1][0] == 'OMNI'
                    assert current_colors[0][1:] == last_colors[0]
                    assert current_colors[1][1:] == last_colors[1]
                    tmcount = 0
                    for support in match.player_tables[0].supports:
                        if support.name == 'Timmie':
                            assert support.usage == 2
                            tmcount += 1
                    assert tmcount == 1
                    tmcount = 0
                    for support in match.player_tables[1].supports:
                        if support.name == 'Timmie':  # pragma: no branch
                            assert support.usage == 2
                            tmcount += 1
                    assert tmcount == 3
                elif test_id == 11:
                    last_colors = [
                        match.player_tables[0].dice.colors.copy(),
                        match.player_tables[1].dice.colors.copy()
                    ]
                else:
                    break
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 2:
                    current_colors = [
                        match.player_tables[0].dice.colors.copy(),
                        match.player_tables[1].dice.colors.copy()
                    ]
                    assert len(current_colors[0]) == 9
                    assert len(current_colors[1]) == 11
                    assert current_colors[0][0] == 'OMNI'
                    assert current_colors[1][0] == 'OMNI'
                    assert current_colors[1][1] == 'OMNI'
                    assert current_colors[1][2] == 'OMNI'
                    assert current_colors[0][1:] == last_colors[0]
                    assert current_colors[1][3:] == last_colors[1]
                    for support in match.player_tables[0].supports:
                        assert support.name != 'Timmie'
                    assert len(match.player_tables[1].supports) == 0
                    assert len(match.player_tables[0].hands) == 10
                    assert len(match.player_tables[1].hands) == 10
                elif test_id == 22:
                    last_colors = [
                        match.player_tables[0].dice.colors.copy(),
                        match.player_tables[1].dice.colors.copy()
                    ]
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_liben():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "reroll 1 7",
            "card 0 0",
            "card 0 0",
            "sw_char 1 0",
            "sw_char 0 0",
            "sw_char 1 3",
            "sw_char 0 3",
            "end",
            "TEST 1 p0 usage 2 1",
            "TEST 1 p1 usage 3 3 2 0",
            "reroll",
            "sw_char 1 3",
            "sw_char 0 3",
            "sw_char 1 3",
            "sw_char 0 3",
            "sw_char 1 3",
            "end",
            "TEST 1 p0 usage 3 2",
            "reroll"
        ],
        [
            "sw_card",
            "choose 0",
            "reroll",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "end",
            "reroll",
            "TEST 2 support all 2",
            "TEST 3 hand 7 dice 12 omni 4",
            "end",
            "reroll"
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
        charactor:PyroMobMage
        charactor:ElectroMobMage
        charactor:Noelle
        Liben*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
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
            # "TEST 2 support all 2",
            # "TEST 3 hand 7 dice 12 omni 4",
            elif test_id == 1:
                cmd = cmd.strip().split()
                pid = int(cmd[2][1])
                usg = [int(x) for x in cmd[4:]]
                for support, u in zip(match.player_tables[pid].supports, usg):
                    assert support.usage == u
            elif test_id == 2:
                for table in match.player_tables:
                    assert len(table.supports) == 2
            elif test_id == 3:
                table = match.player_tables[1]
                assert len(table.hands) == 7
                assert len(table.dice.colors) == 12
                for color in table.dice.colors[:4]:
                    assert color == 'OMNI'
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_setaria():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "reroll",
            "card 2 0 0",
            "card 3 0 0",
            "tune 0 0",
            "tune 0 0",
            "card 0 0 0",
            "TEST 1 p0 hand 2",
            "card 0 0 0",
            "tune 0 1",
            "TEST 1 p0 hand 1",
            "TEST 2 p0 support usage 2 3 3",
            "tune 0 2",
            "tune 0 3",
            "card 0 0 0",
            "TEST 2 p0 support usage 2 3 3",
            "card 0 0 0",
            "card 0 0 0",
            "card 0 0 0",
            "end",
            "TEST 2 p0 support usage 2 3 3",
            "reroll"
        ],
        [
            "sw_card",
            "choose 0",
            "reroll",
            "sw_char 1 0",
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
        charactor:Mona
        charactor:Nahida
        Setaria*15
        Strategize*15
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
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
                pid = int(cmd[2][1])
                assert len(match.player_tables[pid].hands) == int(cmd[4])
            elif test_id == 2:
                cmd = cmd.split()
                pid = int(cmd[2][1])
                us = [int(x) for x in cmd[5:]]
                assert len(match.player_tables[pid].supports) == len(us)
                for support, u in zip(match.player_tables[pid].supports, us):
                    assert support.usage == u
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_liusu():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 0 0 15",
            "card 1 0 14",
            "card 1 0 13",
            "sw_char 1 12",
            "TEST 1 p0 support 1 2 2",
            "sw_char 2 11",
            "sw_char 1 10",
            "TEST 1 p0 support 1 1 2",
            "end",
            "sw_char 0 15",
            "sw_char 1 14"
        ],
        [
            "sw_card",
            "choose 1",
            "TEST 1 p0 support 1 2 2",
            "sw_char 2 15",
            "end",
            "card 1 0 15",
            "sw_char 1 14",
            "TEST 1 p0 support 1 2",
            "TEST 1 p1 support 1",
            "sw_char 0 13",
            "TEST 1 p0 support 1 2",
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
        charactor:Electro Hypostasis
        charactor:Klee
        charactor:Keqing
        Liu Su*30
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
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                usage = [int(x) for x in cmd[4:]]
                support = match.player_tables[pidx].supports
                assert len(usage) == len(support)
                for u, s in zip(usage, support):
                    assert u == s.usage
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_tubby():
    cmd_records = [
        [
            "sw_card 4",
            "choose 0",
            "reroll",
            "card 1 0 7 6",
            "card 0 0",
            "card 1 0",
            "reroll 2 3",
            "TEST 1 card 1 cost 2",
            "card 0 0 4 3",
            "card 0 3",
            "TEST 2 p0 dice 4",
            "end",
            "reroll",
            "reroll",
            "card 0 2",
            "card 0 1",
            "end",
            "reroll",
            "card 1 3",
            "end"
        ],
        [
            "sw_card 2 1",
            "choose 0",
            "reroll",
            "end",
            "reroll",
            "card 2 0 6 5",
            "card 1 0 4 3",
            "card 3 0",
            "card 1 0 2 1",
            "end",
            "reroll",
            "card 3 3",
            "reroll",
            "card 3 1 6 5"
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
        charactor:Electro Hypostasis
        charactor:Klee
        charactor:Keqing
        Knights of Favonius Library*10
        Tubby*10
        Tenshukaku*10
        Vanarana*10
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
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
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                # a sample of HP check based on the command string.
                for req in match.requests:
                    if req.name == 'UseCardRequest' and req.card_idx == 1:
                        assert req.cost.total_dice_cost == 2
            elif test_id == 2:
                assert len(match.player_tables[0].dice.colors) == 4
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_chang_nine():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "card 2 0",
            "skill 0 15 14 13",
            "TEST 1 p0 support 1",
            "TEST 1 p1 support 1",
            "sw_char 4 12",
            "skill 2 11 10 9 8 7",
            "end",
            "card 5 4",
            "card 2 2",
            "card 2 0",
            "end",
            "TEST 1 p0 support 1",
            "TEST 1 p1 support 2",
            "skill 2 15 14 13 12 11"
        ],
        [
            "sw_card 1 2",
            "choose 0",
            "card 2 0",
            "skill 1 15 14 13",
            "sw_char 3 12",
            "TEST 1 p0 support 2",
            "TEST 1 p1 support 2",
            "skill 0 11 10 9",
            "card 1 0",
            "sw_char 1 8",
            "skill 0 7 6 5",
            "TEST 2 p0 card 6",
            "TEST 2 p1 card 5",
            "card 1 1",
            "TEST 1 p1 support 1",
            "sw_char 5 4",
            "skill 0 3 2 1",
            "sw_char 1 0",
            "end",
            "skill 0 15 14 13",
            "TEST 1 p0 support 1",
            "TEST 1 p1 support 2",
            "sw_char 2 12",
            "skill 1 11 10 9",
            "sw_char 3 8",
            "skill 1 7 6 5",
            "end",
            "card 0 0",
            "card 4 0",
            "card 6 0",
            "card 5 0",
            "TEST 1 p1 support 0 0 0 0",
            "card 4 1"
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
        charactor:Xingqiu
        charactor:AnemoMobMage
        charactor:Yae Miko
        charactor:Mona
        charactor:Ganyu
        charactor:Klee
        Chang the Ninth*15
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
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                usages = [int(x) for x in cmd[4:]]
                supports = match.player_tables[pidx].supports
                assert len(supports) == len(usages)
                for u, s in zip(usages, supports):
                    assert u == s.usage
            elif test_id == 2:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                card_num = int(cmd[4])
                assert len(match.player_tables[pidx].hands) == card_num
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_paimon_kujirai():
    cmd_records = [
        [
            "sw_card 1 4",
            "choose 0",
            "reroll",
            "card 3 0 7 6 5",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "end",
            "reroll",
            "TEST 1 p0 support 1 0 0 0",
            "TEST 1 p1 support 1 0",
            "TEST 2 p0 dice 12",
            "TEST 2 p1 dice 12",
            "end",
            "reroll",
            "TEST 1 p0 support 0 0",
            "TEST 1 p1 support 0 0",
            "TEST 2 p0 dice 12",
            "TEST 2 p1 dice 11",
            "card 2 0",
            "card 2 0",
            "sw_char 1 10",
            "end",
            "reroll"
        ],
        [
            "sw_card 2 1",
            "choose 0",
            "reroll",
            "card 0 0",
            "card 0 0",
            "card 0 0 5 4 0",
            "TEST 1 p0 support 2 0 0 0",
            "TEST 1 p1 support 0 0 2",
            "end",
            "reroll",
            "end",
            "reroll",
            "card 1 0",
            "card 0 0",
            "end",
            "reroll",
            "TEST 2 p0 dice 11",
            "TEST 2 p1 dice 12",
            "TEST 1 p0 support 0",
            "TEST 1 p1 support 0 0 0",
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
        charactor:Xingqiu
        charactor:AnemoMobMage
        charactor:Yae Miko
        charactor:Mona
        charactor:Ganyu
        charactor:Klee
        Chang the Ninth*15
        Kid Kujirai*15
        Paimon*15
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
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
                usages = [int(x) for x in cmd[4:]]
                supports = match.player_tables[pidx].supports
                assert len(supports) == len(usages)
                for u, s in zip(usages, supports):
                    assert u == s.usage
            elif test_id == 2:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                dice_num = int(cmd[4])
                assert len(match.player_tables[pidx].dice.colors) == dice_num
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_master_zhang():
    cmd_records = [
        [
            "sw_card 2 4",
            "choose 0",
            "end",
            "end",
            "card 1 0 15",
            "card 1 0 14",
            "TEST 1 card 1 cost 1",
            "card 1 0 13",
            "TEST 2 p0 support 0 0",
            "card 0 0",
            "TEST 1 card 5 cost 1",
            "card 4 0 12",
            "TEST 1 card 4 cost 0",
            "card 0 0 11",
            "card 3 1",
            "TEST 2 p0 support 0 0 0 1",
            "sw_char 1 10",
            "end",
            "card 3 0",
            "TEST 2 p0 support 0 0 1 1",
            "end"
        ],
        [
            "sw_card 1 2",
            "choose 0",
            "end",
            "end",
            "TEST 1 card 2 cost 3",
            "card 2 0 15 14 13",
            "card 4 0 12",
            "card 4 1 11",
            "end",
            "card 5 1",
            "TEST 1 card 6 cost 3",
            "card 5 0 15",
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
        charactor:Xingqiu
        charactor:Ganyu
        charactor:Fischl
        Master Zhang*15
        Where Is the Unseen Razor?*15
        King's Squire*15
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
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
                pidx = int(cmd[2][1])
                usages = [int(x) for x in cmd[4:]]
                supports = match.player_tables[pidx].supports
                assert len(supports) == len(usages)
                for u, s in zip(usages, supports):
                    assert u == s.usage
            elif test_id == 1:
                cmd = cmd.split()
                cid = int(cmd[3])
                cost = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseCardRequest' and req.card_idx == cid:
                        assert req.cost.total_dice_cost == cost
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_katheryne_tian_ellin():
    cmd_records = [
        [
            "sw_card 1 3",
            "choose 0",
            "skill 0 15 14 13",
            "sw_char 2 11",
            "skill 0 10 9 8",
            "card 3 0 7 6",
            "card 3 0 5 4",
            "skill 0 3 2 1",
            "end",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "end",
            "TEST 1 p1 dice 10",
            "TEST 1 p0 dice 16",
            "card 0 0 15",
            "end",
            "sw_char 1 15",
            "sw_char 2 14",
            "skill 2 13 12 11 10",
            "card 0 0 9 8",
            "skill 0 7 6 5",
            "TEST 2 p1 support 0 0 0 1",
            "card 2 0 4 3",
            "TEST 3 skill 0 cost 2",
            "skill 0 2 1",
            "end"
        ],
        [
            "sw_card 1 3",
            "choose 2",
            "skill 0 15 14 13",
            "sw_char 0 11",
            "skill 0 10 9 8",
            "card 2 0 7 6",
            "end",
            "TEST 2 p0 support 1 1",
            "TEST 2 p1 support 1",
            "end",
            "TEST 2 p0 support 1",
            "TEST 4 p0c0 charge 2",
            "TEST 4 p0c1 charge 3",
            "TEST 4 p0c2 charge 2",
            "TEST 4 p1c0 charge 2",
            "TEST 4 p1c1 charge 1",
            "TEST 4 p1c2 charge 1",
            "card 2 0 15",
            "card 2 0 14 13",
            "sw_char 2 12",
            "sw_char 1 11",
            "sw_char 0 10",
            "sw_char 1 9",
            "TEST 2 p0 support 1 1",
            "card 0 0 8 7",
            "card 0 0 6 5",
            "card 3 1 4 3",
            "sw_char 2 2",
            "end",
            "TEST 1 p0 dice 14",
            "TEST 1 p1 dice 16",
            "card 4 0 15 14",
            "skill 1 12 11 10",
            "TEST 3 skill 0 cost 3",
            "TEST 3 skill 1 cost 0",
            "skill 0 9 8 7",
            "TEST 3 skill 0 cost 0",
            "TEST 3 skill 1 cost 0",
            "skill 0",
            "TEST 2 p0 support 1 0 0 1",
            "TEST 2 p1 support 0 0 0 1",
            "TEST 3 skill 0 cost 2",
            "TEST 3 skill 1 cost 2",
            "TEST 3 skill 2 cost 4",
            "end",
            "TEST 3 skill 0 cost 3",
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
        charactor:Kaedehara Kazuha
        charactor:Klee
        charactor:Kaeya
        Ellin*10
        Iron Tongue Tian*10
        Katheryne*5
        Katheryne@3.3*5
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
            cmd = agent.commands[0].split()
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].dice.colors) == int(
                    cmd[4])
            elif test_id == 2:
                pidx = int(cmd[2][1])
                support = match.player_tables[pidx].supports
                check_usage(support, cmd[4:])
            elif test_id == 3:
                sid = int(cmd[3])
                cost = int(cmd[5])
                found = False
                for req in match.requests:
                    if req.name == 'UseSkillRequest' and req.skill_idx == sid:
                        found = True
                        assert req.cost.total_dice_cost == cost
                assert found
            elif test_id == 4:
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


def test_wagner_timaeus():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 0 0 15 14",
            "TEST 1 card 1 cost 1",
            "sw_char 2 13",
            "card 3 0 12 11",
            "end",
            "card 4 0 15 14",
            "TEST 2 p0 support 3 3 2",
            "end",
            "card 2 0 15 14",
            "TEST 1 card 4 cost 3",
            "card 3 0",
            "TEST 1 card 3 cost 0",
            "card 3 1",
            "TEST 2 p0 support 4 4 3 0",
            "end",
            "end",
            "end",
            "card 5 0 15 14",
            "card 0 2 13 12",
            "card 3 3 11 10",
            "card 3 3 9 8",
            "card 3 3 7 6",
            "end"
        ],
        [
            "sw_card 2 1 4",
            "choose 0",
            "card 2 0 15 14",
            "TEST 3 all card cost 0",
            "card 0 1",
            "TEST 2 p1 support 1",
            "TEST 3 all card cost 1",
            "card 0 1 13",
            "end",
            "card 2 0",
            "card 1 1",
            "card 0 1",
            "TEST 2 p1 usage 1",
            "TEST 1 card 0 usage 3",
            "end",
            "TEST 1 card 2 cost 3",
            "end",
            "card 1 0 15 14",
            "end",
            "card 0 1",
            "TEST 2 p1 usage 4 0",
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
        default_version:4.1
        charactor:Kaedehara Kazuha
        charactor:Klee
        charactor:Kaeya
        Timaeus*10
        Wagner*10
        Gambler's Earrings*10
        Tenacity of the Millelith*5
        Rhythm of the Great Dream*5
        Sacrificial Sword*5
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
            cmd = agent.commands[0].split()
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                cidx = int(cmd[3])
                cost = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseCardRequest' and req.card_idx == cidx:
                        assert req.cost.total_dice_cost == cost
            elif test_id == 2:
                pidx = int(cmd[2][1])
                support = match.player_tables[pidx].supports
                check_usage(support, cmd[4:])
            elif test_id == 3:
                cost = int(cmd[-1])
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert req.cost.total_dice_cost == cost
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_chef_mao():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "skill 1 15 14 13",
            "sw_char 0 12",
            "skill 1 11 10 9",
            "card 2 0 8",
            "card 3 0 7",
            "card 1 0",
            "TEST 1 p0 card 4",
            "TEST 3 p0 dice 9",
            "end",
            "sw_char 2 15",
            "sw_char 1 14",
            "sw_char 2 13",
            "card 0 2",
            "TEST 1 p0 card 5",
            "TEST 3 p0 dice 15",
            "card 0 0",
            "card 0 0",
            "TEST 3 p0 dice 15",
            "card 1 0 14",
            "card 1 0 13",
            "end",
            "card 1 3 15",
            "card 0 2",
            "TEST 1 p0 card 3",
            "end",
            "card 3 0 15",
            "card 3 1 14",
            "card 1 1",
            "TEST 1 p0 card 4",
            "end",
            "card 1 1",
            "TEST 1 p0 card 5",
            "card 4 1 15",
            "card 2 0",
            "TEST 1 p0 card 3",
            "end"
        ],
        [
            "sw_card 1 2 3",
            "choose 2",
            "skill 1 15 14 13",
            "card 2 0",
            "TEST 1 p1 card 4",
            "TEST 3 p1 dice 13",
            "skill 1 12 11 10",
            "card 1 0 9",
            "card 1 1",
            "TEST 3 p1 dice 10",
            "TEST 1 p1 card 2",
            "end",
            "sw_char 1 15",
            "sw_char 0 14",
            "skill 0 13 12 11",
            "card 0 0 10",
            "card 0 1",
            "TEST 3 p1 dice 12",
            "TEST 1 p1 card 3",
            "sw_char 1 11",
            "end",
            "end",
            "end",
            "TEST 2 p0 support 0 0 0 0",
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
        charactor:Kaedehara Kazuha
        charactor:Klee
        charactor:Kaeya
        Chef Mao*10
        Chef Mao@3.3*10
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
            cmd = agent.commands[0].split()
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].hands) == int(cmd[-1])
            elif test_id == 2:
                pidx = int(cmd[2][1])
                support = match.player_tables[pidx].supports
                check_usage(support, cmd[4:])
            elif test_id == 3:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[
                    pidx].dice.colors) == int(cmd[-1])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_dunyazard():
    cmd_records = [
        [
            "sw_card 0 1",
            "choose 0",
            "card 0 0 15",
            "TEST 1 card 0 cost 0",
            "TEST 1 card 1 cost 2",
            "TEST 1 card 2 cost 2",
            "end",
            "card 4 0 15 14",
            "end",
            "card 6 0",
            "end",
            "card 6 0",
            "card 4 1 15 14",
            "card 1 3 13 12",
            "end",
            "card 6 3 15 14",
            "end",
            "card 0 3",
            "end",
            "card 0 0",
            "TEST 3 p0 hand 9",
            "TEST 2 p0 support 0 0 1 2",
            "card 1 2",
            "TEST 3 p0 hand 8",
            "card 3 0",
            "TEST 3 p0 hand 8",
            "card 3 0 15 14",
            "end",
            "card 4 3 15 14",
            "card 7 3 13 12",
            "card 3 3",
            "TEST 3 p0 hand 7",
            "card 0 0 11",
            "TEST 3 p0 hand 7",
            "end",
            "end",
            "end",
            "end"
        ],
        [
            "sw_card 1 2",
            "choose 0",
            "TEST 1 card 1 cost 1",
            "card 1 0 15",
            "end",
            "card 5 0",
            "end",
            "card 5 0",
            "end",
            "card 0 0 15 14",
            "card 5 3",
            "end",
            "card 2 0",
            "TEST 2 p1 usage 0 0 1 2",
            "TEST 1 card 0 cost 2",
            "TEST 1 card 1 cost 0",
            "TEST 3 p1 hand 7",
            "card 5 3 15 14",
            "end",
            "card 1 3",
            "end",
            "card 0 0",
            "card 2 3",
            "TEST 3 p1 hand 8",
            "end",
            "card 3 0",
            "card 3 1",
            "end",
            "card 3 0 15 14",
            "end",
            "card 0 3",
            "TEST 3 p1 hand 10",
            "end",
            "TEST 4 p1 deck 11",
            "card 0 3",
            "card 0 3 15 14 13",
            "TEST 4 p1 deck 11",
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
        charactor:Kaedehara Kazuha
        charactor:Klee
        charactor:Kaeya
        Dunyarzad*10
        Dunyarzad@3.7*10
        Paimon*10
        NRE@3.3*10
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
            cmd = agent.commands[0].split()
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                cidx = int(cmd[3])
                cost = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseCardRequest' and req.card_idx == cidx:
                        assert req.cost.total_dice_cost == cost
            elif test_id == 2:
                pidx = int(cmd[2][1])
                support = match.player_tables[pidx].supports
                check_usage(support, cmd[4:])
            elif test_id == 3:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].hands) == int(cmd[-1])
            elif test_id == 4:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[
                    pidx].table_deck) == int(cmd[-1])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_xudong():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 2 0 15 14",
            "card 1 1",
            "card 3 1 13 12",
            "card 1 0 11 10",
            "card 3 0",
            "end",
            "choose 1",
            "card 2 0",
            "card 12 0",
            "TEST 1 card 0 cost 1",
            "card 5 0 15 14",
            "card 0 0",
            "TEST 2 p0 usage 0 0 0",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "sw_char 2 15",
            "skill 1 14 13 12",
            "skill 1 11 10 9",
            "skill 2 8 7 6 5",
            "skill 1 4 3 2",
            "sw_char 1 1",
            "sw_char 2 0",
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
        charactor:Rhodeia of Loch
        charactor:Mona
        charactor:Kaeya
        Xudong*10
        Adeptus' Temptation*10
        Sweet Madame*10
        Lotus Flower Crisp*10
        Teyvat Fried Egg@3.7*10
        # Hanachirusato*10
        # Guardian's Oath*10
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
    match.config.initial_hand_size = 20
    match.config.max_hand_size = 30
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
            cmd = agent.commands[0].split()
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                cidx = int(cmd[3])
                cost = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseCardRequest' and req.card_idx == cidx:
                        assert req.cost.total_dice_cost == cost
            elif test_id == 2:
                pidx = int(cmd[2][1])
                support = match.player_tables[pidx].supports
                check_usage(support, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_hanachirusato():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 2 15 14 13 12 11",
            "card 3 0",
            "skill 0 10 9 8",
            "skill 0 7 6 5",
            "end",
            "card 2 0",
            "card 2 0",
            "TEST 1 card 0 cost 3",
            "card 2 0 15 14 13 12",
            "TEST 2 p0 usage 3 3 3",
            "card 2 0",
            "TEST 2 p0 usage 3",
            "card 0 0 11",
            "end",
            "TEST 2 p1 usage 3",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "card 5 0",
            "card 3 0 15 14 13 12",
            "TEST 1 card 0 cost 3",
            "card 13 0",
            "TEST 2 p1 support 2 0",
            "skill 2 11 10 9 8 7",
            "end",
            "TEST 2 p1 usage 3 1",
            "TEST 2 p0 usage 1",
            "TEST 1 card 0 cost 1",
            "TEST 1 card 1 cost 4",
            "TEST 1 card 4 cost 0",
            "card 4 0",
            "TEST 2 p1 usage 1",
            "skill 2 15 14 13 12 11",
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
        charactor:Rhodeia of Loch
        charactor:Mona
        charactor:Noelle
        Hanachirusato*10
        Guardian's Oath*10
        Tenacity of the Millelith*10
        Gambler's Earrings*10
        The Bell*10
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
    match.config.initial_hand_size = 20
    match.config.max_hand_size = 30
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
            cmd = agent.commands[0].split()
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                cidx = int(cmd[3])
                cost = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseCardRequest' and req.card_idx == cidx:
                        assert req.cost.total_dice_cost == cost
            elif test_id == 2:
                pidx = int(cmd[2][1])
                support = match.player_tables[pidx].supports
                check_usage(support, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_chefmao_dunyarzad():
    cmd_records = [
        [
            "sw_card 2",
            "choose 0",
            "card 2 0 15",
            "TEST 1 p0 hand 4",
            "card 1 0",
            "TEST 1 p0 hand 4",
            "card 3 0",
            "TEST 1 p0 hand 3",
            "skill 0 14 13 12",
            "end",
            "end",
            "card 3 0",
            "TEST 1 p0 hand 7",
            "card 5 0",
            "TEST 1 p0 hand 7",
            "card 3 3",
            "TEST 1 p0 hand 7",
            "card 0 0",
            "TEST 1 p0 hand 8",
            "sw_char 1 15",
            "card 0 0",
            "TEST 1 p0 hand 7",
            "end"
        ],
        [
            "sw_card 2 1",
            "choose 0",
            "card 1 0 15",
            "card 3 0 14",
            "TEST 1 p1 hand 3",
            "card 1 0",
            "card 0 0",
            "TEST 1 p1 hand 3",
            "skill 0 13 15 14",
            "end",
            "end",
            "card 6 0 15",
            "card 0 0",
            "TEST 1 p1 hand 7",
            "card 4 3",
            "TEST 1 p1 hand 6",
            "card 1 0",
            "TEST 1 p1 hand 6",
            "skill 0 14 15 13"
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
        charactor:Kaedehara Kazuha
        charactor:Klee
        charactor:Kaeya
        Dunyarzad*10
        Chef Mao*10
        Timmie*10
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
                pidx = int(cmd[2][1])
                hand = int(cmd[4])
                assert hand == len(match.player_tables[pidx].hands)
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_yayoi_fix():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "end",
            "end",
            "end",
            "end"
        ],
        [
            "sw_card 2 1",
            "choose 2",
            "card 1 0 15",
            "card 1 1 14 13",
            "end",
            "card 2 2 15",
            "end",
            "card 0 0",
            "end",
            "card 2 1",
            "card 4 2 15 14 13",
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
        default_version:4.3
        charactor:Yoimiya@3.8
        charactor:Keqing@3.3
        charactor:Dehya@4.1
        Yayoi Nanatsuki*10
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
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    # test_rana()
    test_timmie()
    test_liben()
    # test_setaria()
    # test_liusu()
    # test_tubby()
    # test_chang_nine()
    # test_paimon_kujirai()
    # test_master_zhang()
    # test_katheryne_tian_ellin()
    # test_wagner_timaeus()
    test_chef_mao()
    test_dunyazard()
    # test_xudong()
    # test_hanachirusato()
    test_chefmao_dunyarzad()
    test_yayoi_fix()
