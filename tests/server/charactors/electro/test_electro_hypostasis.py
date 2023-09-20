from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_elec_hypo():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 2 2 skill 0 1",
            "skill 1 0 1 2 3 4",
            "TEST 1 4 10 10 3 8 10",
            "skill 0 0 1 2",
            "skill 4 0 1 2",
            "TEST 3 sw_char cost 1",
            "sw_char 1 0",
            "end",
            "sw_char 2 0",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "sw_char 0 0",
            "skill 1 0 1 2 3 4",
            "TEST 1 1 8 8 1 6 10",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "TEST 1 8 10 10 8 8 10",
            "sw_char 0 0",
            "TEST 1 8 10 10 6 8 10",
            "skill 1 0 1 2 3 4",
            "TEST 1 1 10 10 1 8 10",
            "TEST 3 switch_charactor cost 2",
            "card 0 0 0 1 2",
            "sw_char 1 0 1",
            "sw_char 0 0",
            "end",
            "TEST 3 sw_char cost 2",
            "skill 1 0 1 2 3 4",
            "TEST 4 active p1",
            "TEST 5 p0c1 status empty",
            "sw_char 0 0 1",
            "sw_char 1 0",
            "skill 1 0 1 2"
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
        charactor:Electro Hypostasis
        charactor:Klee
        charactor:Keqing
        Absorbing Prism*15
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
                found = set()
                for req in match.requests:
                    if req.name == 'UseSkillRequest':
                        found.add(req.skill_idx)
                assert found == set([0, 1])
            elif test_id == 3:
                cmd = cmd.split()
                sc = int(cmd[-1])
                for req in match.requests:
                    if req.name == 'SwitchCharactorRequest':
                        assert sc == req.cost.total_dice_cost
            elif test_id == 4:
                assert match.current_player == 1
            elif test_id == 5:
                assert len(match.player_tables[0].charactors[1].status) == 0
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_2():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "end",
            "sw_char 0 0",
            "end",
            "end",
            "choose 1",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "choose 1"
        ],
        [
            "sw_card",
            "choose 1",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "sw_char 0 0",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "end",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "end",
            "skill 0 0 1 2",
            "sw_char 1 0",
            "skill 2 0 1 2",
            "sw_char 0 0",
            "end",
            "skill 1 0 1 2 3 4"
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
        charactor:Electro Hypostasis
        charactor:Klee
        charactor:Keqing
        Absorbing Prism*15
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
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_prepare_frozen():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2 3 4",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "TEST 1 5 10 10 8 10 7",
            "end",
            "TEST 1 4 10 10 8 7 7",
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
        charactor:Electro Hypostasis
        charactor:CryoMobMage
        charactor:Mona
        Absorbing Prism*30
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
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_electro_bennett():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "card 0 0 0 1 2 3",
            "sw_char 2 0",
            "skill 1 0 1 2 3 4"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "TEST 1 8 10 8 4 6 8",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "TEST 1 8 10 6 4 2 3",
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
        charactor:Bennett
        charactor:Maguu Kenki
        charactor:Electro Hypostasis
        Grand Expectation*30
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
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_elec_hypo()
    # test_prepare_frozen()
