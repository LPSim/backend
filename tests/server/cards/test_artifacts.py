from src.lpsim.agents.interaction_agent import (
    InteractionAgent_V1_0, InteractionAgent
)
from src.lpsim.agents.nothing_agent import NothingAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_pidx_cidx, get_test_id_from_command, make_respond, 
    get_random_state, set_16_omni
)
from src.lpsim.server.interaction import UseSkillRequest


def test_small_elemental_artifacts():
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent_V1_0(
        version = '1.0',
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "reroll 1 2 3 4 5 6 7",
            "card 4 0 pyro geo",
            # cost decrease
            "skill 0 dendro hydro",
            # check skill cost after first attack (should no cost decrease)
            "tune hydro 1",
            "card 1 0 dendro dendro",
            # after equip second artifact, can use A but not E 
            # (cost is dendro + any)
            "skill 0 omni omni",
            "end",
            "reroll 0 1 2 3 4 5 6 7",
            "card 0 0 anemo",
            "tune hydro 0",
            # next run after tune, 3 skills are available but only normal 
            # any decrease
            "skill 1 dendro dendro omni",
            "tune pyro 0",
            # after skill 1 and tune, still have 1-1 normal attack
            "card 0 0 electro electro",
            "tune hydro 0",
            "skill 2 dendro dendro",
            "end",
            "reroll",
            "sw_char 1 anemo",
            "sw_char 2 anemo",
            "tune dendro 0",
            "skill 0 electro dendro dendro",
            "tune pyro 0",
            "skill 0 electro cryo cryo",
            "end"
            # 85 10 10 99 10 10
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
                'name': 'Wine-Stained Tricorne',
            }
        ] * 10 + [
            {
                'name': 'Laurel Coronet',
            }
        ] * 10 + [
            {
                'name': 'Strategize',
            }
        ] * 10,
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

            # asserts
            if len(agent_1.commands) == 22:
                # cost decrease
                skills = [x for x in match.requests
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 2
                assert skills[0].cost.elemental_dice_number == 0
                assert skills[0].cost.any_dice_number == 2
                assert skills[1].cost.elemental_dice_number == 2
                assert skills[1].cost.any_dice_number == 0
            elif len(agent_1.commands) == 21:
                # check skill cost after first attack (should no cost decrease)
                skills = [x for x in match.requests
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 2
                assert skills[0].cost.elemental_dice_number == 1
                assert skills[0].cost.any_dice_number == 2
                assert skills[1].cost.elemental_dice_number == 3
                assert skills[1].cost.any_dice_number == 0
            elif len(agent_1.commands) == 19:
                # after equip second artifact, can use A but not E 
                # (cost is dendro + any)
                skills = [x for x in match.requests
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 1
                skill: UseSkillRequest = skills[0]
                assert skill.cost.elemental_dice_number == 1
                assert skill.cost.any_dice_number == 1
            elif len(agent_1.commands) == 14:
                # next run after tune, 3 skills are available but only normal 
                # any decrease
                skills = [x for x in match.requests 
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 3
                skills.sort(key = lambda x: x.skill_idx)
                assert skills[0].cost.elemental_dice_number == 1
                assert skills[0].cost.any_dice_number == 1
                assert skills[1].cost.elemental_dice_number == 3
                assert skills[1].cost.any_dice_number == 0
                assert skills[2].cost.elemental_dice_number == 3
                assert skills[2].cost.any_dice_number == 0
            elif len(agent_1.commands) == 12:
                # after skill 1 and tune, still have 1-1 normal attack
                skills = [x for x in match.requests 
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 1
                skill: UseSkillRequest = skills[0]
                assert skill.cost.elemental_dice_number == 1
                assert skill.cost.any_dice_number == 1

            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 4
    check_hp(match, [[85, 10, 10], [99, 10, 10]])
    assert match.player_tables[1].charactors[0].artifact is not None

    assert match.state != MatchState.ERROR


def test_create_small_element_artifacts():
    deck = Deck.from_str(
        """
        charactor:Nahida*3
        Broken Rime's Echo*4
        Laurel Coronet*4
        Mask of Solitude Basalt*4
        Thunder Summoner's Crown*4
        Viridescent Venerer's Diadem*4
        Wine-Stained Tricorne*4
        Witch's Scorching Hat*4
        Strategize*2
        """
    )
    match = Match()
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 4
    match.config.max_hand_size = 30
    match.config.initial_hand_size = 30
    match.start()
    match.step()

    assert match.state != MatchState.ERROR


def test_old_version_elemental_artifacts():
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "reroll 1 4",
            "TEST 1 all card can use",
            "sw_char 1 4",
            "TEST 1 all card can use",
            "sw_char 2 0",
            "TEST 2 3 card can use, 0 and 4 cannot",
            "end"
        ],
        only_use_command = True
    )
    deck = Deck.from_str(
        '''
        default_version:4.0
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        Wine-Stained Tricorne*12
        Timmie*2
        Rana*2
        Strategize*2
        # Timmie*22
        '''
    )
    old_wine = {'name': 'Wine-Stained Tricorne', 'version': '3.3'}
    deck_dict = deck.dict()
    deck_dict['cards'] += [old_wine] * 12
    deck = Deck(**deck_dict)
    match = Match(random_state = get_random_state())
    match.config.max_same_card_number = 30
    match.set_deck([deck, deck])
    match.start()
    match.step()
    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    counter = 0
                    for request in match.requests:
                        if request.name == 'UseCardRequest':
                            counter += 1
                    assert counter == 5
                elif test_id == 2:
                    counter = []
                    for request in match.requests:
                        if request.name == 'UseCardRequest':
                            counter.append(request.card_idx)
                    assert len(counter) == 3
                    assert 0 not in counter
                    assert 4 not in counter
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0

    assert match.state != MatchState.ERROR


def test_gambler():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "end",
            "choose 1",
            "choose 2",
            "choose 3",
            "choose 4",
            "choose 5",
            "choose 6",
            "skill 0 0 1 2",
            "choose 7",
            "card 0 0 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 9 15",
            "end",
            "skill 0 0 1 2",
            "TEST 1 13 15",
            "card 0 0 0",
            "skill 0 0 1 2",
            "TEST 1 11 15",
            "end",
            "TEST 2 p0c7 usage2",
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
            "card 0 1 1",
            "skill 0 0 1 2",
            "TEST 1 16 12",
            "card 0 0 1",
            "skill 0 0 1 2",
            "TEST 1 16 10",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 16 8",
            "skill 0 0 1 2",
            "TEST 1 16 5",
            "card 0 0 0",
            "skill 0 0 1 2",
            "TEST 1 16 3",
            "card 0 2 0",
            "end",
            "choose 1",
            "skill 0 0 1 2",
            "choose 2",
            "TEST 1 11 15",
            "end",
            "choose 3",
            "choose 4",
            "card 0 0 0",
            "end",
            "choose 5",
            "choose 6",
            "end"
        ],
        only_use_command = True
    )
    deck = Deck.from_str(
        '''
        # charactor:Fischl
        # charactor:Mona
        # charactor:Nahida
        charactor:Nahida*10
        # Gambler's Earrings*2
        # Wine-Stained Tricorne*2
        # Timmie*2
        # Rana*2
        # Strategize*2
        # The Bestest Travel Companion!*2
        # Covenant of Rock
        Gambler's Earrings*30
        '''
    )
    # old_wine = {'name': 'Wine-Stained Tricorne', 'version': '3.3'}
    # deck_dict = deck.dict()
    # deck_dict['cards'] += [old_wine] * 12
    # deck = Deck(**deck_dict)
    for charactor in deck.charactors:
        charactor.hp = 1
        charactor.max_hp = 1
    match = Match(random_state = get_random_state())
    match.config.max_same_card_number = 30
    match.config.charactor_number = 10
    match.config.random_first_player = False
    match.set_deck([deck, deck])
    set_16_omni(match)
    match.start()
    match.step()
    while True:
        if match.need_respond(0):
            while True:
                cmd = agent_0.commands[0]
                test_id = get_test_id_from_command(agent_0)
                if test_id == 1:
                    number = [int(x) for x in cmd.strip().split(' ')[-2:]]
                    assert number[0] == len(match.player_tables[0].dice.colors)
                    assert number[1] == len(match.player_tables[1].dice.colors)
                elif test_id == 2:
                    charactor = match.player_tables[0].charactors[7]
                    assert charactor.artifact is not None
                    assert charactor.artifact.name == "Gambler's Earrings"
                else:
                    break
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                cmd = agent_1.commands[0]
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    number = [int(x) for x in cmd.strip().split(' ')[-2:]]
                    assert number[0] == len(match.player_tables[0].dice.colors)
                    assert number[1] == len(match.player_tables[1].dice.colors)
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_1.commands) == 0 and len(agent_0.commands) == 0

    assert match.state != MatchState.ERROR


def test_old_gambler():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "end",
            "choose 1",
            "choose 2",
            "choose 3",
            "choose 4",
            "choose 5",
            "choose 6",
        ],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "card 0 1 1",
            "skill 0 0 1 2",
            "TEST 1 16 12",
            "card 0 0 1",
            "skill 0 0 1 2",
            "TEST 1 16 10",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 16 8",
            "skill 0 0 1 2",
            "TEST 1 16 7",
            "skill 0 0 1 2",
            "TEST 1 16 6",
            "end",
        ],
        only_use_command = True
    )
    deck = Deck.from_str(
        '''
        # charactor:Fischl
        # charactor:Mona
        # charactor:Nahida
        charactor:Nahida*10
        # Gambler's Earrings*2
        # Wine-Stained Tricorne*2
        # Timmie*2
        # Rana*2
        # Strategize*2
        # The Bestest Travel Companion!*2
        # Covenant of Rock
        # Gambler's Earrings*30
        '''
    )
    old_gambler = {'name': "Gambler's Earrings", 'version': '3.3'}
    deck_dict = deck.dict()
    deck_dict['cards'] += [old_gambler] * 30
    deck = Deck(**deck_dict)
    for charactor in deck.charactors:
        charactor.hp = 1
        charactor.max_hp = 1
    match = Match(random_state = get_random_state())
    match.config.max_same_card_number = 30
    match.config.charactor_number = 10
    match.config.random_first_player = False
    match.set_deck([deck, deck])
    set_16_omni(match)
    match.start()
    match.step()
    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                cmd = agent_1.commands[0]
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    number = [int(x) for x in cmd.strip().split(' ')[-2:]]
                    assert number[0] == len(match.player_tables[0].dice.colors)
                    assert number[1] == len(match.player_tables[1].dice.colors)
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_1.commands) == 0 and len(agent_0.commands) == 0

    assert match.state != MatchState.ERROR


def test_millelith():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 2 0 0 1 2",
            "TEST 3 p0c0 no status",
            "skill 0 0 1 2",
            "TEST 2 dice number 11 13",
            "TEST 1 9 10 10 9 10 10",
            "end",
            "TEST 4 p0c0 p1c1 status",
            "sw_char 1 0",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "TEST 1 7 10 10 9 10 10",
            "TEST 2 dice number 11 11",
            "sw_char 0 0",
            "TEST 2 dice number 11 8",
            "end",
            "TEST 4 p0c0 p1c1 status 2 usage",
            "end",
            "TEST 4 p0c0 p1c1 status 2 usage",
            "end"
        ],
        [
            "sw_card 0 1 2",
            "choose 0",
            "TEST 2 dice number 10 16",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 2 dice number 11 10",
            "TEST 1 8 10 10 9 10 10",
            "sw_char 1 0",
            "card 2 1 0 1",
            "end",
            "sw_char 0 0",
            "sw_char 1 0",
            "TEST 5 p1c1 status 1 usage 1",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
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
        default_version:4.0
        charactor:PyroMobMage
        charactor:ElectroMobMage
        charactor:Noelle
        Tenacity of the Millelith*15
        General's Ancient Helm*15
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
                hps = [int(x) for x in cmd[2:]]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                cmd = cmd.strip().split()
                number = [int(x) for x in cmd[-2:]]
                assert number[0] == len(match.player_tables[0].dice.colors)
                assert number[1] == len(match.player_tables[1].dice.colors)
            elif test_id == 3:
                assert len(match.player_tables[0].charactors[0].status) == 0
            elif test_id == 4:
                assert len(match.player_tables[0].charactors[0].status) == 1
                assert match.player_tables[
                    0].charactors[0].status[0].usage == 2
                assert len(match.player_tables[1].charactors[1].status) == 1
                assert match.player_tables[
                    1].charactors[1].status[0].usage == 2
            elif test_id == 5:
                assert len(match.player_tables[1].charactors[1].status) == 1
                assert match.player_tables[
                    1].charactors[1].status[0].usage == 1
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_instructor():
    cmd_records = [
        [
            "sw_card 2 1 3",
            "choose 1",
            "card 1 0 15 14",
            "card 1 1 13 12",
            "card 1 2 11 10",
            "end",
            "TEST 2 p0 deck 3",
            "TEST 2 p1 deck 3",
            "end",
            "sw_char 0 15",
            "sw_char 2 14",
            "skill 0 13 12 11",
            "sw_char 0 10",
            "end",
            "end",
            "sw_char 2 15",
            "skill 0 14 13 12",
            "skill 0 11 10 9",
            "sw_char 0 8",
            "end",
            "skill 0 15 14 13",
            "skill 0 13 12 11",
            "skill 0 11 10 9",
            "skill 0 9 8 7",
            "card 0 0 6 5",
            "skill 0 4 3 2",
            "skill 2 2 1 0"
        ],
        [
            "sw_card 1 2",
            "choose 1",
            "skill 0 15 14 13",
            "sw_char 0 12",
            "skill 0 11 10 9",
            "sw_char 2 8",
            "skill 0 7 6 5",
            "TEST 3 p0 dice 10",
            "TEST 3 p1 dice 5",
            "sw_char 0 4",
            "end",
            "card 3 0 15 14",
            "skill 0 13 12 11",
            "TEST 3 p1 dice 12",
            "TEST 1 6 4 6 10 10 10",
            "sw_char 1 11",
            "skill 0 10 9 8",
            "sw_char 2 7",
            "skill 0 6 5 4",
            "TEST 3 p1 dice 4",
            "end",
            "end",
            "end",
            "sw_char 1 15",
            "sw_char 0 14",
            "sw_char 1 13",
            "end",
            "sw_char 2 15",
            "sw_char 1 14",
            "sw_char 2 13",
            "TEST 3 p0 dice 10",
            "sw_char 1 12",
            "TEST 3 p0 dice 7",
            "sw_char 2 11",
            "TEST 3 p0 dice 3",
            "sw_char 1 10",
            "choose 2",
            "TEST 3 p0 dice 1",
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
        charactor:AnemoMobMage
        charactor:Barbara
        charactor:Yae Miko
        Instructor's Cap*10
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
                hps = [int(x) for x in cmd[2:]]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                cmd = cmd.strip().split()
                pidx = int(cmd[2][1])
                num = int(cmd[-1])
                assert len(match.player_tables[pidx].table_deck) == num
            elif test_id == 3:
                cmd = cmd.strip().split()
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


def test_lucky_dog():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "skill 0 15 14 13",
            "TEST 1 10 10 10 10 10 10",
            "skill 0 12 11 10",
            "card 0 1 9 8",
            "skill 0 7 6 5",
            "sw_char 0 4",
            "sw_char 1 3",
            "skill 3 2 1 0",
            "end",
            "skill 2 15 14 13 12 11",
            "TEST 1 10 3 10 6 5 6",
            "sw_char 0 10",
            "card 2 0 9 8",
            "skill 1 7 6 5",
            "skill 1 4 3 2"
        ],
        [
            "sw_card",
            "choose 0",
            "card 0 0 15 14",
            "skill 2 13 12 11 10 9",
            "skill 1 8 7 6",
            "sw_char 2 5",
            "sw_char 1 4",
            "skill 0 3 2 1",
            "TEST 1 10 8 10 7 8 9",
            "end",
            "sw_char 0 15",
            "TEST 1 10 3 10 4 5 6",
            "skill 1 14 13 12",
            "sw_char 2 11",
            "skill 0 10 9 8",
            "TEST 1 9 3 10 6 5 6",
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
        charactor:Rhodeia of Loch
        charactor:Ganyu
        charactor:Yae Miko
        Lucky Dog's Silver Circlet*20
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
                hps = [int(x) for x in cmd[2:]]
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


def test_big_elemental_artifacts():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "reroll 4 3",
            "card 1 2 2 1 0",
            "card 1 1 0 1 2",
            "card 1 0 1 0",
            "end",
            "TEST 1 p0 pyro dendro geo",
            "reroll",
            "card 3 1 5 4 3",
            "sw_char 1 4",
            "TEST 2 skill 0 cost 2",
            "skill 0 0 3",
            "end",
            "TEST 1 p0 dendro geo geo",
            "reroll",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "reroll 1 0 4 5",
            "card 2 2 7 6 5",
            "card 2 1 4 3 1",
            "end",
            "TEST 1 p1 electro electro",
            "reroll",
            "card 0 0 7 6 5",
            "end",
            "TEST 1 p1 cryo electro electro",
            "reroll",
            "end"
        ]
    ]
    repeat_times = 20
    for _ in range(repeat_times):
        cmd_records[0] += cmd_records[0][-2:]
        cmd_records[1] += cmd_records[1][-2:]
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
        charactor:Kamisato Ayaka
        charactor:Yae Miko
        Blizzard Strayer*2
        Deepwood Memories*2
        Archaic Petra*2
        Thundering Fury*2
        Viridescent Venerer*2
        Heart of Depth*2
        Crimson Witch of Flames*2
        Blizzard Strayer@3.6*2
        Deepwood Memories@3.6*2
        Archaic Petra@3.6*2
        Thundering Fury@3.6*2
        Viridescent Venerer@3.6*2
        Heart of Depth@3.6*2
        Crimson Witch of Flames@3.6*2
        Blizzard Strayer@3.3*2
        Deepwood Memories@3.3*2
        Archaic Petra@3.3*2
        Thundering Fury@3.3*2
        Viridescent Venerer@3.3*2
        Heart of Depth@3.3*2
        Crimson Witch of Flames@3.3*2
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
                colors = [x.upper() for x in cmd[3:]]
                colors += colors
                for color in match.player_tables[pidx].dice.colors:
                    if color in colors:
                        colors.remove(color)
                assert len(colors) == 0
            elif test_id == 2:
                cmd = cmd.split()
                sid = int(cmd[3])
                cost = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseSkillRequest' and req.skill_idx == sid:
                        assert req.cost.total_dice_cost == cost
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_advanturer_traveling_doctor():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 15 14 13",
            "card 12 0 12",
            "skill 0 11 10 9",
            "skill 0 8 7 6",
            "skill 0 5 4 3",
            "skill 0 2 1 0",
            "end",
            "skill 0 15 14 13",
            "skill 1 12 11 10",
            "TEST 1 24 30 30 27 29 24",
            "skill 2 9 8 7",
            "TEST 1 23 30 30 26 28 22",
            "sw_char 1",
            "skill 1 6 5 4",
            "sw_char 0",
            "skill 0 3 2 1",
            "end",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "skill 0 6 5 4",
            "skill 0 3 2 1",
            "end",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "end",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "TEST 1 25 30 30 0 28 19",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 0 15 14 13",
            "sw_char 1 12",
            "sw_char 2 11",
            "skill 0 10 9 8",
            "TEST 1 28 30 30 26 28 26",
            "sw_char 1 7",
            "skill 0 6 5 4",
            "card 5 2 3",
            "sw_char 2 2",
            "card 9 1",
            "card 1 0",
            "card 3 0",
            "end",
            "skill 1 15 14 13",
            "TEST 1 25 30 30 26 28 23",
            "skill 2 12 11 10",
            "TEST 1 24 30 30 26 28 22",
            "card 13 0 9",
            "skill 2 8 7 6",
            "sw_char 0 5",
            "end",
            "end",
            "end",
            "choose 2",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "skill 2 9 8 7"
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
        charactor:Venti
        charactor:Xiangling
        charactor:Xingqiu
        Sweet Madame*15
        Adventurer's Bandana*5
        Traveling Doctor's Handkerchief*5
        Calx's Arts*5
        '''
    )
    for charactor in deck.charactors:
        charactor.max_hp = 30
        charactor.hp = 30
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    match.config.initial_hand_size = 20
    match.config.max_hand_size = 30
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


def test_emblem_of_severed_fate():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 2 2 15 14",
            "card 10 1 13 12 11",
            "card 10 0 10",
            "skill 0 9 8 7",
            "skill 0 6 5 4",
            "skill 2 3 2 1",
            "end",
            "sw_char 1 15",
            "skill 0 14 13 12",
            "sw_char 0 11",
            "skill 0 10 9 8",
            "sw_char 1 7",
            "end",
            "skill 2 15 14 13 12",
            "card 9 0 11",
            "skill 2 10 9 8 7",
            "TEST 1 19 21 30 30 15 19",
            "sw_char 2 6",
            "TEST 1 19 21 29 30 15 19",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "card 0 0 15 14",
            "card 2 2 13 12",
            "skill 0 11 10 9",
            "skill 0 8 7 6",
            "TEST 1 26 30 30 30 24 30",
            "TEST 2 p0c0 charge 0",
            "TEST 2 p0c1 charge 1",
            "TEST 2 p0c2 charge 1",
            "TEST 2 p1c0 charge 0",
            "TEST 2 p1c1 charge 2",
            "TEST 2 p1c2 charge 0",
            "skill 2 5 4 3 2",
            "end",
            "sw_char 2 15",
            "skill 0 14 13 12",
            "sw_char 1 11",
            "skill 0 10 9 8",
            "sw_char 2 7",
            "end",
            "TEST 1 19 26 30 30 15 26",
            "sw_char 2 15",
            "TEST 1 19 26 30 30 15 19",
            "skill 2 14 13 12",
            "card 3 0 11",
            "skill 2 10 9 8"
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
        charactor:Venti
        charactor:Xiangling
        charactor:Xingqiu@4.0
        Sweet Madame*15
        Ornate Kabuto*5
        Ornate Kabuto@3.7*5
        Emblem of Severed Fate*5
        Emblem of Severed Fate@4.0*5
        Emblem of Severed Fate@3.7*5
        Calx's Arts*5
        '''
    )
    for charactor in deck.charactors:
        charactor.max_hp = 30
        charactor.hp = 30
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    match.config.initial_hand_size = 20
    match.config.max_hand_size = 30
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
                pidx, cidx = get_pidx_cidx(cmd)
                charge = int(cmd[-1])
                assert match.player_tables[pidx].charactors[
                    cidx].charge == charge
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_shadow_of_chiwang():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "sw_char 2 15",
            "sw_char 1 14",
            "sw_char 0 13",
            "card 0 0 12",
            "skill 1 11 10 9",
            "sw_char 1 8",
            "sw_char 2 7",
            "sw_char 1 6",
            "card 1 1 5",
            "skill 1 4 3 2",
            "TEST 1 hands 6 5",
            "end",
            "sw_char 2 15",
            "skill 1 14 13 12",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "sw_char 1 15",
            "card 1 1 14",
            "skill 1 13 12 11",
            "TEST 1 hands 5 5",
            "sw_char 2 10",
            "skill 1 9 8 7",
            "sw_char 1 6",
            "end",
            "TEST 1 hands 8 8",
            "skill 1 15 14 13",
            "sw_char 2 12",
            "skill 1 11 10 9",
            "sw_char 1 8",
            "skill 1 7 6 5",
            "TEST 1 hand 8 9",
            "sw_char 2 4"
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
        charactor:Fischl
        charactor:Mona
        Shadow of the Sand King*30
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
                hlen = [int(cmd[3]), int(cmd[4])]
                assert len(match.player_tables[0].hands) == hlen[0]
                assert len(match.player_tables[1].hands) == hlen[1]
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_millelith_2():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "skill 1 9 8 7",
            "card 4 2 6 5 4",
            "end",
            "choose 1"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "skill 1 9 8 7",
            "skill 0 6 5 4",
            "TEST 1 p0 dice 4",
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
        charactor:Keqing@4.2*3
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
        # do tests
        while True:
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                assert len(match.player_tables[0].dice.colors) == 4
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    # from tests.utils_for_test import enable_logging
    # enable_logging()
    # test_small_elemental_artifacts()
    # test_create_small_element_artifacts()
    # test_old_version_elemental_artifacts()
    # test_gambler()
    # test_old_gambler()
    # test_millelith()
    # test_instructor()
    # test_lucky_dog()
    # test_big_elemental_artifacts()
    # test_advanturer_traveling_doctor()
    # test_emblem_of_severed_fate()
    # test_shadow_of_chiwang()
    test_millelith_2()
