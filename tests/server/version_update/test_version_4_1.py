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


def test_4_1_diona_xingqiu_NRE_egg():
    cmd_records = [
        [
            "sw_card 1",
            "choose 0",
            "card 4 0 15 14 13",
            "skill 0 12 11 10",
            "TEST 1 10 10 10 8 10 8",
            "end",
            "card 5 0 15 14",
            "sw_char 1 13",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "skill 0 6 5 4",
            "skill 0 3 2 1",
            "choose 2",
            "end",
            "card 5 0 15 14",
            "sw_char 1 13",
            "choose 2",
            "end",
            "card 2 0 15 14 13",
            "end"
        ],
        [
            "sw_card 2 3",
            "choose 2",
            "sw_char 0 15",
            "card 0 0 14 13 12 11",
            "card 1 0 10",
            "end",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "skill 1 9 8 7",
            "skill 1 6 5 4",
            "skill 1 3 2 1",
            "end",
            "skill 1 15 14 13",
            "end",
            "sw_char 1 15",
            "skill 0 14 13 12",
            "skill 0 11 10 9",
            "skill 2 8 7 6",
            "TEST 1 10 1 4 8 10 8",
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
        default_version:4.1
        charactor:Diona
        charactor:Xingqiu
        charactor:Nahida
        Shaken, Not Purred*5
        Shaken, Not Purred@3.3*5
        NRE*5
        NRE@3.3*5
        Teyvat Fried Egg*5
        Teyvat Fried Egg@3.7*5
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
    test_4_1_diona_xingqiu_NRE_egg()
