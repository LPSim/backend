from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.agents.nothing_agent import NothingAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_bestest():
    """
    AA + electro A + talent
    """
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "reroll",
            "TEST 1 omni 1",
            "card 0 0 6 7",
            "TEST 2 omni 3",
            "card 2 0 6 7",
            "TEST 3 omni 5",
            "card 2 0 4 7",
            "TEST 4 omni 6",
            "end",
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        """
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        Wine-Stained Tricorne*2
        Timmie*2
        Rana*2
        Strategize*2
        The Bestest Travel Companion!*2
        The Bestest Travel Companion!*20
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                cmd = agent_1.commands[0]
                test_id = get_test_id_from_command(agent_1)
                if test_id == 0:
                    break
                omni_num = int(cmd[-1])
                for color in match.player_tables[1].dice.colors:
                    if color == 'OMNI':
                        omni_num -= 1
                assert omni_num == 0
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_changing_shifts():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 1",
            "card 0 0",
            "card 0 0",
            "TEST 1 status usage 1",
            "skill 0 0 1 2",
            "TEST 1 status 1 usage 1",
            "sw_char 0",
            "TEST 3 status 0",
            "sw_char 1 0",
            "card 0 0",
            "sw_char 0",
            "TEST 4 dice 12",
            "card 0 0",
            "end",
            "TEST 1 status usage 1",
            "end"
        ],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 1",
            "sw_char 0 0",
            "sw_char 1 0",
            "end",
            "end"
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        # Gambler's Earrings*2
        # Wine-Stained Tricorne*2
        # Vanarana
        # Timmie*2
        # Rana*2
        # Covenant of Rock
        # Wind and Freedom
        # The Bestest Travel Companion!*2
        # Changing Shifts*2
        # Strategize*2
        Changing Shifts*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.random_first_player = False
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            while True:
                test_id = get_test_id_from_command(agent_0)
                if test_id == 1:
                    assert len(match.player_tables[0].team_status) == 1
                    assert match.player_tables[0].team_status[0].usage == 1
                elif test_id == 3:
                    assert len(match.player_tables[0].team_status) == 0
                elif test_id == 4:
                    assert len(match.player_tables[0].dice.colors) == 12
                else:
                    break
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_toss_up():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "card 0 0",
            "TEST 2 reroll req 2 time",
            "reroll 0 1 2 3 4 5 6 7",
            "TEST 1 reroll req 1 time",
            "reroll 0 1 2 3 4 5 6 7",
            "end",
        ],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "card 0 0",
            "reroll 0 1 2 3 4 5 6 7",
            "reroll 0 1 2 3 4 5 6 7",
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        # Gambler's Earrings*2
        # Wine-Stained Tricorne*2
        # Vanarana
        # Timmie*2
        # Rana*2
        # Covenant of Rock
        # Wind and Freedom
        # The Bestest Travel Companion!*2
        # Changing Shifts*2
        # Toss-Up
        # Strategize*2
        Toss-Up*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.random_first_player = False
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            while True:
                test_id = get_test_id_from_command(agent_0)
                if test_id == 0:
                    break
                assert len(match.requests) == 1
                req = match.requests[0]
                assert req.name == 'RerollDiceRequest'
                assert req.reroll_times == test_id
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_i_havent_lost_yet():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "TEST 1 no card can use",
            "skill 0 0 1 2",
            "choose 1",
            "TEST 2 cards can use",
            "end",
            "TEST 1 card cannot use",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "choose 1",
            "TEST 2 card can use",
            "end",
            "TEST 1 no status cannot use card",
            "end",
            "skill 1 0 1 2",
            "choose 3",
            "card 0 0",
            "TEST 3 dice 14",
            "end",
            "sw_char 4 0",
            "choose 3",
            "skill 1 0 1 2",
            "end"
        ],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2",
            "end",
            "choose 1",
            "card 2 0",
            "TEST 1 charge 1 status cannot use card",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "end",
            "end",
            "choose 1",
            "skill 1 0 1 2",
            "end",
            "skill 3 0 1 2",
            "choose 3",
            "card 0 0",
            "TEST 2",
            "end"
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        # charactor:Fischl
        # charactor:Mona
        charactor:Nahida*10
        # Gambler's Earrings*2
        # Wine-Stained Tricorne*2
        # Vanarana
        # Timmie*2
        # Rana*2
        # Covenant of Rock
        # Wind and Freedom
        # The Bestest Travel Companion!*2
        # Changing Shifts*2
        # Toss-Up
        # Strategize*2
        # I Haven't Lost Yet!*2
        I Haven't Lost Yet!*30
        '''
    )
    for charactor in deck.charactors:
        charactor.hp = 2
        charactor.max_hp = 2
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.charactor_number = 10
    match.config.random_first_player = False
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            while True:
                test_id = get_test_id_from_command(agent_0)
                if test_id == 1:
                    assert len(match.player_tables[0].team_status) == 0
                    for req in match.requests:
                        assert req.name != 'UseCardRequest'
                elif test_id == 2:
                    use_card_req = 0
                    for req in match.requests:
                        if req.name == 'UseCardRequest':
                            use_card_req += 1
                    assert use_card_req > 0
                elif test_id == 3:
                    assert len(match.player_tables[0].dice.colors) == 14
                else:
                    break
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    table = match.player_tables[1]
                    active = table.get_active_charactor()
                    assert active.charge == 1
                    assert len(table.team_status) == 1
                    assert table.team_status[0].name == "I Haven't Lost Yet!"
                    for req in match.requests:
                        assert req.name != 'UseCardRequest'
                elif test_id == 2:
                    table = match.player_tables[1]
                    active = table.get_active_charactor()
                    assert active.charge == 1
                    assert len(table.team_status) == 2
                    assert table.team_status[1].name == "I Haven't Lost Yet!"
                    for req in match.requests:
                        assert req.name != 'UseCardRequest'
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_old_i_havent_lost_yet():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "choose 1",
            "end",
            "skill 1 0 1 2",
            "choose 3",
            "end"
        ],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2",
            "end",
            "choose 1",
            "card 2 0",
            "TEST 1 charge 0 status",
            "card 0 0",
            "skill 3 0 1 2",
            "end"
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        # charactor:Fischl
        # charactor:Mona
        charactor:Nahida*10
        # Gambler's Earrings*2
        # Wine-Stained Tricorne*2
        # Vanarana
        # Timmie*2
        # Rana*2
        # Covenant of Rock
        # Wind and Freedom
        # The Bestest Travel Companion!*2
        # Changing Shifts*2
        # Toss-Up
        # Strategize*2
        # I Haven't Lost Yet!*2
        '''
    )
    old = {'name': 'I Haven\'t Lost Yet!', 'version': '3.3'}
    deck_dict = deck.dict()
    deck_dict['cards'] += [old] * 30
    deck = Deck(**deck_dict)
    for charactor in deck.charactors:
        charactor.hp = 2
        charactor.max_hp = 2
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.charactor_number = 10
    match.config.random_first_player = False
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    table = match.player_tables[1]
                    active = table.get_active_charactor()
                    assert active.charge == 1
                    assert len(table.team_status) == 0
                    use_card_req = 0
                    for req in match.requests:
                        if req.name == 'UseCardRequest':
                            use_card_req += 1
                    assert use_card_req > 0
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_leave_it_to_me():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "card 0 0",
            "card 0 0",
            "TEST 1 status 1",
            "skill 0 0 1 2",
            "TEST 1 status 1",
            "sw_char 0 0",
            "TEST 1 status 1",
            "sw_char 1 0",
            "TEST 2 status 0",
            "sw_char 2 0",
            "TEST 3 opponent ended",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "sw_char 0 0",
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
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        # Gambler's Earrings*2
        # Wine-Stained Tricorne*2
        # Vanarana
        # Timmie*2
        # Rana*2
        # Covenant of Rock
        # Wind and Freedom
        # The Bestest Travel Companion!*2
        # Changing Shifts*2
        # Toss-Up
        # Strategize*2
        # I Haven't Lost Yet!*2
        # Leave It to Me!
        Leave It to Me!*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.random_first_player = False
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            while True:
                test_id = get_test_id_from_command(agent_0)
                if test_id == 1:
                    table = match.player_tables[0]
                    assert len(table.team_status) == 1
                    assert table.team_status[0].name == 'Leave It to Me!'
                elif test_id == 2:
                    table = match.player_tables[0]
                    assert len(table.team_status) == 0
                elif test_id == 3:
                    assert match.player_tables[1].has_round_ended
                else:
                    break
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_claxs_art():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "end",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "TEST 1 no card can use",
            "skill 0 0 1 2",
            "TEST 1 no card can use",
            "sw_char 1 0",
            "TEST 3 card can use",
            "card 0 0 0",
            "TEST 2 0 1",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "card 0 0 0",
            "TEST 2 0 0 2",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "end",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "sw_char 3 0",
            "card 0 0 0",
            "TEST 2 0 0 2 2",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "card 0 0 0",
            "TEST 2 2 0 1 1",
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
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        # charactor:Fischl
        # charactor:Mona
        charactor:Nahida*10
        # Gambler's Earrings*2
        # Wine-Stained Tricorne*2
        # Vanarana
        # Timmie*2
        # Rana*2
        # Covenant of Rock
        # Wind and Freedom
        # The Bestest Travel Companion!*2
        # Changing Shifts*2
        # Toss-Up
        # Strategize*2
        # I Haven't Lost Yet!*2
        # Leave It to Me!
        # Clax's Arts*2
        Clax's Arts*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    match.config.random_first_player = False
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            agent = agent_1
            while True:
                cmd = agent.commands[0]
                test_id = get_test_id_from_command(agent)
                if test_id == 1:
                    for req in match.requests:
                        assert req.name != 'UseCardRequest'
                elif test_id == 2:
                    charges = [int(x) for x in cmd.strip().split()[2:]]
                    for c, cc in zip(match.player_tables[1].charactors,
                                     charges):
                        assert c.charge == cc
                elif test_id == 3:
                    card_req = 0
                    for req in match.requests:
                        if req.name == 'UseCardRequest':
                            card_req += 1
                    assert card_req == len(match.player_tables[1].hands)
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_heavy_strike():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 0 0 0",
            "sw_char 1 0",
            "TEST 1 10 7 10 10 10 10",
            "card 0 0 0",
            "skill 0 0 1 2",
            "TEST 1 10 4 10 7 10 10",
            "TEST 2 p1c0 1 status",
            "TEST 2 p0c0 1 status",
            "end",
            "TEST 2 p1c0 0 status",
            "TEST 2 p0c0 0 status",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "card 0 0 0",
            "card 0 0 0",
            "skill 0 0 1 2",
            "TEST 1 10 7 10 7 10 10",
            "card 0 0 0",
            "skill 1 0 1 2",
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
        charactor:PyroMobMage
        charactor:Arataki Itto
        charactor:Noelle
        Heavy Strike*30
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
                # test 2 p0c0 1 status
                cmd = cmd.split()
                pnum = int(cmd[2][1])
                cnum = int(cmd[2][3])
                count = int(cmd[3])
                assert len(
                    match.player_tables[pnum].charactors[cnum].status
                ) == count
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_heavy_strike_2():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "sw_char 1 0",
            "card 0 0 0",
            "skill 0 0 1 2",
            "TEST 1 10 10 10 9 6 9",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
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
        charactor:ElectroMobMage
        charactor:CryoMobMage
        charactor:Noelle
        Heavy Strike*30
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


def test_friendship_eternal():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "reroll",
            "TEST 1 no card can use",
            "tune 0 0",
            "tune 0 0",
            "TEST 2 card can use",
            "card 0 0 0 1",
            "TEST 3 card number 4 5",
            "tune 0 0",
            "tune 0 3",
            "tune 0 4",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "reroll",
            "TEST 2 can use card",
            "card 0 0 0 1",
            "TEST 2 can use card",
            "card 0 0 2 3",
            "TEST 3 card number 4 4",
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
        charactor:Rhodeia of Loch
        charactor:Nahida
        Friendship Eternal*30
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
                for req in match.requests:
                    assert req.name != 'UseCardRequest'
            elif test_id == 2:
                found = False
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        found = True
                assert found
            elif test_id == 3:
                cmd = cmd.split()
                numbers = [int(cmd[-2]), int(cmd[-1])]
                for table, num in zip(match.player_tables, numbers):
                    assert len(table.hands) == num
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_unseen_razor():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "card 0 1 0 1 2",
            "TEST 1 4 card can use",
            "skill 1 0 1 2",
            "card 1 0",
            "TEST 3 p0c2 no equip",
            "card 0 1 0",
            "skill 0 0 1 2",
            "TEST 2 p0 2+2 usage",
            "card 1 0",
            "end",
            "end",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "TEST 1 0 card can use",
            "end",
            "TEST 4 p0 2 status",
            "end",
            "card 7 1 0 1 2",
            "card 7 1 0 1 2",
            "skill 1 0 1 2",
            "card 0 0",
            "card 6 1 0",
            "skill 1 0 1 2",
            "TEST 2 p1 2+2 usage",
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
        charactor:Barbara
        charactor:Arataki Itto
        charactor:Noelle
        Where Is the Unseen Razor?*15
        The Bell*15
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
                cnum = int(cmd[2])
                counter = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        counter += 1
                assert cnum == counter
            elif test_id == 2:
                cmd = cmd.split()
                pnum = int(cmd[2][1])
                status = match.player_tables[pnum].team_status
                assert len(status) == 2
                for s in status:
                    assert s.usage == 2
            elif test_id == 3:
                assert match.player_tables[0].charactors[2].weapon is None
            elif test_id == 4:
                assert len(match.player_tables[0].team_status) == 2
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_send_off_new_and_old():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 1 no card can use",
            "skill 2 0 1 2 3 4",
            "TEST 1 no card can use",
            "sw_char 1 0",
            "sw_char 0 0",
            "sw_char 1 0",
            "end",
            "card 2 0 0 1",
            "TEST 3 p1 usage 2",
            "end"
        ],
        [
            "sw_card 0 1 2",
            "choose 0",
            "TEST 2 card can use",
            "sw_char 1 0",
            "card 0 0 0 1",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "card 0 0 0 1",
            "TEST 3 p0 usage 0",
            "TEST 0 1 0 1",
            "card 0 0 0 1",
            "TEST 3 p0 usage",
            "end",
            "skill 2 0 1 2 3 4"
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
        charactor:Rhodeia of Loch*3
        Send Off*15
        '''
    )
    # use old version cards
    old = {'name': 'Send Off', 'version': '3.3'}
    deck_dict = deck.dict()
    deck_dict['cards'] += [old] * 15
    deck = Deck(**deck_dict)
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
                for req in match.requests:
                    assert req.name != 'UseCardRequest'
            elif test_id == 2:
                counter = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        counter += 1
                assert counter > 0
            elif test_id == 3:
                cmd = cmd.split()
                pnum = int(cmd[2][1])
                usage = [int(x) for x in cmd[4:]]
                assert len(match.player_tables[pnum].summons) == len(usage)
                for s, u in zip(match.player_tables[pnum].summons, usage):
                    assert s.usage == u
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_plunge_strike():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 2 card target 1 2",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "TEST 2 card target 0 2",
            "card 0 0 0 1 2",
            "sw_char 1 0",
            "TEST 1 7 9 10 7 10 8",
            "sw_char 0 0",
            "TEST 1 5 9 10 7 10 8",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "TEST 3 dice number 9 12",
            "TEST 1 7 10 10 7 10 8",
            "sw_char 1 0",
            "card 0 0 0 1 2",
            "skill 0 0 1"
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
        charactor:Klee
        charactor:Arataki Itto
        charactor:Rhodeia of Loch
        Plunging Strike*30
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
                cnum = [int(x) for x in cmd[4:]]
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert len(req.targets) == len(cnum)
                        for t, c in zip(req.targets, cnum):
                            assert t.charactor_idx == c
            elif test_id == 3:
                assert len(match.player_tables[0].dice.colors) == 9
                assert len(match.player_tables[1].dice.colors) == 12
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    # test_bestest()
    # test_changing_shifts()
    # test_toss_up()
    # test_old_i_havent_lost_yet()
    # test_leave_it_to_me()
    # test_claxs_art()
    # test_heavy_strike_2()
    # test_friendship_eternal()
    # test_unseen_razor()
    test_send_off_new_and_old()
    # test_plunge_strike()
