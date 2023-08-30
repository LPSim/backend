from agents.interaction_agent import InteractionAgent
from server.match import Match, MatchState
from server.deck import Deck
from tests.utils_for_test import (
    get_test_id_from_command, make_respond, 
    get_random_state
)


def test_vanarana():
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
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "end",
            "TEST 1 8 dice and all usage",
            "reroll",
            "TEST 2 16 dice",
            "card 0 0",
            "sw_char 2 0",
            "sw_char 0 0",
            "sw_char 2 0",
            "sw_char 0 0",
            "sw_char 2 0",
            "sw_char 0 0",
            "sw_char 2 0",
            "sw_char 0 0",
            "sw_char 2 0",
            "end",
            "TEST 3 7 dice",
            "reroll",
            "end",
            "reroll",
            "end",
            "TEST 4 ppeeggdd+cccheaoo",
            "reroll",
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
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "end",
            "reroll",
            "sw_char 2 1",
            "sw_char 0 1",
            "sw_char 2 1",
            "sw_char 0 1",
            "sw_char 2 1",
            "sw_char 0 1",
            "sw_char 2 1",
            "sw_char 0 1",
            "sw_char 2 1",
            "sw_char 0 1",
            "sw_char 2 1",
            "sw_char 0 1",
            "sw_char 2 1",
            "sw_char 0 1",
            "sw_char 2 1",
            "end",
            "reroll 0 1 2 3 4 5 6 7",
            "sw_char 0 1",
            "sw_char 2 1",
            "sw_char 0 1",
            "sw_char 2 1",
            "sw_char 0 1",
            "sw_char 2 1",
            "sw_char 0 1",
            "sw_char 2 1",
            "end",
            "reroll 1 2 3 4 5 6 7",
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
        # Strategize*2
        # The Bestest Travel Companion!*2
        # Covenant of Rock
        Vanarana*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.random_first_player = False
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            while True:
                test_id = get_test_id_from_command(agent_0)
                if test_id == 1:
                    current_colors = [
                        match.player_tables[0].dice.colors.copy(),
                        match.player_tables[1].dice.colors.copy()
                    ]
                    assert len(current_colors[0]) == 8
                    assert len(current_colors[1]) == 8
                    assert len(match.player_tables[0].supports) == 4
                    assert len(match.player_tables[1].supports) == 4
                    colors = [
                        ['HYDRO', 'HYDRO'],
                        ['HYDRO', 'HYDRO'],
                        ['GEO', 'GEO'],
                        ['CRYO', 'ANEMO']
                    ]
                    for support, color in zip(
                        match.player_tables[0].supports, colors
                    ):
                        assert support.name == 'Vanarana'
                        assert support.usage == 2
                        assert support.colors == color
                    colors = [
                        ['HYDRO', 'HYDRO'],
                        ['ELECTRO', 'ELECTRO'],
                        ['PYRO', 'DENDRO'],
                        ['ANEMO', 'OMNI']
                    ]
                    for support, color in zip(
                        match.player_tables[1].supports, colors
                    ):
                        assert support.name == 'Vanarana'
                        assert support.usage == 2
                        assert support.colors == color
                elif test_id == 2:
                    assert len(match.player_tables[0].dice.colors) == 16
                    assert len(match.player_tables[1].dice.colors) == 16
                elif test_id == 3:
                    supports = match.player_tables[0].supports
                    assert len(supports) == 4
                    assert supports[3].usage == 1
                    for i in range(3):
                        assert supports[i].usage == 2
                    colors = [
                        ['GEO', 'GEO'],
                        ['DENDRO', 'DENDRO'],
                        ['ELECTRO', 'GEO'],
                        ['ANEMO']
                    ]
                    for support, c in zip(supports, colors):
                        assert support.name == 'Vanarana'
                        assert support.colors == c
                    supports = match.player_tables[1].supports
                    assert len(supports) == 4
                    assert supports[0].usage == 1
                    for i in range(3):
                        assert supports[i + 1].usage == 0
                    colors = [
                        ['OMNI'],
                        [],
                        [],
                        []
                    ]
                    for support, c in zip(supports, colors):
                        assert support.name == 'Vanarana'
                        assert support.colors == c
                elif test_id == 4:
                    supports = (
                        match.player_tables[0].supports
                        + match.player_tables[1].supports
                    )
                    assert len(supports) == 8
                    colors = [
                        ['CRYO', 'CRYO'],
                        ['PYRO', 'PYRO'],
                        ['ELECTRO', 'ELECTRO'],
                        ['GEO', 'GEO'],
                        ['CRYO', 'CRYO'],
                        ['CRYO', 'HYDRO'],
                        ['ELECTRO', 'ANEMO'],
                        ['OMNI', 'OMNI']
                    ]
                    for support, c in zip(supports, colors):
                        assert support.name == 'Vanarana'
                        assert support.colors == c
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


if __name__ == '__main__':
    test_vanarana()
