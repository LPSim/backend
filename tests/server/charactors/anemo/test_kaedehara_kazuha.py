from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.consts import DamageElementalType
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_kaedehara_kazuha():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "skill 1 0 1 2",
            "TEST 1 9 9 8 9 9 10 8 10 10 10",
            "TEST 2 p1 active 2",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 3 p1c1 Midare Ranzan",
            "end",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "TEST 4 p0 all hydro",
            "TEST 5 p1c1 status usage",
            "sw_char 2 0",
            "choose 0",
            "end",
            "sw_char 3 0",
            "TEST 1 2 7 0 5 7 10 6 7 10 10",
            "sw_char 0 0",
            "choose 1",
            "TEST 6 p1 team hydro 2",
            "end",
            "sw_char 4 0",
            "sw_char 3 0",
            "sw_char 4 0",
            "TEST 1 0 6 0 2 2 10 6 7 10 10",
            "sw_char 1 0",
            "TEST 1 0 3 0 2 2 10 6 7 10 10",
            "sw_char 3 0",
            "skill 0 0 1 2",
            "end",
            "sw_char 4 0",
            "choose 3",
            "sw_char 1 0",
            "card 0 0 0 1 2",
            "end",
            "choose 1",
            "end",
            "skill 0 0 1 2",
            "skill 2 0 1 2",
            "skill 1 0 1 2"
        ],
        [
            "sw_card 0 1 2",
            "choose 1",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "TEST 1 9 9 3 9 9 10 6 8 10 10",
            "end",
            "skill 1 0 1 2",
            "card 0 1 0 1 2",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "end",
            "skill 0 0 1 2",
            "card 1 0 0 1 2",
            "end",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 2 0 1 2",
            "skill 0 0 1 2",
            "end",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "end",
            "skill 1 0 1 2",
            "sw_char 0 0",
            "end",
            "sw_char 2 0",
            "choose 0",
            "TEST 1 0 2 0 0 0 2 0 0 4 4",
            "TEST 7 p0 summon hydro",
            "TEST 8 p0 status electro hydro",
            "sw_char 3 0",
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
        charactor:Klee
        charactor:Kaedehara Kazuha
        charactor:Xingqiu
        charactor:ElectroMobMage
        charactor:CryoMobMage
        Plunging Strike*15
        Poetics of Fuubutsu*15
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
                assert match.player_tables[1].active_charactor_idx == 2
            elif test_id == 3:
                assert match.player_tables[1].charactors[1].status[
                    0].name == 'Midare Ranzan'
            elif test_id == 4:
                for charactor in match.player_tables[0].charactors:
                    assert charactor.element_application == ['HYDRO']
            elif test_id == 5:
                assert len(match.player_tables[1].charactors[1].status) == 0
            elif test_id == 6:
                assert match.player_tables[1].team_status[
                    0].name[-5:] == 'Hydro'
            elif test_id == 7:
                assert match.player_tables[0].summons[
                    0].damage_elemental_type == DamageElementalType.HYDRO
            elif test_id == 8:
                assert match.player_tables[0].team_status[
                    0].name[-7:] == 'Electro'
                assert match.player_tables[0].team_status[
                    1].name[-5:] == 'Hydro'
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_kaedehara_klee():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 2 0 1 2",
            "end",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "end",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "TEST 1 6 9 9 9 9 4 10 8 10 10",
            "card 0 1 0 1 2",
            "TEST 1 3 9 9 9 9 4 8 8 10 10",
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
        charactor:Klee
        charactor:Kaedehara Kazuha
        charactor:Xingqiu
        charactor:ElectroMobMage
        charactor:CryoMobMage
        Plunging Strike*15
        Poetics of Fuubutsu*15
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
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_kaedehara_kazuha()
