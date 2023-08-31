from agents.interaction_agent import InteractionAgent
from server.match import Match, MatchState
from server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_adeptus_temptation():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 1 all card can use 3 target",
            "card 0 0 0 1",
            "skill 0 0 1 2",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "TEST 2 10 10 10 10 10 6",
            "skill 2 0 1 2",
            "TEST 3 status 1 sati, 8 8 0, card target 1 2",
            "end",
            "TEST 4 p0c0 no status, 3 can eat",
            "end",
            "end",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 3 0 1 2",
            "TEST 2 1 8 8 6 2 0",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "end",
            "choose 0",
            "card 0 0 0 1",
            "card 0 0 0 1",
            "TEST 5 cannot eat",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "end",
            "skill 2 0 1 2",
            "TEST 2 2 8 8 6 8 0",
            "end",
            "sw_char 1 0",
            "card 0 1 0 1",
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
        # Clax's Arts*2
        # Adeptus' Temptation*2
        Adeptus' Temptation*30
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
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError('No need respond.')
        # do tests
        while True:
            cmd = agent.commands[0]
            test_id = get_test_id_from_command(agent)
            if test_id == 1:
                count = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        count += 1
                        assert len(req.targets) == 3
                assert count > 0
            elif test_id == 2:
                hps = [int(x) for x in cmd.strip().split()[2:]]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 3:
                check_hp(match, [[10, 10, 10], [8, 8, 0]])
                table = match.player_tables[0]
                assert len(table.charactors[0].status) == 1
                assert table.charactors[0].status[0].name == 'Satiated'
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert len(req.targets) == 2
                        assert req.targets[0].charactor_idx == 1
                        assert req.targets[1].charactor_idx == 2
            elif test_id == 4:
                assert len(match.player_tables[0].charactors[0].status) == 0
                cards = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert len(req.targets) == 3
                        cards += 1
                assert cards > 0
            elif test_id == 5:
                for req in match.requests:
                    assert req.name != 'UseCardRequest'
            else:
                break
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_lotus_flower_crisp():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 1 card can use",
            "card 0 0 1",
            "skill 1 0 1 2",
            "TEST 2 10 10 10 9 10 10",
            "TEST 3 status 1",
            "end",
            "TEST 2 9 10 10 9 10 10",
            "sw_char 1 0",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "card 0 1 0",
            "TEST 4 card target 0 2",
            "skill 1 0 1 2",
            "TEST 2 5 6 10 8 9 7",
            "sw_char 0 0",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "TEST 5 p0c0 2 status",
            "skill 1 0 1 2",
            "card 0 0 0",
            "end",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "skill 3 0 1 2",
            "card 0 0 0",
            "card 0 0 0",
            "card 0 0 0",
            "TEST 6 no card use",
            "end",
            "TEST 2 4 6 10 7 8 5",
            "TEST 7 p1 no c status",
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
        # Clax's Arts*2
        # Adeptus' Temptation*2
        # Lotus Flower Crisp*2
        Lotus Flower Crisp*30
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
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError('No need respond.')
        # do tests
        while True:
            cmd = agent.commands[0]
            test_id = get_test_id_from_command(agent)
            if test_id == 1:
                count = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        count += 1
                        assert len(req.targets) == 3
                assert count > 0
            elif test_id == 2:
                hps = [int(x) for x in cmd.strip().split()[2:]]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 3:
                table = match.player_tables[0]
                assert len(table.charactors[0].status) == 1
                assert table.charactors[0].status[0].name == 'Satiated'
            elif test_id == 4:
                cards = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert len(req.targets) == 2
                        assert req.targets[0].charactor_idx == 0
                        assert req.targets[1].charactor_idx == 2
                        cards += 1
                assert cards > 0
            elif test_id == 5:
                table = match.player_tables[0]
                assert len(table.charactors[0].status) == 2
            elif test_id == 6:
                for req in match.requests:
                    assert req.name != 'UseCardRequest'
            elif test_id == 7:
                table = match.player_tables[1]
                for charactor in table.charactors:
                    assert len(charactor.status) == 0
            else:
                break
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_lotus_flower_crisp_and_reflection():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 1 card can use",
            "card 0 0 1",
            "skill 1 0 1 2",
            "TEST 2 10 10 10 9 10 10",
            "TEST 3 status 1",
            "end",
            "TEST 2 9 10 10 9 10 10",
            "sw_char 1 0",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "card 0 1 0",
            "TEST 4 card target 0 2",
            "skill 1 0 1 2",
            "sw_char 0 0",
        ],
        [
            "sw_card",
            "choose 0",
            "TEST 5 p0c0 2 status",
            "skill 1 0 1 2",
            "card 0 0 0",
            "end",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "skill 0 0 1 2",
            "TEST 6 5 7 10 8 9 7 and reflection remain usage",
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
        # Clax's Arts*2
        # Adeptus' Temptation*2
        # Lotus Flower Crisp*2
        Lotus Flower Crisp*30
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
            agent = agent_0
        elif match.need_respond(1):
            agent = agent_1
        else:
            raise AssertionError('No need respond.')
        # do tests
        while True:
            cmd = agent.commands[0]
            test_id = get_test_id_from_command(agent)
            if test_id == 1:
                count = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        count += 1
                        assert len(req.targets) == 3
                assert count > 0
            elif test_id == 2:
                hps = [int(x) for x in cmd.strip().split()[2:]]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 3:
                table = match.player_tables[0]
                assert len(table.charactors[0].status) == 1
                assert table.charactors[0].status[0].name == 'Satiated'
            elif test_id == 4:
                cards = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert len(req.targets) == 2
                        assert req.targets[0].charactor_idx == 0
                        assert req.targets[1].charactor_idx == 2
                        cards += 1
                assert cards > 0
            elif test_id == 5:
                table = match.player_tables[0]
                assert len(table.charactors[0].status) == 2
            elif test_id == 6:
                # "TEST 6 5 7 10 8 9 7 and reflection remain usage",
                check_hp(match, [[5, 7, 10], [8, 9, 7]])
                table = match.player_tables[0]
                assert len(table.summons) == 2
                assert table.summons[1].name == 'Reflection'
                assert table.summons[1].usage == 1
            else:
                break
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    # test_adeptus_temptation()
    test_lotus_flower_crisp()
    test_lotus_flower_crisp_and_reflection()
