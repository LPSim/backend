from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, check_usage, get_random_state, get_test_id_from_command, 
    make_respond, set_16_omni
)


def test_xingqiu():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "end",
            "skill 1 0 1 2",
            "skill 2 0 1 2",
            "sw_char 2 0",
            "skill 1 0",
            "TEST 1 5 10 10 10 7 6",
            "skill 0 0 1 2",
            "TEST 1 5 10 10 10 1 6",
            "end",
            "TEST 2 p1 team usage 3",
            "sw_char 0 0",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "sw_char 2 0",
            "skill 1 0",
            "skill 0 0 1 2",
            "end",
            "TEST 1 7 10 10 10 8 6",
            "TEST 3 p0c0 no ele app",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "end",
            "card 0 0 0 1 2 3",
            "skill 2 0 1 2",
            "sw_char 2 0",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "TEST 1 4 8 8 10 1 4",
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
        charactor:Xingqiu@3.3
        charactor:Xingqiu
        charactor:Yoimiya
        The Scent Remained*30
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
                assert len(match.player_tables[1].team_status) == 1
                assert match.player_tables[1].team_status[0].usage == 3
            elif test_id == 3:
                assert match.player_tables[0].charactors[
                    0].element_application == []
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_xingqiu_4_2():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 2 0 15 14 13",
            "skill 1 12 11 10",
            "TEST 1 8 10 10 10 6 10",
            "TEST 2 p0 team 2",
            "TEST 2 p1 team 3",
            "end"
        ],
        [
            "sw_card 1 2 3",
            "choose 1",
            "skill 1 15 14 13",
            "card 2 0 12 11 10 9"
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
        default_version:4.2
        charactor:Xingqiu
        charactor:Xingqiu@3.6
        charactor:Xingqiu@3.3
        The Scent Remained*15
        The Scent Remained@3.3*15
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
                cmd = cmd.strip().split(' ')
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].team_status, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_xingqiu()
    test_xingqiu_4_2()
