from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.agents.nothing_agent import NothingAgent
from src.lpsim.server.deck import Deck
from src.lpsim.server.match import Match, MatchState
from tests.utils_for_test import (
    get_random_state, get_test_id_from_command, make_respond, set_16_omni
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


def test_stone_hunder_nature():
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


if __name__ == '__main__':
    test_wind_and_freedom()
    test_stone_hunder_nature()
