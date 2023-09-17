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
    Note currently adding Lightning Stiletto into deck directly will cause
    a bug that using skill first time will not remove itself and add buff.
    As it is not a normal way to get this card, currently it is not fixed,
    and this test is based on this bug, so it will fail if this bug is fixed.

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
            "sw_card",
            "choose 0",
            "card 0 1 0 1",
            "card 1 0 0 1",
            "sw_char 0 0",
            "card 1 0 0 1 2",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "end",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "card 2 0 0 1"
        ],
        [
            "sw_card 0 1 2",
            "choose 1",
            "skill 1 0 1 2",
            "sw_char 0 0",
            "card 0 0 0 1 2",
            "skill 1 0 1 2",
            "end",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "TEST 1 4 use card req",
            "end",
            "choose 2"
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
        charactor:Kaeya
        charactor:Keqing
        charactor:Fischl
        Lightning Stiletto*15
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
                # a sample of HP check based on the command string.
                counter = 0
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        counter += 1
                assert counter == 4
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_keqing()
