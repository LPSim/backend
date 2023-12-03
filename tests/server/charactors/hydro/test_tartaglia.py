from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, check_usage, get_pidx_cidx, get_random_state, 
    get_test_id_from_command, make_respond, set_16_omni
)


def test_tartaglia():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "TEST 2 p0c2 status",
            "sw_char 1 0",
            "TEST 3 p1c1 melle",
            "TEST 2 p0c1 status 1",
            "sw_char 0 0",
            "TEST 1 8 8 8 10 10 10 10 10 10 8",
            "TEST 4 p0c0 elem hydro",
            "sw_char 2 0",
            "end",
            "TEST 2 p1c1 status 1",
            "skill 0 0 1 2",
            "choose 4",
            "TEST 2 p0c4 status 2",
            "sw_char 3 0",
            "TEST 1 8 8 0 1 10 10 8 10 10 8",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 2 0 1 2",
            "end",
            "skill 1 0 1 2",
            "sw_char 4 0",
            "skill 1 0 1 2",
            "sw_char 3 0",
            "skill 0 0 1 2",
            "TEST 2 p1c4 status 2",
            "end",
            "end",
            "choose 0",
            "sw_char 4 0",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "TEST 2 p1c0 usage",
            "end",
            "skill 0 0 1 2",
            "skill 1 0 1 2",
            "TEST 1 8 8 0 0 10 9 2 6 0 0",
            "skill 2 0 1 2",
            "TEST 1 8 8 0 0 10 9 0 5 0 0",
            "skill 0 0 1 2",
            "TEST 1 8 8 0 0 10 9 0 2 0 0",
            "end",
            "skill 1 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 8 8 0 0 10 5 0 0 0 0",
            "card 0 0 0 1 2 3",
            "end"
        ],
        [
            "sw_card",
            "choose 4",
            "TEST 2 p1c4 status 2",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "skill 1 0 1 2",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 8 8 3 9 10 10 10 10 10 8",
            "end",
            "skill 0 0 1 2",
            "skill 2 0 1 2",
            "sw_char 2 0",
            "sw_char 3 0",
            "sw_char 4 0",
            "TEST 1 8 8 0 1 10 10 8 8 8 4",
            "end",
            "sw_char 3 0",
            "TEST 1 8 8 0 1 10 10 8 8 5 3",
            "sw_char 4 0",
            "sw_char 3 0",
            "sw_char 4 0",
            "end",
            "end",
            "skill 0 0 1 2",
            "end",
            "choose 0",
            "sw_char 1 0",
            "end",
            "choose 2",
            "end",
            "choose 0",
            "TEST 1 8 8 0 0 10 1 0 0 0 0",
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
        charactor:Klee
        charactor:Tartaglia
        charactor:Venti
        charactor:ElectroMobMage
        charactor:CryoMobMage
        Abyssal Mayhem: Hydrospout*30
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
                hps = [hps[:5], hps[5:]]
                check_hp(match, hps)
            elif test_id == 2:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                cidx = int(cmd[2][3])
                usage = [int(x) for x in cmd[4:]]
                status = match.player_tables[pidx].charactors[cidx].status
                assert len(status) == len(usage)
                for s, u in zip(status, usage):
                    assert s.usage == u
            elif test_id == 3:
                status = match.player_tables[1].charactors[1].status
                assert len(status) == 1
                assert 'Melee' in status[0].name
            elif test_id == 4:
                assert match.player_tables[0].charactors[
                    0].element_application == ['HYDRO']
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_tartaglia_2():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "card 0 0 1 2 3 4",
            "skill 0 0 1 2",
            "end",
            "TEST 1 10 3 10 10 10 8 7 10 10 10",
            "end",
            "end",
            "choose 2"
        ],
        [
            "sw_card",
            "choose 0",
            "sw_char 1 0",
            "card 0 0 1 2 3 4",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "end",
            "end",
            "skill 2 15 14 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7",
            "TEST 2 p0c2 usage 2",
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
        charactor:Klee
        charactor:Tartaglia
        charactor:Venti
        charactor:ElectroMobMage
        charactor:CryoMobMage
        Abyssal Mayhem: Hydrospout*30
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
                hps = [hps[:5], hps[5:]]
                check_hp(match, hps)
            elif test_id == 2:
                cmd = cmd.split()
                pidx, cidx = get_pidx_cidx(cmd)
                status = match.player_tables[pidx].charactors[cidx].status
                check_usage(status, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_tartaglia_4_1():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "TEST 2 p0c0 usage 2",
            "sw_char 2 12",
            "sw_char 3 11",
            "sw_char 2 10",
            "sw_char 3 9",
            "sw_char 2 8",
            "TEST 1 8 10 8 8 10 10 8 10 10 10",
            "TEST 2 p0c3 usage 2",
            "end",
            "TEST 1 8 10 8 8 10 10 8 10 10 10",
            "TEST 2 p1c1 usage 1 1",
            "TEST 2 p0c3 usage 1",
            "sw_char 0 15",
            "skill 0 14 13 12",
            "skill 0 11 10 9",
            "sw_char 3 8",
            "end",
            "sw_char 0 15",
            "skill 2 14 13 12",
            "sw_char 4 11",
            "TEST 1 8 10 8 7 6 10 8 5 8 8",
            "TEST 2 p0c4 usage 2",
            "TEST 2 p1c2 usage 1",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "TEST 2 p1c1 usage 1 1",
            "skill 1 15 14 13",
            "sw_char 3 12",
            "sw_char 2 11",
            "sw_char 1 10",
            "skill 0 9 8 7",
            "card 0 0 6 5 4",
            "end",
            "sw_char 3 15",
            "sw_char 4 14",
            "TEST 2 p1c4 usage 1",
            "end",
            "TEST 1 8 10 8 7 10 10 8 10 8 8",
            "sw_char 3 15",
            "sw_char 2 14",
            "sw_char 1 13",
            "skill 2 12 11 10"
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
        default_version:4.1
        charactor:Tartaglia
        charactor:Tartaglia@3.7
        charactor:Venti
        charactor:ElectroMobMage
        charactor:CryoMobMage
        Abyssal Mayhem: Hydrospout*15
        Abyssal Mayhem: Hydrospout@3.7*15
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
                hps = [hps[:5], hps[5:]]
                check_hp(match, hps)
            elif test_id == 2:
                cmd = cmd.split()
                pidx, cidx = get_pidx_cidx(cmd)
                status = match.player_tables[pidx].charactors[cidx].status
                check_usage(status, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_tartaglia_reaction_bug_fix():
    # also test revive with status. Tartaglia & Raiden will re-attach status,
    # but fatui pyro agent will not.
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "sw_char 0 12",
            "end",
            "skill 1 15 14 13",
            "end",
            "skill 0 15 14 13",
            "TEST 1 1 7 8 1 7 8",
            "end",
            "choose 2",
            "skill 0 15 14 13",
            "skill 1 12 11 10",
            "skill 0 9 8 7",
            "choose 1",
            "skill 0 6 5 4",
            "skill 0 3 2 1",
            "end",
            "card 4 1 15 14",
            "sw_char 2 13",
            "end",
            "end",
            "sw_char 1 15",
            "card 6 0 14 13",
            "skill 2 12 11 10 9",
            "skill 1 8 7 6",
            "skill 0 5 4 3",
            "end",
            "choose 2",
            "skill 1 15 14 13",
            "card 3 0 12 11",
            "end",
            "TEST 2 p0c1 status 0",
            "TEST 2 p1c1 status 0",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "sw_char 0 12",
            "end",
            "skill 1 15 14 13",
            "end",
            "skill 0 15 14 13",
            "end",
            "choose 2",
            "skill 0 15 14 13",
            "skill 1 12 11 10",
            "skill 2 9 8 7",
            "end",
            "choose 1",
            "TEST 1 0 7 0 0 7 0",
            "card 3 0 15 14",
            "sw_char 0 13",
            "end",
            "TEST 2 p0c2 status",
            "TEST 2 p1c0 status 1",
            "TEST 2 p0c0 status",
            "TEST 2 p1c2 status",
            "end",
            "sw_char 1 15",
            "card 5 0 14 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7 6",
            "skill 1 5 4 3",
            "end",
            "skill 1 15 14 13",
            "card 2 0 12 11",
            "skill 1 10 9 8",
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
        default_version:4.2
        charactor:Tartaglia
        charactor:Raiden Shogun
        charactor:Fatui Pyro Agent
        Teyvat Fried Egg*10
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
                pidx, cidx = get_pidx_cidx(cmd)
                status = match.player_tables[pidx].charactors[cidx].status
                check_usage(status, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_tartaglia()
    test_tartaglia_2()
    test_tartaglia_4_1()
    test_tartaglia_reaction_bug_fix()
