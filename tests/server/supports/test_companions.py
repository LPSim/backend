from agents.interaction_agent import (
    InteractionAgent_V1_0, InteractionAgent
)
from agents.nothing_agent import NothingAgent
from server.match import Match, MatchState
from server.deck import Deck
from tests.utils_for_test import (
    get_test_id_from_command, set_16_omni, check_hp, make_respond, 
    get_random_state
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
    assert match.start()
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
    assert match.start()
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
                    elif die == 'DENDRO':
                        dendro_num -= 1
                assert omni_num == 0
                assert dendro_num == 0
            elif len(agent_1.commands) == 1:
                # should be 13 omni
                assert len(match.player_tables[1].dice.colors) == 13
                for die in match.player_tables[1].dice.colors:
                    assert die == 'OMNI'
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
    assert match.start()
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
                        if support.name == 'Timmie':
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
                    for support in match.player_tables[1].supports:
                        assert support.name != 'Timmie'
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
        if len(agent_1.commands) == 0:
            break

    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    # test_rana()
    test_timmie()
