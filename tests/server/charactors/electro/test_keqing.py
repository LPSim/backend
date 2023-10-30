from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_keqing():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "end",
            "skill 0 0 1 2",
            "card 0 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 20 20 20 14 20 13",
            "card 6 0 0 1 2",
            "skill 2 0 1 2 3",
            "TEST 1 20 20 20 11 17 5",
            "end",
            "end",
            "sw_char 1 0",
            "end",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "TEST 1 6 3 18 11 15 5",
            "TEST 3 p1c1 ele app",
            "skill 1 0 1 2",
            "TEST 1 6 3 18 11 12 5",
            "TEST 4 hand 10 10",
            "skill 1 0 1 2",
            "TEST 2 p0c0 status usage",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "end",
            "sw_char 2 0",
            "TEST 1 20 20 20 14 20 18",
            "TEST 3 p1c2 ele application electro",
            "end",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "card 0 0 0 1 2",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "end",
            "skill 0 0 1 2",
            "skill 2 0 1 2 3",
            "card 8 0 0 1 2",
            "TEST 1 7 10 19 11 17 5",
            "TEST 3 p0c1 ele app",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "end",
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
        charactor:Keqing
        charactor:Kaeya
        charactor:Fischl
        Thundering Penance*30
        '''
    )
    for charactor in deck.charactors:
        charactor.hp = 20
        charactor.max_hp = 20
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
                pid = int(cmd[2][1])
                cid = int(cmd[2][3])
                usage = [int(x) for x in cmd[5:]]
                status = match.player_tables[pid].charactors[cid].status
                assert len(status) == len(usage)
            elif test_id == 3:
                cmd = cmd.split()
                pid = int(cmd[2][1])
                cid = int(cmd[2][3])
                app = [x.upper() for x in cmd[5:]]
                charactor = match.player_tables[pid].charactors[cid]
                assert charactor.element_application == app
            elif test_id == 4:
                hand = [int(x) for x in cmd.split()[3:]]
                assert len(hand) == 2
                for table, h in zip(match.player_tables, hand):
                    assert len(table.hands) == h
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_keqing_2():
    """
    This test mainly tests the following:
        1. when hands have multiple Lightning Stiletto, use skill will remove
            all of them (to get multiple Lightning Stiletto, use Nature and 
            Wisdom to put them into deck)
        2. Artifacts can decrease the cost of Lightning Stiletto, even if
            Keqing is not active charactor
        3. When Keqing defeated, all Lightning Stiletto cannot use.
    """
    cmd_records = [
        [
            "sw_card 1 3",
            "choose 1",
            "card 0 1 15 14",
            "skill 1 13 12",
            "sw_char 0 11",
            "end",
            "card 4 0 15 14",
            "sw_char 2 13",
            "card 3 0 12",
            "sw_card 0 1 2 4 5 3",
            "sw_char 1 11",
            "skill 1 10 9 8",
            "card 1 0 7",
            "sw_card 5 3 2 1 0",
            "end",
            "sw_char 2 15",
            "sw_char 0 14",
            "sw_char 1 13",
            "skill 1 12 11",
            "card 7 0 10",
            "sw_card 7 8 9",
            "card 6 2 9 8",
            "card 7 0 7",
            "sw_card 6 7",
            "end",
            "card 7 0 15",
            "sw_card 8 7 6 5 4 3 2 1 0",
            "end",
            "choose 2",
            "TEST 3 card 0 1 cannot use",
            "end"
        ],
        [
            "sw_card 1",
            "choose 1",
            "skill 1 15 14 13",
            "card 4 1 12 11",
            "TEST 2 card 4 cost 2",
            "card 3 0 10",
            "sw_card 3",
            "skill 1 9 8",
            "card 4 0 7",
            "sw_card 4 5",
            "skill 1 6 5 4",
            "card 5 0 3",
            "sw_card 5",
            "skill 1 2 1 0",
            "end",
            "end",
            "card 5 0 15",
            "sw_card 5 6 7 9",
            "skill 1 14 13",
            "card 9 0 12",
            "sw_card",
            "card 9 2 11 10",
            "skill 1 9 8 7",
            "sw_char 0 6",
            "card 8 0 5",
            "sw_card 8 7",
            "card 8 2 4 3",
            "card 8 0 2 1",
            "end",
            "sw_char 1 15",
            "card 8 0 14",
            "sw_card 7 6 9 5 4 3 2 1 0",
            "card 3 0 13 12",
            "TEST 1 p1 hand 5",
            "skill 2 11 10 9 8",
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
        charactor:Kaeya
        charactor:Keqing
        charactor:Fischl
        Nature and Wisdom*15
        Thunder Summoner's Crown*15
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
                assert len(match.player_tables[1].hands) == 5
            elif test_id == 2:
                for req in match.requests:
                    if req.name == 'UseCardRequest' and req.card_idx == 4:
                        assert req.cost.total_dice_cost == 2
            elif test_id == 3:
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert req.card_idx not in [0, 1]
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_keqing_freeze():
    """
    If keqing is frozen, it cannot use Lightning Stiletto.
    """
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "sw_char 2 12",
            "sw_char 1 11",
            "sw_char 2 10",
            "skill 1 9 8 7",
            "end",
            "sw_char 0 15",
            "skill 1 14 13 12"
        ],
        [
            "sw_card 1 2",
            "choose 1",
            "skill 1 15 14 13",
            "TEST 1 card 5 can use",
            "sw_char 0 12",
            "TEST 1 card 5 can use",
            "sw_char 1 11",
            "TEST 2 card 5 cannot use",
            "sw_char 0 10",
            "TEST 2 card 5 cannot use",
            "end",
            "TEST 1 card 5 can use",
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
        charactor:Kaeya
        charactor:Keqing
        charactor:Mona
        Nature and Wisdom*15
        Thunder Summoner's Crown*15
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
            test_cmd = agent.commands[0]
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                cidx = int(test_cmd.split()[3])
                for req in match.requests:
                    if req.name == 'UseCardRequest' and req.card_idx == cidx:
                        break
                else:
                    raise AssertionError('Request not found')
            elif test_id == 2:
                cidx = int(test_cmd.split()[3])
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert req.card_idx != cidx
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    # test_keqing()
    test_keqing_2()
    # test_keqing_freeze()
