from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_seelie():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "card 0 0 0",
            "skill 1 0 1 2",
            "skill 0 0 1 2",
            "end",
            "skill 0 0 1 2",
            "TEST 2 card number 9 10",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "card 0 0 0",
            "card 0 0 0",
            "skill 1 0 1 2",
            "TEST 1 all support usage 1",
            "skill 1 0 1 2",
            "end",
            "sw_char 0 0",
            "TEST 3 card number 9 5",
            "skill 0 0 1 2"
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
        charactor:Noelle*3
        Treasure-Seeking Seelie*30
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
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                num = [1, 2]
                for table, n in zip(match.player_tables, num):
                    assert n == len(table.supports)
                    for support in table.supports:
                        assert support.usage == 1
            elif test_id == 2:
                assert len(match.player_tables[0].hands) == 9
                assert len(match.player_tables[1].hands) == 10
            elif test_id == 3:
                assert len(match.player_tables[0].hands) == 9
                assert len(match.player_tables[1].hands) == 5
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_NRE():
    cmd_records = [
        [
            "sw_card 1",
            "choose 0",
            "skill 1 15 14 13 12 11",
            "card 0 0 10 9",
            "card 3 0",
            "sw_char 1 8",
            "end",
            "card 4 0",
            "TEST 1 p0 support usage 0",
            "TEST 2 p0 card 7",
            "end"
        ],
        [
            "sw_card 1 3",
            "choose 0",
            "sw_char 1 15",
            "sw_char 2 14",
            "card 1 2",
            "TEST 2 p1 hand 4",
            "card 0 0 13 12",
            "TEST 2 p1 card 4",
            "card 0 0 11 10",
            "TEST 2 p1 card 4",
            "card 0 0 9 8",
            "TEST 2 p1 card 4",
            "TEST 1 p1 support usage 0 0",
            "skill 1 7 6 5",
            "TEST 2 p0 card 5",
            "end",
            "card 3 0 15 14",
            "TEST 2 p0 card 7",
            "TEST 2 p1 card 6",
            "TEST 1 p1 support usage 0 0",
            "TEST 1 p0 support usage 1",
            "end",
            "card 5 0 15 14",
            "card 4 0 13 12",
            "TEST 2 p1 card 6",
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
        charactor:Electro Hypostasis
        charactor:Klee
        charactor:Keqing
        NRE*15
        Sweet Madame*2
        Mushroom Pizza*2
        Tandoori Roast Chicken*2
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
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                usage = [int(x) for x in cmd[5:]]
                supports = match.player_tables[pidx].supports
                assert len(usage) == len(supports)
                for u, s in zip(usage, supports):
                    assert u == s.usage
            elif test_id == 2:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                cardnum = int(cmd[4])
                assert len(match.player_tables[pidx].hands) == cardnum
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_parametric():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 0 0 15 14",
            "skill 1 13 12 11",
            "TEST 1 p0 support 1",
            "TEST 1 p1 support 0",
            "sw_char 2 10",
            "skill 0 9 8 7",
            "skill 2 6 5 4 3 2",
            "end",
            "skill 0 15 14 13",
            "TEST 2 p1 dice 13",
            "card 0 0 12 11",
            "card 0 0 10 9",
            "card 0 0 8 7",
            "skill 1 6 5 4",
            "skill 1 3 2 1",
            "end",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "TEST 1 p0 support 1",
            "card 2 0 15 14",
            "skill 1 13 12 11",
            "TEST 1 p0 support 1",
            "TEST 1 p1 support 0",
            "sw_char 0 10",
            "TEST 1 p0 support 2",
            "TEST 1 p1 support 1",
            "end",
            "TEST 1 p0 support 2",
            "TEST 1 p1 support 1",
            "skill 0 15 14 13",
            "skill 1 12 11 10",
            "skill 1 9 8 7",
            "TEST 2 p0 dice 10",
            "end",
            "sw_char 3 0",
            "card 0 0 0 1",
            "skill 1 0 1 2",
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
        charactor:Mona
        charactor:Xiangling
        charactor:Ganyu
        charactor:Barbara
        Parametric Transformer*30
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
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                usages = [int(x) for x in cmd[4:]]
                supports = match.player_tables[pidx].supports
                assert len(supports) == len(usages)
                for u, s in zip(usages, supports):
                    assert u == s.usage
            elif test_id == 2:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                num = int(cmd[-1])
                assert len(match.player_tables[pidx].dice.colors) == num
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_seelie()
    test_NRE()
    test_parametric()
