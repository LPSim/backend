
from agents.interaction_agent import InteractionAgent
from agents.nothing_agent import NothingAgent
from server.match import Match, MatchState
from server.deck import Deck
from tests.utils_for_test import (
    get_random_state, get_test_id_from_command, make_respond
)


def test_bestest():
    """
    AA + electro A + talent
    """
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = InteractionAgent(
        player_id = 1,
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
        if len(agent_1.commands) == 0:
            break

    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_bestest()
