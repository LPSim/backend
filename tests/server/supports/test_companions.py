from agents.interaction_agent import InteractionAgent
from agents.nothing_agent import NothingAgent
from server.match import Match, MatchState
from server.deck import Deck
from tests.utils_for_test import (
    set_16_omni, check_hp, make_respond, get_random_state
)


def test_rana():
    """
    first: test one round one time, can use imeediately, only elemental skill
    will trigger, can trigger multiple Rana.
    """
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 0',
            'reroll 1 2 3 4 5 6 7',
            'card 0 omni geo',
            'skill 1 dendro dendro omni',
            'card 0 hydro hydro',
            'tune pyro 0',
            'card 0 dendro dendro',
            'end',
            'reroll 0 1 2 3 4 5 6 7',
            'skill 0 dendro pyro anemo',
            'tune hydro 0',
            'tune hydro 0',
            'skill 2 dendro dendro omni',
            'end',
            'reroll 3 4 5 6 7',
            'skill 1 dendro dendro dendro',
            'card 0 dendro dendro',
            'skill 1 dendro dendro dendro',
            'skill 0 dendro geo anemo'
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
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            if len(agent_1.commands) == 6:
                # should only have two electro dice
                assert len(match.player_tables[1].dice) == 2
                assert match.player_tables[1].dice[0].color == 'ELECTRO'
                assert match.player_tables[1].dice[1].color == 'ELECTRO'
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 3
    check_hp(match, [[83, 10, 10], [99, 10, 10]])
    assert len(match.player_tables[1].dice) == 1
    assert match.player_tables[1].dice[0].color == 'PYRO'
    assert len(match.player_tables[1].supports) == 4
    for support in match.player_tables[1].supports:
        assert support.name == 'Rana'

    assert match.match_state != MatchState.ERROR

    """
    second: next one is other people; cannot generate when only one charactor;
    TODO: if overcharged self, will generate next of next?
    """
    agent_0 = InteractionAgent(
        player_id = 0,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 2',
            'skill 0 omni omni omni',
            'end',
            'skill 0 omni omni omni',
            'end',
        ],
        random_after_no_command = True
    )
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 0',
            'choose 2',
            'card 0 omni omni',
            'card 1 omni omni',
            'skill 1 omni omni omni',
            'sw_char 1 omni',
            'end',
            'choose 2',
            'skill 1 omni omni omni',
            'end',
        ],
        random_after_no_command = True
    )
    match = Match(random_state = get_random_state())
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
    match.match_config.max_same_card_number = 30
    match.match_config.random_first_player = False
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            if len(agent_1.commands) == 4:
                # should be 8 omni and 2 dendro
                assert len(match.player_tables[1].dice) == 10
                omni_num = 8
                dendro_num = 2
                for die in match.player_tables[1].dice:
                    if die.color == 'OMNI':
                        omni_num -= 1
                    elif die.color == 'DENDRO':
                        dendro_num -= 1
                assert omni_num == 0
                assert dendro_num == 0
            elif len(agent_1.commands) == 1:
                # should be 13 omni
                assert len(match.player_tables[1].dice) == 13
                for die in match.player_tables[1].dice:
                    assert die.color == 'OMNI'
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert len(agent_0.commands) == 0
    assert match.round_number == 3
    check_hp(match, [[1, 1, 4], [0, 0, 10]])
    assert len(match.player_tables[1].supports) == 2
    for support in match.player_tables[1].supports:
        assert support.name == 'Rana'

    assert match.match_state != MatchState.ERROR


if __name__ == '__main__':
    test_rana()
