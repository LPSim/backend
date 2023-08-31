
from agents.interaction_agent import InteractionAgent
from agents.nothing_agent import NothingAgent
from server.match import Match, MatchState
from server.deck import Deck
from tests.utils_for_test import (
    get_random_state, get_test_id_from_command, make_respond, set_16_omni
)


def test_bestest():
    """
    AA + electro A + talent
    """
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
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
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_changing_shifts():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 1",
            "card 0 0",
            "card 0 0",
            "TEST 1 status usage 1",
            "skill 0 0 1 2",
            "TEST 1 status 1 usage 1",
            "sw_char 0",
            "TEST 3 status 0",
            "sw_char 1 0",
            "card 0 0",
            "sw_char 0",
            "TEST 4 dice 12",
            "card 0 0",
            "end",
            "TEST 1 status usage 1",
            "end"
        ],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 1",
            "sw_char 0 0",
            "sw_char 1 0",
            "end",
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
        # Covenant of Rock
        # Wind and Freedom
        # The Bestest Travel Companion!*2
        # Changing Shifts*2
        # Strategize*2
        Changing Shifts*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.random_first_player = False
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            while True:
                test_id = get_test_id_from_command(agent_0)
                if test_id == 1:
                    assert len(match.player_tables[0].team_status) == 1
                    assert match.player_tables[0].team_status[0].usage == 1
                elif test_id == 3:
                    assert len(match.player_tables[0].team_status) == 0
                elif test_id == 4:
                    assert len(match.player_tables[0].dice.colors) == 12
                else:
                    break
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_toss_up():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "card 0 0",
            "TEST 2 reroll req 2 time",
            "reroll 0 1 2 3 4 5 6 7",
            "TEST 1 reroll req 1 time",
            "reroll 0 1 2 3 4 5 6 7"
        ],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0"
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
        # Covenant of Rock
        # Wind and Freedom
        # The Bestest Travel Companion!*2
        # Changing Shifts*2
        # Toss-Up
        # Strategize*2
        Toss-Up*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.random_first_player = False
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            while True:
                test_id = get_test_id_from_command(agent_0)
                if test_id == 0:
                    break
                assert len(match.requests) == 1
                req = match.requests[0]
                assert req.name == 'RerollDiceRequest'
                assert req.reroll_times == test_id
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    # test_bestest()
    # test_changing_shifts()
    test_toss_up()
