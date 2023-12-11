from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_ganyu():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 2 0 15 14 13 12 11",
            "skill 2 10 9 8 7 6",
            "TEST 1 5 5 5 5 6 5",
            "sw_char 1 5",
            "end",
            "card 3 0 15 14 13 12 11",
            "skill 2 10 9 8 7 6",
            "TEST 1 4 4 4 0 2 0",
            "end",
            "sw_char 0 15",
            "skill 1 14 13 12",
            "skill 3 11 10 9"
        ],
        [
            "sw_card 2 3 4",
            "choose 1",
            "TEST 1 10 10 10 8 8 8",
            "skill 2 15 14 13 12 11",
            "TEST 1 8 8 8 5 6 5",
            "card 2 0 10 9 8 7 6",
            "sw_char 0 5",
            "end",
            "TEST 1 5 5 5 3 4 3",
            "sw_char 1 15",
            "TEST 1 5 5 5 0 2 0",
            "skill 3 14 13 12",
            "end",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "TEST 1 2 3 3 0 1 0",
            "skill 2 9 8 7 6 5"
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
        charactor:Ganyu@3.3
        charactor:Fischl
        Undivided Heart*15
        Undivided Heart@3.3*15
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


def test_ganyu_2():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "skill 1 9 8 7",
            "sw_char 1 6",
            "end",
            "skill 0 15 14 13",
            "choose 0",
            "end",
            "TEST 1 6 0 2 10 5 10",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 2 15 14 13 12 11",
            "card 2 0 10 9 8 7 6",
            "skill 3 5 4 3",
            "skill 0 2 1 0",
            "end",
            "skill 0 15 14 13",
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
        charactor:Ganyu
        charactor:Ganyu@3.3
        charactor:Fischl
        Undivided Heart*15
        Undivided Heart@3.3*15
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


def test_ganyu_with_heavy_and_cryo_resonance():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "card 1 0 15",
            "card 1 0 14",
            "skill 2 13 12 11 10 9",
            "TEST 1 10 7 10 8 4 8",
            "skill 0 8 7 6"
        ],
        [
            "sw_card 4 3",
            "choose 1",
            "TEST 1 10 10 10 8 4 8",
            "card 1 0 15",
            "card 2 0 14",
            "skill 1 13 12 11",
            "TEST 1 10 7 10 8 3 8",
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
        charactor:Ganyu@4.2*3
        Heavy Strike*15
        Elemental Resonance: Shattering Ice*15
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
            cmd = agent.commands[0].strip().split(' ')
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                # a sample of HP check based on the command string.
                hps = cmd[2:]
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
    test_ganyu()
    test_ganyu_with_heavy_and_cryo_resonance()
