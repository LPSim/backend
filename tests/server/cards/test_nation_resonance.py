from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.agents.nothing_agent import NothingAgent
from src.lpsim.server.deck import Deck
from src.lpsim.server.match import Match, MatchState
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_wind_and_freedom():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "sw_char 1 0",
            "TEST 1 opposite status",
            "skill 2 0 1 2 3 4",
            "choose 0",
            "card 0 0 0",
            "TEST 11 record opposite command number",
            "skill 1 0 1 2",
            "TEST 2 number -2",
            "card 0 0 0",
            "skill 1 0 1 2",
            "TEST 2 number -3",
            "sw_char 3 0",
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
            "card 0 0 0",
            "card 0 0 0",
            "TEST 1 one team status",
            "skill 0 0 1 2",
            "choose 1",
            "TEST 1 one team status",
            "TEST 11 record opposite command number",
            "skill 1 0 1 2",
            "TEST 2 status none, number -1",
            "sw_char 2 0",
            "TEST 3 number changed",
            "choose 1",
            "choose 3",
            "end"
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        default_version:4.0
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
        # Strategize*2
        Wind and Freedom*30
        '''
    )
    for charactor in deck.charactors:
        charactor.hp = 2
        charactor.max_hp = 2
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.charactor_number = 10
    match.config.check_deck_restriction = False
    match.config.random_first_player = False
    set_16_omni(match)
    match.start()
    match.step()

    cmd_record_0 = 0
    cmd_record_1 = 0
    while True:
        if match.need_respond(0):
            while True:
                cmd = agent_0.commands[0]
                test_id = get_test_id_from_command(agent_0)
                if test_id == 1:
                    assert len(match.player_tables[1].team_status) == 1
                    assert match.player_tables[1].team_status[0].usage == 1
                elif test_id == 11:
                    cmd_record_1 = len(agent_1.commands)
                elif test_id == 2:
                    assert (
                        cmd_record_1 + int(cmd.strip().split()[-1])
                        == len(agent_1.commands)
                    )
                else:
                    break
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                cmd = agent_1.commands[0]
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    assert len(match.player_tables[1].team_status) == 1
                    assert match.player_tables[1].team_status[0].usage == 1
                elif test_id == 11:
                    cmd_record_0 = len(agent_0.commands)
                elif test_id == 2:
                    assert len(match.player_tables[1].team_status) == 0
                    assert (
                        cmd_record_0 + int(cmd.strip().split()[-1])
                        == len(agent_0.commands)
                    )
                elif test_id == 3:
                    assert cmd_record_0 != len(agent_0.commands) + 1
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_wind_and_freedom_one_round():
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "card 0 0 0",
            "card 0 0 0",
            "TEST 1 one team status",
            "end",
            "TEST 2 no status",
            "end"
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        default_version:4.0
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
        # Strategize*2
        Wind and Freedom*30
        '''
    )
    for charactor in deck.charactors:
        charactor.hp = 2
        charactor.max_hp = 2
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.charactor_number = 10
    match.config.check_deck_restriction = False
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
                    assert len(match.player_tables[1].team_status) == 1
                    assert match.player_tables[1].team_status[0].usage == 1
                elif test_id == 2:
                    assert len(match.player_tables[1].team_status) == 0
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_stone_thunder_nature():
    cmd_records = [
        [
            "sw_card 0 2",
            "choose 0",
            "reroll",
            "card 2 0 4",
            "sw_card 2 0",
            "TEST 1 p0 no stone in hand",
            "TEST 1 p1 no stone in hand",
            "TEST 1 p1 no thunder in hand",
            "card 0 0",
            "sw_char 1 6",
            "end",
            "reroll",
            "card 4 0 7",
            "sw_card 0 2 1 3 5",
            "card 4 0 1",
            "sw_card 3 5",
            "TEST 1 p0 no nature card",
            "TEST 1 p0 no thunder card",
            "card 4 0 5 4 3",
            "card 2 0 2 1 0",
            "end",
            "reroll",
            "TEST 2 p0 11 dice",
            "TEST 2 p1 8 dice",
            "end"
        ],
        [
            "sw_card 0 2 3 4",
            "choose 0",
            "reroll",
            "card 1 0 2",
            "sw_card 0 1 2 3",
            "TEST 3 p0 all cryo",
            "card 2 0",
            "TEST 3 p1 all omni",
            "card 2 0 6 5 4",
            "end",
            "reroll",
            "TEST 2 p1 11 dice",
            "TEST 4 p1 no team status",
            "sw_char 1 10",
            "end",
            "reroll"
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
        charactor:Ganyu
        charactor:Fischl
        charactor:Keqing
        Stone and Contracts*7
        Thunder and Eternity*7
        Thunder and Eternity@3.7*7
        Nature and Wisdom*7
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    # check whether random_first_player is enabled.
    match.config.random_first_player = False
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
                pidx = int(cmd[2][1])
                name = cmd[4]
                for card in match.player_tables[pidx].hands:
                    assert name not in card.name.lower()
            elif test_id == 2:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                dnum = int(cmd[3])
                assert len(match.player_tables[pidx].dice.colors) == dnum
            elif test_id == 3:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                color = cmd[4].upper()
                colors = match.player_tables[pidx].dice.colors
                assert colors == [color] * len(colors)
            elif test_id == 4:
                assert len(match.player_tables[1].team_status) == 0
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_fatui_monster():
    cmd_records = [
        [
            "sw_card 1 0",
            "choose 0",
            "end",
            "end",
            "TEST 2 card 1 cannot use",
            "skill 1 15 14 13",
            "card 3 0 12 11",
            "card 7 0 10 9",
            "card 4 0 8 7",
            "TEST 2 card 3 cannot use",
            "card 0 0 6 5",
            "card 1 0 4 3",
            "card 2 0 2 1",
            "end",
            "TEST 1 2 10 10 8 5 4",
            "skill 1 15 14 13",
            "TEST 1 2 10 10 6 5 0",
            "TEST 3 p1c0 status 1",
            "card 0 0 12 11 10 9",
            "TEST 4 no summon",
            "end",
            "skill 0 15 14 13",
            "sw_char 1 12",
            "skill 0 11 10 9",
            "skill 0 8 7 6"
        ],
        [
            "sw_card",
            "choose 0",
            "end",
            "end",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "skill 0 11 10 9",
            "TEST 1 8 10 10 9 6 10",
            "TEST 5 p1 usage 1 1 1 1",
            "sw_char 2 8",
            "skill 0 7 6 5",
            "TEST 1 5 10 10 9 6 10",
            "end",
            "card 4 0 15 14",
            "skill 0 13 12 11",
            "choose 0",
            "end",
            "sw_char 1 15",
            "sw_char 0 14",
            "card 0 0 13 12",
            "card 0 0 11 10",
            "card 0 0 9 8",
            "card 1 0 7 6",
            "TEST 5 p0 usage 1 2 2 2 2",
            "sw_char 1 5",
            "TEST 5 p0 usage 1 1 1 1 1",
            "TEST 1 2 6 7 3 4 0",
            "TEST 3 p0c2 status 1",
            "TEST 2 card 1 cannot use",
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
        charactor:Nahida
        charactor:Klee
        Fatui Conspiracy*10
        Abyssal Summons*10
        Guardian's Oath*10
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
                hps = cmd.strip().split(' ')[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                cmd = cmd.split()
                card_num = int(cmd[3])
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert req.card_idx != card_num
            elif test_id == 3:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                cidx = int(cmd[2][3])
                usages = [int(x) for x in cmd[4:]]
                status = match.player_tables[pidx].charactors[cidx].status
                assert len(status) == len(usages)
                for s, u in zip(status, usages):
                    assert s.usage == u
            elif test_id == 4:
                for table in match.player_tables:
                    assert len(table.summons) == 0
            elif test_id == 5:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                usages = [int(x) for x in cmd[4:]]
                status = match.player_tables[pidx].team_status
                assert len(status) == len(usages)
                for s, u in zip(status, usages):
                    assert s.usage == u
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_wind_and_freedom()
    test_stone_thunder_nature()
    test_fatui_monster()
