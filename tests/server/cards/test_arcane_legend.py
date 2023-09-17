
from src.lpsim.server.deck import Deck
from src.lpsim.server.interaction import UseCardResponse
from src.lpsim.server.match import Match, MatchState

from tests.utils_for_test import (
    get_random_state, get_test_id_from_command, make_respond
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
    assert match.start()
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
    assert match.start()
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
        assert match.start()
        match.step()
        for table in match.player_tables:
            first_three = table.hands[:3]
            for card in first_three:
                assert card.name == 'Covenant of Rock'


if __name__ == '__main__':
    # test_covenant_of_rock()
    test_rock_dice_different_not_omni()
    # test_arcane_card_always_in_hand()
