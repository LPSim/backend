import time
import json
import dictdiffer

import pytest
from src.lpsim.server.consts import ObjectType
from src.lpsim.agents.nothing_agent import NothingAgent
from src.lpsim.server.event_handler import OmnipotentGuideEventHandler_3_3
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from src.lpsim.agents.random_agent import RandomAgent
from src.lpsim.agents.interaction_agent import InteractionAgent
from tests.utils_for_test import (
    get_test_id_from_command, set_16_omni, make_respond, remove_ids, 
    get_random_state, check_hp
)


TEST_DECK = {
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
            'name': 'Strategize',
        }
    ] * 30,
}


def test_match_pipeline():
    agent_0 = RandomAgent(player_idx = 0)
    agent_1 = NothingAgent(player_idx = 1)
    match = Match()
    deck = TEST_DECK
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    set_16_omni(match)
    # main.match.event_handlers[0].version = '3.3'
    assert match.start()[0]
    match.step()  # switch card

    while match.round_number < 100 and not match.is_game_end():
        make_respond(agent_0, match, assertion = False)
        make_respond(agent_1, match, assertion = False)

    assert match.state != MatchState.ERROR


def test_save_load():
    """
    use v3.3 Catalyzing Field to test save & load.
    when save on field generated, load should be same. otherwise, load should
    be different only on id.
    """
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 2',
            # 'reroll',
            'skill 0 omni omni omni',
            'sw_char 0 omni',
            'skill 0 omni omni omni',  # quiken activated
            'skill 0 omni omni omni',
            'sw_char 2 omni',
            'skill 0 omni omni omni',  # quiken activated, renew in v3.3
            'end',
            'skill 0 omni omni omni',
            'skill 0 omni omni omni',
            'skill 0 omni omni omni',  # run out of field
        ],
        only_use_command = True
    )
    match = Match()
    deck = TEST_DECK
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    set_16_omni(match)
    match.event_handlers[0].version = '3.3'  # type: ignore
    assert match.start()[0]
    match.step()  # switch card

    saves = {}
    agent_saves = {}

    while True:
        make_respond(agent_0, match, assertion = False)
        make_respond(agent_1, match, assertion = False)
        if len(agent_1.commands) not in saves:
            length = len(agent_1.commands)
            saves[length] = match.copy(deep = True)
            agent_saves[length] = agent_1.copy(deep = True)
        else:
            raise AssertionError()
        if len(agent_1.commands) == 0:
            break

    def check_range(saves, agent_saves, start, end, 
                    same = True, ignore_id = False):
        """
        load start and run until end, then check if they are same.
        if ignore_id, before compare will remove ids from objects.
        """
        match = saves[start].copy(deep = True)
        agent_1 = agent_saves[start].copy(deep = True)
        while True:
            make_respond(agent_0, match, assertion = False)
            make_respond(agent_1, match, assertion = False)
            if len(agent_1.commands) == end:
                break
        saves_end = saves[end]
        if ignore_id:
            match = match.copy(deep = True)
            saves_end = saves_end.copy(deep = True)
            remove_ids(match)
            remove_ids(saves_end)
        is_same = match == saves_end
        assert is_same == same

    # from any position, run reuslts should same
    for _ in range(1, 11):
        check_range(saves, agent_saves, _, 0, same = True, ignore_id = True)
    # generate status, id should not change
    check_range(saves, agent_saves, 8, 7, same = False, ignore_id = False)
    # ignore id, should same
    check_range(saves, agent_saves, 8, 7, same = True, ignore_id = True)
    # renew status, id should not change
    check_range(saves, agent_saves, 6, 4, same = True, ignore_id = False)

    assert len(agent_1.commands) == 0

    assert match.state != MatchState.ERROR


def test_copy_speed():
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "card 1 0 0 1",
            "skill 1 0 1 2",
            "sw_char 1 1",
            "skill 1 omni omni hydro",
            "end",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "skill 2 omni omni dendro omni omni",
            "end",
            "skill 1 0 1 2",
            "card 0 0 0 1 2"
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        """
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        Rana*10
        Wine-Stained Tricorne*10
        The Seed of Stored Knowledge*10
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    set_16_omni(match)
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

    assert match.state != MatchState.ERROR

    run_time = 100
    match = Match()
    deck = TEST_DECK
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    assert match.start()[0]
    starttime = time.time()
    for i in range(run_time):
        _ = match.copy(deep = True)
    endtime = time.time()
    print('not json speed', (endtime - starttime) / run_time)

    match = Match()
    match.config.max_same_card_number = 30
    match.set_deck([deck, deck])
    mainjson = match.json()
    starttime = time.time()
    assert match.start()[0]
    for i in range(run_time):
        mainjson = match.json()
        _ = Match(**json.loads(mainjson))
    endtime = time.time()
    print('json speed', (endtime - starttime) / run_time)
    assert True


def test_random_same_after_load():
    agent_0 = RandomAgent(player_idx = 0, random_seed = 42)
    agent_1 = RandomAgent(player_idx = 1, random_seed = 19260817)
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        default_version:4.0
        charactor:Rhodeia of Loch
        charactor:Kamisato Ayaka
        Traveler's Handy Sword*5
        Gambler's Earrings*5
        Kanten Senmyou Blessing*5
        Sweet Madame*5
        Abyssal Summons*5
        Fatui Conspiracy*5
        '''
    )
    for charactor in deck.charactors:
        charactor.hp = charactor.max_hp = 99
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.max_hand_size = 30
    match.config.initial_hand_size = 10
    match.config.card_number = None
    match.config.charactor_number = None
    match.config.check_deck_restriction = False
    initial_match = match.copy(deep = True)
    initial_agent_0 = agent_0.copy(deep = True)
    initial_agent_1 = agent_1.copy(deep = True)
    results_1 = []
    test_step = 100
    assert match.start()[0]
    match.step()
    for _ in range(test_step):
        make_respond(agent_0, match, assertion = False)
        make_respond(agent_1, match, assertion = False)
        results_1.append(match.copy(deep = True))
    assert match.state != MatchState.ERROR

    # use deepcopy to rerun
    match = initial_match.copy(deep = True)
    agent_0 = initial_agent_0.copy(deep = True)
    agent_1 = initial_agent_1.copy(deep = True)
    assert match.start()[0]
    match.step()
    for i in range(test_step):
        make_respond(agent_0, match, assertion = False)
        make_respond(agent_1, match, assertion = False)
        remove_ids(results_1[i])
        now = match.copy(deep = True)
        remove_ids(now)
        assert now == results_1[i], f'deepcopy error at {i}'
    assert match.state != MatchState.ERROR

    match = Match(**json.loads(initial_match.json()))
    assert match.json() == initial_match.json()
    assert match == initial_match
    # random agent do not support json, use copy instead
    agent_0 = initial_agent_0.copy()
    agent_1 = initial_agent_1.copy()
    assert agent_0 == initial_agent_0
    assert agent_1 == initial_agent_1
    assert match.start()[0]
    match.step()
    for i in range(test_step):
        make_respond(agent_0, match, assertion = False)
        make_respond(agent_1, match, assertion = False)
        remove_ids(results_1[i])
        now = match.copy(deep = True)
        remove_ids(now)
        assert now == results_1[i], f'json error at {i}'
    assert match.state != MatchState.ERROR


def test_save_load_same():
    agent_0 = RandomAgent(player_idx = 0, random_seed = 42)
    agent_1 = RandomAgent(player_idx = 1, random_seed = 19260817)
    match = Match(random_state = get_random_state(100))
    deck = Deck.from_str(
        '''
        default_version:4.0
        charactor:Rhodeia of Loch
        charactor:Kamisato Ayaka
        Traveler's Handy Sword*5
        Gambler's Earrings*5
        Kanten Senmyou Blessing*5
        Sweet Madame*5
        Abyssal Summons*5
        Fatui Conspiracy*5
        Timmie*5
        '''
    )
    for charactor in deck.charactors:
        charactor.hp = charactor.max_hp = 99
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.max_hand_size = 30
    match.config.initial_hand_size = 10
    match.config.card_number = None
    match.config.charactor_number = None
    match.config.check_deck_restriction = False
    test_step = 100
    assert match.start()[0]
    match.step()
    for _ in range(test_step):
        make_respond(agent_0, match, assertion = False)
        make_respond(agent_1, match, assertion = False)
        match_copy = match.copy(deep = True)
        assert remove_ids(match_copy) == remove_ids(
            Match(**json.loads(match_copy.json())))
        match = Match(**json.loads(match.json()))
    assert match.state != MatchState.ERROR


def test_use_card():
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        commands = [
            'sw_card',
            'choose 2',
            'card 0 0 omni',
            'card 0 0 omni',
            'card 0 0 omni',
            'card 0 0 omni',
            'end',
            'card 0 0 omni',
            'card 0 0 omni',
            'card 0 0 omni',
            'card 0 0 omni',
        ]
    )
    match = Match()
    deck = TEST_DECK
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.initial_dice_number = 16
    match.event_handlers = (
        [OmnipotentGuideEventHandler_3_3()] + match.event_handlers
    )
    assert match.start()[0]
    match.step()

    hand_numbers = [10, 10, 10, 10, 10, 9, 8, 7, 6, 5, 5, 5]
    deck_numbers = [7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 25, 25]

    while len(agent_1.commands) > 0:
        if match.need_respond(0):
            current_agent = agent_0
        elif match.need_respond(1):
            current_agent = agent_1
            assert len(match.player_tables[1].hands) == hand_numbers[
                len(agent_1.commands)]
            assert len(match.player_tables[1].table_deck) == deck_numbers[
                len(agent_1.commands)]
        else:
            raise AssertionError('no need respond')
        make_respond(current_agent, match)

    assert match.state != MatchState.ERROR


def test_support_over_maximum_and_error_tests():
    """
    put 6 Ranas and check usages and order.
    """
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 1',
            'card 0 0 omni omni',
            'card 0 0 omni omni',
            'card 0 0 omni omni',
            'end',
            'end',
            'skill 1 omni omni omni',
            'card 0 0 omni electro',
            'card 0 3 electro electro',
            # 4 rana, usage 0 0 0 1
            'card 0 0 omni omni',
            # 4 rana, usage 0 0 1 1
            'skill 1 omni omni omni',
            # dice 7 omni + 2 electro
            'end',
            'skill 1 omni omni omni',
            # 13 omni and 3 electro and 0 usage
            'end',
            'skill 2 omni omni omni',
            # 13 omni, all 1 usage
            'end',
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
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
    set_16_omni(match)
    assert match.start()[0]
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):

            # asserts
            if len(agent_1.commands) == 7:
                # 4 rana, usage 0 0 0 1
                assert len(match.player_tables[1].supports) == 4
                for support, usage in zip(
                        match.player_tables[1].supports, [0, 0, 0, 1]):
                    assert support.name == 'Rana'
                    assert support.usage == usage
            elif len(agent_1.commands) == 6:
                # 4 rana, usage 0 0 1 1
                assert len(match.player_tables[1].supports) == 4
                for support, usage in zip(
                        match.player_tables[1].supports, [0, 0, 1, 1]):
                    assert support.name == 'Rana'
                    assert support.usage == usage
            elif len(agent_1.commands) == 5:
                # dice 7 omni + 2 electro
                assert len(match.player_tables[1].dice.colors) == 9
                omni_counter = 0
                electro_counter = 0
                for d in match.player_tables[1].dice.colors:
                    if d == 'OMNI':
                        omni_counter += 1
                    else:
                        assert d == 'ELECTRO'
                        electro_counter += 1
                assert omni_counter == 7
                assert electro_counter == 2
            elif len(agent_1.commands) == 3:
                # 13 omni and 3 electro and 0 usage
                assert len(match.player_tables[1].dice.colors) == 16
                omni_counter = 0
                electro_counter = 0
                for d in match.player_tables[1].dice.colors:
                    if d == 'OMNI':
                        omni_counter += 1
                    else:
                        assert d == 'ELECTRO'
                        electro_counter += 1
                assert omni_counter == 13
                assert electro_counter == 3
                for support in match.player_tables[1].supports:
                    assert support.name == 'Rana'
                    assert support.usage == 0
            elif len(agent_1.commands) == 1:
                # 13 omni, all 1 usage
                assert len(match.player_tables[1].dice.colors) == 13
                for d in match.player_tables[1].dice.colors:
                    assert d == 'OMNI'
                for support in match.player_tables[1].supports:
                    assert support.name == 'Rana'
                    assert support.usage == 1

            make_respond(agent_1, match)
        else:
            raise AssertionError('no need respond')
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 6
    check_hp(match, [[85, 10, 10], [99, 10, 10]])
    assert len(match.player_tables[1].supports) == 4
    for support in match.player_tables[1].supports:
        assert support.name == 'Rana'

    assert match.state != MatchState.ERROR

    # after start, set deck will raise error
    with pytest.raises(ValueError):
        match.set_deck([deck, deck])
    assert not match.start()[0]


def test_summon_over_maximum():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "skill 2 0 1 2 3 4",
            "skill 2 0 1 2 3 4",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "end",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "skill 2 0 1 2 3 4",
            "skill 2 0 1 2 3 4",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "end",
            "sw_char 0 0",
            "sw_char 2 0",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "skill 2 0 1 2 3 4",
            "TEST 1 frog squi rap oz rap squi oz ref",
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
        charactor:Fischl
        charactor:Rhodeia of Loch
        Send Off*30
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
                summons = cmd[-8:]
                summons = [summons[:4], summons[4:]]
                for table, name in zip(match.player_tables, summons):
                    assert len(table.summons) == 4
                    for s, n in zip(table.summons, name):
                        assert n in s.name.lower()
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_plunge_mark():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 1 p0 true",
            "TEST 1 p1 true",
            "skill 1 0 1 2",
            "TEST 1 p1 true",
            "sw_char 2 0",
            "TEST 1 p1 false",
            "card 0 0 0 1",
            "TEST 1 p0 true",
            "skill 0 0 1 2"
        ],
        [
            "sw_card",
            "choose 0",
            "TEST 1 p0 false",
            "sw_char 1 0",
            "TEST 1 p0 true",
            "skill 1 0 1 2",
            "TEST 1 p0 false",
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
        charactor:Nahida
        charactor:Fischl
        charactor:Rhodeia of Loch
        Send Off*30
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
                b = bool(['false', 'true'].index(cmd[-1].lower()))
                pid = int(cmd[2][1])
                assert match.player_tables[pid].plunge_satisfied == b
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_higher_version_compatible():
    deck = Deck.from_str(
        '''
        default_version:4.0
        charactor:Yoimiya@3.3
        charactor:Yoimiya@3.4
        charactor:Yoimiya@3.5
        charactor:Yoimiya@3.6
        charactor:Yoimiya@3.7
        charactor:Yoimiya@3.8
        charactor:Yoimiya@4.0
        charactor:Yoimiya
        Send Off@3.3
        Send Off@3.4
        Send Off@3.5*1
        Send Off@3.6*1
        Send Off@3.7*1
        Send Off@3.8*1
        Send Off@4.0*1
        Send Off*1
        '''
    )
    res = ['3.3', '3.4', '3.4', '3.4', '3.4', '3.8', '3.8', '3.8']
    res2 = ['3.3', '3.3', '3.3', '3.3', '3.7', '3.7', '3.7', '3.7']
    for c, r in zip(deck.charactors, res):
        assert c.version == r
    for c, r in zip(deck.cards, res2):
        assert c.version == r


def test_save_history():
    agent_0 = RandomAgent(player_idx = 0, random_seed = 42)
    agent_1 = RandomAgent(player_idx = 1, random_seed = 19260817)
    match = Match(random_state = get_random_state(100))
    deck = Deck.from_str(
        '''
        default_version:4.0
        charactor:Rhodeia of Loch
        charactor:Kamisato Ayaka
        Traveler's Handy Sword*5
        Gambler's Earrings*5
        Kanten Senmyou Blessing*5
        Sweet Madame*5
        Abyssal Summons*5
        Fatui Conspiracy*5
        Timmie*5
        '''
    )
    for charactor in deck.charactors:
        charactor.hp = charactor.max_hp = 99
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.max_hand_size = 30
    match.config.initial_hand_size = 10
    match.config.card_number = None
    match.config.charactor_number = None
    match.config.check_deck_restriction = False
    match.config.history_level = 10  # record important history
    test_step = 100
    assert match.start()[0]
    match.step()
    for _ in range(test_step):
        make_respond(agent_0, match, assertion = False)
        make_respond(agent_1, match, assertion = False)
    assert len(match._history) > test_step  # should record history
    match_dict = match._history[0].copy(deep = True).dict()
    starttime = time.time()
    for patch in match._history_diff[1:]:
        match_dict = dictdiffer.patch(patch, match_dict)
    print('patch speed', (time.time() - starttime) / len(match._history_diff))
    assert match._history[-1].dict() == match_dict

    match_dict = match._history[0].copy(deep = True).dict()
    starttime = time.time()
    for patch in match._history_diff[1:]:
        dictdiffer.patch(patch, match_dict, in_place = True)
    print('patch speed in-place', 
          (time.time() - starttime) / len(match._history_diff))
    assert match._history[-1].dict() == match_dict

    # for prev, next, diff in zip(match._history[:-1], match._history[1:],
    #                             match._history_diff[1:]):
    #     assert next.dict() == dictdiffer.patch(diff, prev.dict())
    #     assert next.dict() == Match(**next.dict()).dict()
    #     assert next == Match(**dictdiffer.patch(diff, prev.dict()))
    assert match.state != MatchState.ERROR


def test_save_history_2():
    agent_0 = RandomAgent(player_idx = 0, random_seed = 42)
    agent_1 = RandomAgent(player_idx = 1, random_seed = 19260817)
    match = Match(random_state = get_random_state(100))
    deck = Deck.from_str(
        '''
        default_version:4.0
        charactor:Rhodeia of Loch
        charactor:Kamisato Ayaka
        Toss-Up*10
        Nature and Wisdom*10
        '''
    )
    for charactor in deck.charactors:
        charactor.hp = charactor.max_hp = 1
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.max_hand_size = 30
    match.config.initial_hand_size = 10
    match.config.card_number = None
    match.config.charactor_number = None
    match.config.check_deck_restriction = False
    match.config.history_level = 10  # record important history
    test_step = 10
    assert match.start()[0]
    match.step()
    for _ in range(test_step):
        make_respond(agent_0, match, assertion = False)
        make_respond(agent_1, match, assertion = False)
    assert len(match._history) > test_step  # should record history
    assert match.state != MatchState.ERROR


def test_generate_unused_cards():
    agent_0 = RandomAgent(player_idx = 0, random_seed = 42)
    agent_1 = RandomAgent(player_idx = 1, random_seed = 19260817)
    match = Match(random_state = get_random_state(100))
    deck = Deck.from_str(
        '''
        default_version:4.0
        charactor:AnemoMob
        charactor:PyroMob
        charactor:DendroMob
        charactor:ElectroMob
        charactor:HydroMob
        charactor:CryoMob
        charactor:GeoMob
        Elemental Resonance: Woven Stone
        Skyward Harp
        '''
    )
    for charactor in deck.charactors:
        charactor.hp = charactor.max_hp = 1
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.max_hand_size = 30
    match.config.initial_hand_size = 10
    match.config.card_number = None
    match.config.charactor_number = None
    match.config.check_deck_restriction = False
    match.config.history_level = 10  # record important history
    test_step = 10
    assert match.start()[0]
    match.step()
    for _ in range(test_step):
        make_respond(agent_0, match, assertion = False)
        make_respond(agent_1, match, assertion = False)
    assert len(match._history) > test_step  # should record history
    assert match.state != MatchState.ERROR


def test_prediction():
    """
    3335 + E + talent
    """
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "card 1 0 0 1",
            "skill 1 0 1 2",
            "sw_char 1 1",
            "skill 1 omni omni hydro",
            "end",
            "TEST 1 hp 4 8 8",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "skill 2 omni omni dendro omni omni",
            "TEST 2 hp 0 7 7 and 1 seed for alive",
            "end",
            "TEST 3 hp 0 1 5",
            "skill 1 0 1 2",
            "card 0 0 0 1 2"
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        """
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        Rana*10
        Wine-Stained Tricorne*10
        The Seed of Stored Knowledge*10
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.make_skill_prediction = True
    match.config.history_level = 10
    set_16_omni(match)
    assert match.start()[0]
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    check_hp(match, [[4, 8, 8], [10, 10, 10]])
                elif test_id == 2:
                    check_hp(match, [[0, 7, 7], [10, 10, 10]])
                    for charactor in match.player_tables[0].charactors:
                        if charactor.is_alive:
                            assert len(charactor.status) == 1
                            assert charactor.status[
                                0].name == "Seed of Skandha"
                        else:
                            assert len(charactor.status) == 0
                elif test_id == 3:
                    check_hp(match, [[0, 1, 5], [10, 10, 10]])
                else:
                    break
            prediction_found = None
            prediction_all = None
            if (
                len(agent_1.commands) > 0 
                and agent_1.commands[0][:5] == 'skill'
            ):
                # is skill, check prediction
                prediction_all = match.skill_predictions
                for p in prediction_all:
                    assert p['player_idx'] == 1
                    assert (p['charactor_idx'] 
                            == match.player_tables[1].active_charactor_idx)
                    skill_idx = int(agent_1.commands[0].split()[1])
                    if skill_idx == p['skill_idx']:
                        prediction_found = p
            if prediction_all is not None:
                assert prediction_found is not None
                prediction_found['current_dict'] = match.dict(
                    exclude = {'skill_predictions'}
                )
            make_respond(agent_1, match)
            after_dict = match.dict(exclude = {'skill_predictions'})
            if prediction_found is not None:
                patch_dict = dictdiffer.patch(
                    prediction_found['diff'],
                    prediction_found['current_dict']
                )
                # remove ids, as newly created ids may differ
                patch_match = Match(**patch_dict)
                after_match = Match(**after_dict)
                remove_ids(patch_match)
                remove_ids(after_match)
                for d in (patch_match, after_match):
                    for tb in d.player_tables:
                        # remove dice, as prediction will not use dice
                        tb.dice.colors = []
                        tb.dice.colors = []
                        # as dice number may differ, charge may differ
                        tb.charge_satisfied = False
                    # remove requests, as prediction will not use requests
                    d.requests = []
                    # remove event frames, as it contains ids in some action,
                    # which is hard to remove
                    d.event_frames = []
                assert after_match == patch_match
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 3
    check_hp(match, [[0, 0, 1], [10, 10, 10]])
    assert len(match.player_tables[1].team_status) == 1
    assert match.player_tables[1].team_status[0].name == 'Shrine of Maya'
    assert match.player_tables[1].team_status[0].usage == 3

    assert match.state != MatchState.ERROR


def test_player_table_charactor_order():
    deck_str = '''
    default_version:4.0
    charactor:Fischl
    charactor:Mona
    charactor:Nahida
    Strategize*30
    '''
    deck = Deck.from_str(deck_str)
    match = Match(random_state = get_random_state())
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    assert match.start()[0]
    table = match.player_tables[0].copy(deep = True)
    for active_idx in range(3):
        table.active_charactor_idx = active_idx
        objs = table.get_object_lists()
        result = []
        for obj in objs:
            if obj.type == ObjectType.CHARACTOR:
                result.append(obj.position.charactor_idx)
        if active_idx == 0:
            assert result == [0, 1, 2]
        elif active_idx == 1:
            assert result == [1, 2, 0]
        elif active_idx == 2:
            assert result == [2, 0, 1]
        else:
            raise AssertionError()


if __name__ == '__main__':
    # test_match_pipeline()
    # test_save_load()
    # test_random_same_after_load()
    # test_use_card()
    # test_copy_speed()
    # test_save_load_same()
    # test_support_over_maximum_and_error_tests()
    # test_summon_over_maximum()
    # test_plunge_mark()
    # test_higher_version_compatible()
    # test_save_history()
    # test_generate_unused_cards()
    # test_prediction()
    test_player_table_charactor_order()
