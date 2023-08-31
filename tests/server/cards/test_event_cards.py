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


def test_i_havent_lost_yet():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "TEST 1 no card can use",
            "skill 0 0 1 2",
            "choose 1",
            "TEST 2 cards can use",
            "end",
            "TEST 1 card cannot use",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "choose 1",
            "TEST 2 card can use",
            "end",
            "TEST 1 no status cannot use card",
            "end",
            "skill 1 0 1 2",
            "choose 3",
            "card 0 0",
            "TEST 3 dice 14",
            "end",
            "sw_char 4 0",
            "choose 3",
            "skill 1 0 1 2",
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
            "skill 1 0 1 2",
            "end",
            "choose 1",
            "card 2 0",
            "TEST 1 charge 1 status cannot use card",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "end",
            "end",
            "choose 1",
            "skill 1 0 1 2",
            "end",
            "skill 3 0 1 2",
            "choose 3",
            "card 0 0",
            "TEST 2",
            "end"
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        # charactor:Fischl
        # charactor:Mona
        charactor:Nahida*10
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
        # I Haven't Lost Yet!*2
        I Haven't Lost Yet!*30
        '''
    )
    for charactor in deck.charactors:
        charactor.hp = 2
        charactor.max_hp = 2
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.charactor_number = 10
    match.config.random_first_player = False
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            while True:
                test_id = get_test_id_from_command(agent_0)
                if test_id == 1:
                    assert len(match.player_tables[0].team_status) == 0
                    for req in match.requests:
                        assert req.name != 'UseCardRequest'
                elif test_id == 2:
                    use_card_req = 0
                    for req in match.requests:
                        if req.name == 'UseCardRequest':
                            use_card_req += 1
                    assert use_card_req > 0
                elif test_id == 3:
                    assert len(match.player_tables[0].dice.colors) == 14
                else:
                    break
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    table = match.player_tables[1]
                    active = table.get_active_charactor()
                    assert active.charge == 1
                    assert len(table.team_status) == 1
                    assert table.team_status[0].name == "I Haven't Lost Yet!"
                    for req in match.requests:
                        assert req.name != 'UseCardRequest'
                elif test_id == 2:
                    table = match.player_tables[1]
                    active = table.get_active_charactor()
                    assert active.charge == 1
                    assert len(table.team_status) == 2
                    assert table.team_status[1].name == "I Haven't Lost Yet!"
                    for req in match.requests:
                        assert req.name != 'UseCardRequest'
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_old_i_havent_lost_yet():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "choose 1",
            "end",
            "skill 1 0 1 2",
            "choose 3",
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
            "skill 1 0 1 2",
            "end",
            "choose 1",
            "card 2 0",
            "TEST 1 charge 0 status",
            "card 0 0",
            "skill 3 0 1 2",
            "end"
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        # charactor:Fischl
        # charactor:Mona
        charactor:Nahida*10
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
        # I Haven't Lost Yet!*2
        '''
    )
    old = {'name': 'I Haven\'t Lost Yet!', 'version': '3.3'}
    deck_dict = deck.dict()
    deck_dict['cards'] += [old] * 30
    deck = Deck(**deck_dict)
    for charactor in deck.charactors:
        charactor.hp = 2
        charactor.max_hp = 2
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.charactor_number = 10
    match.config.random_first_player = False
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    table = match.player_tables[1]
                    active = table.get_active_charactor()
                    assert active.charge == 1
                    assert len(table.team_status) == 0
                    use_card_req = 0
                    for req in match.requests:
                        if req.name == 'UseCardRequest':
                            use_card_req += 1
                    assert use_card_req > 0
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_leave_it_to_me():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "card 0 0",
            "card 0 0",
            "TEST 1 status 1",
            "skill 0 0 1 2",
            "TEST 1 status 1",
            "sw_char 0 0",
            "TEST 1 status 1",
            "sw_char 1 0",
            "TEST 2 status 0",
            "sw_char 2 0",
            "TEST 3 opponent ended",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "sw_char 0 0",
            "sw_char 1 0",
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
        # I Haven't Lost Yet!*2
        # Leave It to Me!
        Leave It to Me!*30
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
                    table = match.player_tables[0]
                    assert len(table.team_status) == 1
                    assert table.team_status[0].name == 'Leave It to Me!'
                elif test_id == 2:
                    table = match.player_tables[0]
                    assert len(table.team_status) == 0
                elif test_id == 3:
                    assert match.player_tables[1].has_round_ended
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


def test_claxs_art():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "end",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "TEST 1 no card can use",
            "skill 0 0 1 2",
            "TEST 1 no card can use",
            "sw_char 1 0",
            "TEST 3 card can use",
            "card 0 0 0",
            "TEST 2 0 1",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "card 0 0 0",
            "TEST 2 0 0 2",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "end",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "sw_char 3 0",
            "card 0 0 0",
            "TEST 2 0 0 2 2",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "card 0 0 0",
            "TEST 2 2 0 1 1",
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
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        # charactor:Fischl
        # charactor:Mona
        charactor:Nahida*10
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
        # I Haven't Lost Yet!*2
        # Leave It to Me!
        # Clax's Arts*2
        Clax's Arts*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.random_first_player = False
    set_16_omni(match)
    match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            agent = agent_1
            while True:
                cmd = agent.commands[0]
                test_id = get_test_id_from_command(agent)
                if test_id == 1:
                    for req in match.requests:
                        assert req.name != 'UseCardRequest'
                elif test_id == 2:
                    charges = [int(x) for x in cmd.strip().split()[2:]]
                    for c, cc in zip(match.player_tables[1].charactors,
                                     charges):
                        assert c.charge == cc
                elif test_id == 3:
                    card_req = 0
                    for req in match.requests:
                        if req.name == 'UseCardRequest':
                            card_req += 1
                    assert card_req == len(match.player_tables[1].hands)
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    # test_bestest()
    # test_changing_shifts()
    # test_toss_up()
    # test_old_i_havent_lost_yet()
    # test_leave_it_to_me()
    test_claxs_art()
