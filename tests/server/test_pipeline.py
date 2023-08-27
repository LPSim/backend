import time
import json
from agents.nothing_agent import NothingAgent
from server.match import Match, MatchState
from server.deck import Deck
from agents.random_agent import RandomAgent
from agents.interaction_agent import InteractionAgent
from tests.utils_for_test import (
    set_16_omni, make_respond, remove_ids, get_random_state, check_hp
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
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = RandomAgent(player_id = 1)
    match = Match()
    deck = TEST_DECK
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    set_16_omni(match)
    # main.match.event_handlers[0].version = '3.3'
    assert match.start()
    match.step()  # switch card

    while match.round_number < 100 and not match.is_game_end():
        make_respond(agent_0, match, assertion = False)
        make_respond(agent_1, match, assertion = False)

    assert match.match_state != MatchState.ERROR


def test_save_load():
    """
    use v3.3 Catalyzing Field to test save & load.
    when save on field generated, load should be same. otherwise, load should
    be different only on id.
    """
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = InteractionAgent(
        player_id = 1,
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
        random_after_no_command = True
    )
    match = Match()
    deck = TEST_DECK
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    set_16_omni(match)
    match.event_handlers[0].version = '3.3'
    assert match.start()
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

    assert match.match_state != MatchState.ERROR


def test_copy_speed():
    run_time = 100
    match = Match()
    deck = TEST_DECK
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    assert match.start()
    starttime = time.time()
    for i in range(run_time):
        _ = match.copy(deep = True)
    endtime = time.time()
    print('not json speed', (endtime - starttime) / run_time)

    match = Match()
    match.match_config.max_same_card_number = 30
    match.set_deck([deck, deck])
    mainjson = match.json()
    starttime = time.time()
    assert match.start()
    for i in range(run_time):
        mainjson = match.json()
        _ = Match(**json.loads(mainjson))
    endtime = time.time()
    print('json speed', (endtime - starttime) / run_time)
    assert True


def test_random_same_after_load():
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = RandomAgent(player_id = 1, random_seed = 19260817)
    match = Match()
    deck = TEST_DECK
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    initial_match = match.copy(deep = True)
    initial_agent_1 = agent_1.copy(deep = True)
    results_1 = []
    test_step = 100
    assert match.start()
    match.step()
    for _ in range(test_step):
        make_respond(agent_0, match, assertion = False)
        make_respond(agent_1, match, assertion = False)
        results_1.append(match.copy(deep = True))
    assert match.match_state != MatchState.ERROR

    # use deepcopy to rerun
    match = initial_match.copy(deep = True)
    agent_1 = initial_agent_1.copy(deep = True)
    assert match.start()
    match.step()
    for i in range(test_step):
        make_respond(agent_0, match, assertion = False)
        make_respond(agent_1, match, assertion = False)
        remove_ids(results_1[i])
        now = match.copy(deep = True)
        remove_ids(now)
        assert now == results_1[i], f'deepcopy error at {i}'
    assert match.match_state != MatchState.ERROR

    # use json to rerun
    match = Match(**json.loads(initial_match.json()))
    assert match.json() == initial_match.json()
    assert match == initial_match
    agent_1 = RandomAgent(**json.loads(initial_agent_1.json()))
    assert agent_1 == initial_agent_1
    assert match.start()
    match.step()
    for i in range(test_step):
        make_respond(agent_0, match, assertion = False)
        make_respond(agent_1, match, assertion = False)
        remove_ids(results_1[i])
        now = match.copy(deep = True)
        remove_ids(now)
        assert now == results_1[i], f'json error at {i}'
    assert match.match_state != MatchState.ERROR


def test_use_card():
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = InteractionAgent(
        player_id = 1,
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
    match.match_config.max_same_card_number = 30
    set_16_omni(match)
    assert match.start()
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
            raise Exception('no need respond')
        make_respond(current_agent, match)

    assert match.match_state != MatchState.ERROR


def test_support_over_maximum():
    """
    put 6 Ranas and check usages and order.
    """
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = InteractionAgent(
        player_id = 1,
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
        random_after_no_command = True
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
    match.match_config.max_same_card_number = 30
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):

            # asserts
            if len(agent_1.commands) == 999:
                ...
            elif len(agent_1.commands) == 7:
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
                assert len(match.player_tables[1].dice) == 9
                omni_counter = 0
                electro_counter = 0
                for d in match.player_tables[1].dice:
                    if d.color == 'OMNI':
                        omni_counter += 1
                    elif d.color == 'ELECTRO':
                        electro_counter += 1
                assert omni_counter == 7
                assert electro_counter == 2
            elif len(agent_1.commands) == 3:
                # 13 omni and 3 electro and 0 usage
                assert len(match.player_tables[1].dice) == 16
                omni_counter = 0
                electro_counter = 0
                for d in match.player_tables[1].dice:
                    if d.color == 'OMNI':
                        omni_counter += 1
                    elif d.color == 'ELECTRO':
                        electro_counter += 1
                assert omni_counter == 13
                assert electro_counter == 3
                for support in match.player_tables[1].supports:
                    assert support.name == 'Rana'
                    assert support.usage == 0
            elif len(agent_1.commands) == 1:
                # 13 omni, all 1 usage
                assert len(match.player_tables[1].dice) == 13
                for d in match.player_tables[1].dice:
                    assert d.color == 'OMNI'
                for support in match.player_tables[1].supports:
                    assert support.name == 'Rana'
                    assert support.usage == 1

            make_respond(agent_1, match)
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 6
    check_hp(match, [[85, 10, 10], [99, 10, 10]])
    assert len(match.player_tables[1].supports) == 4
    for support in match.player_tables[1].supports:
        assert support.name == 'Rana'

    assert match.match_state != MatchState.ERROR


if __name__ == '__main__':
    # test_match_pipeline()
    # test_save_load()
    # test_random_same_after_load()
    # test_use_card()
    test_support_over_maximum()