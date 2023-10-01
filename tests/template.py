# type: ignore
"""
This file contains a template for writing tests. You can copy this file to
tests/folder/test_xxx.py and modify it to write your own tests.
"""
from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_...():
    # use frontend and FastAPI server to perform commands, and test commands 
    # that start with TEST. NO NOT put TEST at the end of command list!
    # If a command is succesfully performed, frontend will print history 
    # commands in console. Note that frontend cannot distinguish if a new
    # match begins, so you need to refresh the page before recording a new
    # match, otherwise the history commands will be mixed.
    #
    # for tests, it starts with TEST and contains a test id, which is used to
    # identify the test. Other texts in the command are ignored, but you can
    # parse them if you want. Refer to the following code.
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2",
            "end",
            "TEST 1 9 10 10 10 9 10",
            ...
        ],
        [
            "sw_card",
            "choose 1",
            "skill 1 0 1 2",
            "end",
            "end",
            "TEST 1 9 10 10 9 8 9",
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
        charactor:Nahida*3
        Rana*30
        ...
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
            elif test_id == 2:
                ...
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR
