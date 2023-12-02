
from src.lpsim.server.deck import Deck
from src.lpsim.server.interaction import UseCardResponse
from src.lpsim.server.match import Match, MatchState

from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)
from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.agents.nothing_agent import NothingAgent


def test_covenant_of_rock():
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "reroll",
            "TEST 1 no card can use",
            "sw_char 1 0",
            "tune 0 6",
            "skill 0 0 1 2",
            "tune 0 1",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "TEST 2 can use 3 card",
            "card 0 0",
            "TEST 3 dice 2 not same no omni",
            "sw_char 1 0",
            "sw_char 0 0",
            "TEST 1 no card can use",
            "end",
            "reroll",
            "TEST 1 no card can use",
            "TEST 4 table arcane still false",
            "sw_char 1 1"
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        """
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        # Wine-Stained Tricorne*2
        # Timmie*2
        # Rana*2
        # Strategize*2
        # The Bestest Travel Companion!*2
        # Covenant of Rock
        Covenant of Rock*30
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    assert match.start()[0]
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    for request in match.requests:
                        assert request.name != 'UseCardRequest'
                elif test_id == 2:
                    card_req = 0
                    for request in match.requests:
                        if request.name == 'UseCardRequest':
                            card_req += 1
                    assert card_req == 3
                elif test_id == 3:
                    colors = match.player_tables[1].dice.colors.copy()
                    colorset = set(colors)
                    assert len(colors) == len(colorset)
                    assert len(colors) == 2
                    for color in colors:
                        assert color != 'OMNI'
                elif test_id == 4:
                    assert not match.player_tables[1].arcane_legend
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_rock_dice_different_not_omni():
    """
    stop in using card, and set random random_state, then use card again
    to check always different and not omni
    """
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "reroll",
            "sw_char 1 0",
            "tune 0 6",
            "skill 0 0 1 2",
            "tune 0 1",
            "skill 0 0 1 2",
            "sw_char 2 0",
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        """
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        # Wine-Stained Tricorne*2
        # Timmie*2
        # Rana*2
        # Strategize*2
        # The Bestest Travel Companion!*2
        # Covenant of Rock
        Covenant of Rock*30
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    assert match.start()[0]
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break
    match.step()

    assert match.state != MatchState.ERROR
    assert match.need_respond(1)
    card_req = None
    for req in match.requests:
        if req.name == 'UseCardRequest':
            card_req = req
    assert card_req is not None
    card_resp = UseCardResponse(
        request = card_req,
        dice_idxs = [],
        target = None
    )
    match_bk = match.copy(deep = True)
    for _ in range(50):
        match = match_bk.copy(deep = True)
        match_new = Match()
        match.random_state = match_new.random_state
        match._init_random_state()
        match.respond(card_resp)
        match.step()
        colors = match.player_tables[1].dice.colors.copy()
        colorset = set(colors)
        assert len(colors) == len(colorset)
        for color in colors:
            assert color != 'OMNI'
        assert len(colors) == 2


def test_arcane_card_always_in_hand():
    """
    when 3 arcane card, they should always be the first three
    """
    deck = Deck.from_str(
        """
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        # Wine-Stained Tricorne*2
        # Timmie*2
        # Rana*2
        # Strategize*2
        # The Bestest Travel Companion!*2
        # Covenant of Rock
        Covenant of Rock*3
        Strategize*27
        """
    )
    for i in range(50):
        match = Match()
        match.set_deck([deck, deck])
        match.config.max_same_card_number = 30
        assert match.start()[0]
        match.step()
        for table in match.player_tables:
            first_three = table.hands[:3]
            for card in first_three:
                assert card.name == 'Covenant of Rock'


def test_ancient_courtyard():
    cmd_records = [
        [
            "sw_card 0 1 2 3",
            "choose 1",
            "reroll",
            "TEST 1 card 0 cannot use",
            "card 1 0 1 0",
            "TEST 2 card 0 can use",
            "card 1 0",
            "TEST 1 card 0 cannot use",
            "card 1 0",
            "sw_char 2 5",
            "end",
            "reroll",
            "end",
            "reroll",
            "end",
            "reroll",
            "card 0 0",
            "sw_char 1 7",
            "card 5 1",
            "TEST 3 p0 no team status",
            "end"
        ],
        [
            "sw_card 0 1 2 3",
            "choose 0",
            "reroll",
            "TEST 1 card 0 cannot use",
            "card 1 2 3",
            "TEST 2 card 0 can use",
            "card 1 1 6 5",
            "card 1 0",
            "card 0 0",
            "card 0 1",
            "card 0 0",
            "skill 0 0 4 2",
            "end",
            "reroll",
            "end",
            "reroll",
            "end",
            "reroll",
            "TEST 4 card 5 cost 2",
            "TEST 4 card 1 cost 1",
            "card 1 1 4",
            "card 4 2 6 5",
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
        charactor:Mona
        charactor:Nahida
        charactor:Klee
        Ancient Courtyard*10
        Where Is the Unseen Razor?*10
        Gambler's Earrings*10
        Magic Guide*10
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
                # a sample of HP check based on the command string.
                cmd = cmd.split()
                cardnum = int(cmd[3])
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert req.card_idx != cardnum
            elif test_id == 2:
                cmd = cmd.split()
                cardnum = int(cmd[3])
                found = False
                for req in match.requests:
                    if (
                        req.name == 'UseCardRequest' 
                        and req.card_idx == cardnum
                    ):
                        found = True
                assert found
            elif test_id == 3:
                assert len(match.player_tables[0].team_status) == 0
            elif test_id == 4:
                cmd = cmd.split()
                cardnum = int(cmd[3])
                costnum = int(cmd[5])
                for req in match.requests:
                    if (
                        req.name == 'UseCardRequest' 
                        and req.card_idx == cardnum
                    ):
                        assert req.cost.total_dice_cost == costnum
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_joyous():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "TEST 1 card 0 can use",
            "sw_char 3 12",
            "TEST 2 card 0 cannot use",
            "sw_char 4 11",
            "TEST 2 card 0 cannot use",
            "sw_char 1 10",
            "sw_char 2 9",
            "skill 0 8 7 6",
            "sw_char 3 5",
            "end",
            "sw_char 0 15",
            "sw_char 2 14",
            "card 0 0 0",
            "TEST 3 p1 summon usage 1",
            "TEST 4 p0c0 pyro",
            "TEST 4 p0c4 pyro",
            "TEST 4 p0c1 none",
            "TEST 4 p0c2 none",
            "TEST 4 p0c3 none",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "card 0 0 0",
            "TEST 5 p0 team dendro core",
            "TEST 6 p1 all dendro except 2",
            "skill 0 1 10 9",
            "sw_char 0 1",
            "skill 1 1 6 5",
            "end",
            "skill 0 15 14 13",
            "sw_char 2 12",
            "skill 0 11 10"
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
        charactor:Mona
        charactor:Nahida
        charactor:Klee
        charactor:Noelle
        charactor:Venti
        Joyous Celebration
        Where Is the Unseen Razor?*10
        Gambler's Earrings*10
        Magic Guide*10
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
                found = False
                for req in match.requests:
                    if req.name == 'UseCardRequest' and req.card_idx == 0:
                        found = True
                assert found
            elif test_id == 2:
                cmd = cmd.split()
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert req.card_idx != 0
            elif test_id == 3:
                assert len(match.player_tables[1].summons) == 1
                assert match.player_tables[1].summons[0].usage == 1
            elif test_id == 4:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                cidx = int(cmd[2][3])
                charactor = match.player_tables[pidx].charactors[cidx]
                if cmd[3] == 'none':
                    assert charactor.element_application == []
                else:
                    assert charactor.element_application == [cmd[3].upper()]
            elif test_id == 5:
                team_status = match.player_tables[0].team_status
                assert len(team_status) == 1
                assert team_status[0].name == 'Dendro Core'
            elif test_id == 6:
                charactors = match.player_tables[1].charactors
                for cid, c in enumerate(charactors):
                    if cid == 2:
                        assert c.element_application == []
                    else:
                        assert c.element_application == ['DENDRO']
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_joyous_2():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "sw_char 2 12",
            "skill 1 11 10 9",
            "skill 1 8 7 6",
            "skill 0 5 4"
        ],
        [
            "sw_card",
            "choose 2",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "skill 0 9 8",
            "choose 0",
            "card 0 0 0",
            "TEST 6 p1 all hydro except 2",
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
        charactor:Mona
        charactor:Nahida
        charactor:Klee
        charactor:Noelle
        charactor:Venti
        Joyous Celebration
        Where Is the Unseen Razor?*10
        Gambler's Earrings*10
        Magic Guide*10
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
            elif test_id == 6:
                charactors = match.player_tables[1].charactors
                for cid, c in enumerate(charactors):
                    if cid == 2:
                        assert c.element_application == []
                    else:
                        assert c.element_application == ['HYDRO']
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_fresh_wind_of_freedom():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "end",
            "skill 0 15 14 13",
            "choose 2",
            "TEST 1 0 10 8 10 10 4",
            "end",
            "card 3 0",
            "skill 0 15 14 13",
            "choose 1",
            "TEST 1 0 10 0 8 10 4",
            "skill 1 12 11 10",
            "TEST 1 0 8 0 5 10 4",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "skill 2 9 8 7 6",
            "skill 0 5 4 3",
            "end",
            "card 2 0",
            "sw_char 1 15",
            "sw_char 0 14",
            "skill 0 13 12 11",
            "skill 0 10 9 8",
            "skill 0 7 6 5",
            "end",
            "skill 0 15 14 13",
            "sw_char 1 12"
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
        Fresh Wind of Freedom*10
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


def test_arcaneguoba_hairan_fenglong_lyresong():
    cmd_records = [
        [
            "sw_card 1 2",
            "choose 0",
            "skill 1 15 14 13",
            "TEST 1 7 8 8 10 10 10",
            "card 0 0",
            "sw_char 1 12",
            "card 2 1 11 10 9",
            "card 0 0 8 7",
            "card 1 0 6 5",
            "TEST 2 skill 2 cost 3",
            "TEST 3 card 1 cost 1",
            "TEST 4 p0 hand 4",
            "card 1 0 4",
            "sw_char 1 3",
            "skill 0 2 1 0",
            "TEST 1 7 10 8 10 5 10",
            "end",
            "TEST 1 7 7 8 10 10 10",
            "sw_char 0 15",
            "card 0 0",
            "card 4 0 14",
            "skill 0 13 12 11",
            "TEST 1 7 4 5 10 10 6",
            "card 0 0",
            "card 3 1 10",
            "sw_char 1 9",
            "end",
            "sw_char 0 15",
            "TEST 5 p1 support",
            "skill 2 14 13",
            "sw_char 2 12",
            "end",
            "card 0 0 15 14 13",
            "TEST 5 p0 support",
            "TEST 1 4 7 5 8 6 7",
            "end"
        ],
        [
            "sw_card 2 3 4",
            "choose 2",
            "TEST 1 10 10 10 10 10 7",
            "card 4 2 15 14 13",
            "card 1 0 12 11",
            "TEST 2 skill 2 cost 4",
            "TEST 3 card 3 cost 4",
            "card 3 0 10 9 8 7",
            "sw_char 1 6",
            "TEST 2 skill 2 cost 5",
            "end",
            "card 4 1 15 14 13",
            "card 1 0",
            "card 3 1 12",
            "skill 2 11 10 9 8",
            "sw_char 2 7",
            "skill 2 6 5 4 3 2",
            "sw_char 1 1",
            "end",
            "skill 2 15 14 13 12",
            "card 2 1",
            "card 4 2 11",
            "card 3 0",
            "card 2 1 10",
            "sw_char 0 9",
            "end",
            "card 1 1",
            "card 4 2 15",
            "card 3 0 14 13 12",
            "card 2 0 11 10",
            "end",
            "card 0 0",
            "TEST 4 p1 hand 7",
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
        charactor:Keqing
        charactor:Nahida
        charactor:Ganyu
        Lyresong
        Stormterror's Lair*10
        Ocean-Hued Clam*10
        Lyresong*9
        In Every House a Stove
        Undivided Heart
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
                sidx = int(cmd[3])
                cost = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseSkillRequest' and req.skill_idx == sidx:
                        assert req.cost.total_dice_cost == cost
            elif test_id == 3:
                cidx = int(cmd[3])
                cost = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseCardRequest' and req.card_idx == cidx:
                        assert req.cost.total_dice_cost == cost
            elif test_id == 4:
                pidx = int(cmd[2][1])
                hnum = int(cmd[4])
                assert len(match.player_tables[pidx].hands) == hnum
            elif test_id == 5:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].supports) == 0
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    # test_covenant_of_rock()
    test_rock_dice_different_not_omni()
    # test_arcane_card_always_in_hand()
    test_ancient_courtyard()
    test_joyous()
    test_fresh_wind_of_freedom()
    test_arcaneguoba_hairan_fenglong_lyresong()
