from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_adeptus_temptation():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 1 all card can use 3 target",
            "card 0 0 0 1",
            "skill 0 0 1 2",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "TEST 2 10 10 10 10 10 6",
            "skill 2 0 1 2",
            "TEST 3 status 1 sati, 8 8 0, card target 1 2",
            "end",
            "TEST 4 p0c0 no status, 3 can eat",
            "end",
            "end",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 3 0 1 2",
            "TEST 2 1 8 8 6 2 0",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "end",
            "choose 0",
            "card 0 0 0 1",
            "card 0 0 0 1",
            "TEST 5 cannot eat",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "end",
            "skill 2 0 1 2",
            "TEST 2 2 8 8 6 8 0",
            "end",
            "sw_char 1 0",
            "card 0 1 0 1",
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
        # Clax's Arts*2
        # Adeptus' Temptation*2
        Adeptus' Temptation*30
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
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError('No need respond.')
        # do tests
        while True:
            cmd = agent.commands[0]
            test_id = get_test_id_from_command(agent)
            if test_id == 1:
                count = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        count += 1
                        assert len(req.targets) == 3
                assert count > 0
            elif test_id == 2:
                hps = [int(x) for x in cmd.strip().split()[2:]]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 3:
                check_hp(match, [[10, 10, 10], [8, 8, 0]])
                table = match.player_tables[0]
                assert len(table.charactors[0].status) == 1
                assert table.charactors[0].status[0].name == 'Satiated'
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert len(req.targets) == 2
                        assert req.targets[0].charactor_idx == 1
                        assert req.targets[1].charactor_idx == 2
            elif test_id == 4:
                assert len(match.player_tables[0].charactors[0].status) == 0
                cards = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert len(req.targets) == 3
                        cards += 1
                assert cards > 0
            elif test_id == 5:
                for req in match.requests:
                    assert req.name != 'UseCardRequest'
            else:
                break
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_lotus_flower_crisp():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 1 card can use",
            "card 0 0 1",
            "skill 1 0 1 2",
            "TEST 2 10 10 10 9 10 10",
            "TEST 3 status 1",
            "end",
            "TEST 2 9 10 10 9 10 10",
            "sw_char 1 0",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "card 0 1 0",
            "TEST 4 card target 0 2",
            "skill 1 0 1 2",
            "TEST 2 5 6 10 8 9 7",
            "sw_char 0 0",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "TEST 5 p0c0 2 status",
            "skill 1 0 1 2",
            "card 0 0 0",
            "end",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "skill 3 0 1 2",
            "card 0 0 0",
            "card 0 0 0",
            "card 0 0 0",
            "TEST 6 no card use",
            "end",
            "TEST 2 4 6 10 7 8 5",
            "TEST 7 p1 no c status",
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
        # Clax's Arts*2
        # Adeptus' Temptation*2
        # Lotus Flower Crisp*2
        Lotus Flower Crisp*30
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
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError('No need respond.')
        # do tests
        while True:
            cmd = agent.commands[0]
            test_id = get_test_id_from_command(agent)
            if test_id == 1:
                count = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        count += 1
                        assert len(req.targets) == 3
                assert count > 0
            elif test_id == 2:
                hps = [int(x) for x in cmd.strip().split()[2:]]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 3:
                table = match.player_tables[0]
                assert len(table.charactors[0].status) == 1
                assert table.charactors[0].status[0].name == 'Satiated'
            elif test_id == 4:
                cards = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert len(req.targets) == 2
                        assert req.targets[0].charactor_idx == 0
                        assert req.targets[1].charactor_idx == 2
                        cards += 1
                assert cards > 0
            elif test_id == 5:
                table = match.player_tables[0]
                assert len(table.charactors[0].status) == 2
            elif test_id == 6:
                for req in match.requests:
                    assert req.name != 'UseCardRequest'
            elif test_id == 7:
                table = match.player_tables[1]
                for charactor in table.charactors:
                    assert len(charactor.status) == 0
            else:
                break
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_lotus_flower_crisp_and_reflection():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 1 card can use",
            "card 0 0 1",
            "skill 1 0 1 2",
            "TEST 2 10 10 10 9 10 10",
            "TEST 3 status 1",
            "end",
            "TEST 2 9 10 10 9 10 10",
            "sw_char 1 0",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "card 0 1 0",
            "TEST 4 card target 0 2",
            "skill 1 0 1 2",
            "sw_char 0 0",
        ],
        [
            "sw_card",
            "choose 0",
            "TEST 5 p0c0 2 status",
            "skill 1 0 1 2",
            "card 0 0 0",
            "end",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "skill 0 0 1 2",
            "TEST 6 5 7 10 8 9 7 and reflection remain usage",
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
        # Clax's Arts*2
        # Adeptus' Temptation*2
        # Lotus Flower Crisp*2
        Lotus Flower Crisp*30
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
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError('No need respond.')
        # do tests
        while True:
            cmd = agent.commands[0]
            test_id = get_test_id_from_command(agent)
            if test_id == 1:
                count = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        count += 1
                        assert len(req.targets) == 3
                assert count > 0
            elif test_id == 2:
                hps = [int(x) for x in cmd.strip().split()[2:]]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 3:
                table = match.player_tables[0]
                assert len(table.charactors[0].status) == 1
                assert table.charactors[0].status[0].name == 'Satiated'
            elif test_id == 4:
                cards = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert len(req.targets) == 2
                        assert req.targets[0].charactor_idx == 0
                        assert req.targets[1].charactor_idx == 2
                        cards += 1
                assert cards > 0
            elif test_id == 5:
                table = match.player_tables[0]
                assert len(table.charactors[0].status) == 2
            elif test_id == 6:
                # "TEST 6 5 7 10 8 9 7 and reflection remain usage",
                check_hp(match, [[5, 7, 10], [8, 9, 7]])
                table = match.player_tables[0]
                assert len(table.summons) == 2
                assert table.summons[1].name == 'Reflection'
                assert table.summons[1].usage == 1
            else:
                break
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_mond_hash():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 1 no card can use",
            "sw_char 2 0",
            "TEST 2 card can use one target",
            "card 0 0 0",
            "TEST 1 no use card",
            "TEST 3 10 10 10 10 10 10",
            "end",
        ],
        [
            "sw_card",
            "choose 0",
            "TEST 1 no card can use",
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
        # Clax's Arts*2
        # Adeptus' Temptation*2
        # Lotus Flower Crisp*2
        # Mondstadt Hash Brown*2
        Mondstadt Hash Brown*30
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
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError('No need respond.')
        # do tests
        while True:
            cmd = agent.commands[0]
            test_id = get_test_id_from_command(agent)
            if test_id == 1:
                for req in match.requests:
                    assert req.name != 'UseCardRequest'
            elif test_id == 2:
                count = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        count += 1
                        assert len(req.targets) == 1
                assert count > 0
            elif test_id == 3:
                hps = [int(x) for x in cmd.strip().split()[2:]]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            else:
                break
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_tandoori():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 1 2 card can use",
            "sw_char 2 0",
            "TEST 2 5 card can use",
            "card 0 0 0",
            "card 1 0 0 1",
            "TEST 3 p0c0c1 2 status p0c2 1 no card can use",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "TEST 4 not consumed",
            "TEST 5 10 10 10 10 10 8",
            "skill 1 0 1 2",
            "TEST 5 10 10 10 7 10 8",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "TEST 5 10 8 10 7 10 5",
            "end",
            "TEST 6 p0 only c1 status seed",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "sw_char 0 0",
            "sw_char 2 0",
            "skill 1 0 1 2",
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
        # Clax's Arts*2
        # Adeptus' Temptation*2
        # Lotus Flower Crisp*2
        # Mondstadt Hash Brown*2
        # Tandoori Roast Chicken
        Tandoori Roast Chicken*15
        Mondstadt Hash Brown*15
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
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError('No need respond.')
        # do tests
        while True:
            cmd = agent.commands[0]
            test_id = get_test_id_from_command(agent)
            if test_id == 1:
                count = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        count += 1
                        assert len(req.targets) == 0
                assert count == 2
            elif test_id == 2:
                count = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        count += 1
                assert count == 5
            elif test_id == 3:
                charactors = match.player_tables[0].charactors
                assert len(charactors[0].status) == 2
                assert len(charactors[1].status) == 2
                assert len(charactors[2].status) == 1
                for req in match.requests:
                    assert req.name != 'UseCardRequest'
            elif test_id == 4:
                charactors = match.player_tables[0].charactors
                assert len(charactors[0].status) == 2
                assert len(charactors[1].status) == 2
                assert len(charactors[2].status) == 1
            elif test_id == 5:
                hps = [int(x) for x in cmd.strip().split()[2:]]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 6:
                charactors = match.player_tables[0].charactors
                assert len(charactors[0].status) == 0
                assert len(charactors[1].status) == 1
                assert charactors[1].status[0].name == "Seed of Skandha"
                assert len(charactors[2].status) == 0
            else:
                break
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_pizza():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 2 no card can use",
            "skill 1 0 1 2",
            "end",
            "TEST 3 p1c0 status 2 1",
            "skill 1 0 1 2",
            "end",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "TEST 4 all card can use",
            "card 0 0 0",
            "end",
            "TEST 3 p1c0 status 1",
            "card 0 0 0",
            "end",
            "end",
            "TEST 1 10 10 10 9 10 10",
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
        Mushroom Pizza*30
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
                for req in match.requests:
                    assert req.name != 'UseCardRequest'
            elif test_id == 3:
                cmd = cmd.split()
                status = match.player_tables[1].charactors[0].status
                usages = [int(x) for x in cmd[4:]]
                assert len(usages) == len(status)
                for s, u in zip(status, usages):
                    assert s.usage == u
            elif test_id == 4:
                count = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        count += 1
                assert count == 5
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_full_and_tandoori():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "card 2 0 0",
            "card 0 0 0 1",
            "skill 1 0 1 2",
            "end",
            "card 0 0 0 1",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "TEST 1 10 10 10 7 7 10",
            "end",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "TEST 1 9 10 10 7 10 10",
            "end",
            "sw_char 1 0",
            "card 0 0 0",
            "TEST 1 10 10 10 7 7 10",
            "end",
            "card 7 0 0 1",
            "skill 0 0 1 2",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "TEST 1 9 5 9 7 4 9",
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
        Mushroom Pizza*15
        Tandoori Roast Chicken*15
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


def test_north_chicken():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 1 card can use",
            "TEST 2 skill 0 cost 3",
            "card 0 0",
            "TEST 2 skill 0 cost 2",
            "TEST 2 skill 1 cost 3",
            "sw_char 1 0",
            "TEST 2 skill 0 cost 3",
            "sw_char 0 0",
            "skill 0 0 1",
            "TEST 2 skill 0 cost 3",
            "TEST 3 p0c0 status 1",
            "end",
            "card 0 0",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "end",
            "sw_char 1 0",
            "sw_char 0 0",
            "TEST 2 skill 0 cost 3",
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
        charactor:Mona
        charactor:Nahida
        Northern Smoked Chicken*30
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
                count = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        count += 1
                assert count > 0
            elif test_id == 2:
                cmd = cmd.split()
                sidx = int(cmd[3])
                c = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseSkillRequest':
                        if req.skill_idx == sidx:
                            assert req.cost.total_dice_cost == c
            elif test_id == 3:
                assert len(match.player_tables[0].charactors[0].status) == 1
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_north_chicken_2():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "end",
            "card 0 0 0 1",
            "card 1 0",
            "skill 0 1",
            "sw_char 1 0",
            "sw_char 2 0",
            "sw_char 0 0",
            "TEST 1 p0c0 status 3",
            "skill 0 1",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2",
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
        charactor:Mona
        charactor:Nahida
        Northern Smoked Chicken*15
        Laurel Coronet*15
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
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                assert len(match.player_tables[0].charactors[0].status) == 3
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_adeptus_temptation()
    test_lotus_flower_crisp()
    test_lotus_flower_crisp_and_reflection()
    test_mond_hash()
    test_tandoori()
    test_pizza()
    test_full_and_tandoori()
    test_north_chicken()
