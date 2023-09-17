from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_maguu_kenki():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 3 0 1 2",
            "sw_char 0 0",
            "TEST 1 10 4 10 10 4 10",
            "sw_char 1 0",
            "end",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "TEST 1 3 2 9 9 4 10",
            "TEST 2 p1 summon usage 2 2",
            "sw_char 2 0",
            "sw_char 1 0",
            "choose 2",
            "sw_char 0 0",
            "card 0 0 0 1 2",
            "end",
            "sw_char 0 0",
            "sw_char 2 0",
            "sw_char 0 0",
            "TEST 3 p1 active 2",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "choose 0",
            "skill 1 0 1 2",
            "skill 2 0 1 2",
            "skill 0 0 1 2",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 2 0 1 2",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 3 0 1 2",
            "sw_char 0 0",
            "end",
            "TEST 1 10 3 10 9 4 10",
            "skill 1 0 1 2",
            "skill 2 0 1 2",
            "skill 3 0 1 2",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "end",
            "sw_char 0 0",
            "card 0 0 0 1 2",
            "TEST 3 p1 active 1",
            "sw_char 0 0",
            "skill 2 0 1 2",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "end",
            "choose 0"
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
        charactor:Maguu Kenki
        charactor:Nahida
        charactor:Fischl
        Transcendent Automaton*30
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
                summon = match.player_tables[1].summons
                assert len(summon) == 2
                for s in summon:
                    assert s.usage == 2
            elif test_id == 3:
                cmd = cmd.strip().split(' ')
                pidx = int(cmd[2][1])
                aidx = int(cmd[4])
                assert match.player_tables[pidx].active_charactor_idx == aidx
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_maguu_kenki_old():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "card 0 0 0 1 2",
            "sw_char 2 9",
            "skill 2 0 1 2",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "end",
            "choose 1",
            "TEST 1 7 8 0 9 10 5",
            "end",
            "choose 0",
            "TEST 1 6 0 0 9 8 5",
            "end",
            "TEST 1 2 0 0 9 8 5",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "skill 2 0 1 2",
            "card 0 0 0 1 2",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "skill 3 0 1 2",
            "end",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "sw_char 1 0",
            "end",
            "sw_char 2 0",
            "skill 3 0 1 2",
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
        charactor:Nahida
        charactor:Fischl
        Transcendent Automaton*30
        '''
    )
    old = {'name': 'Maguu Kenki', 'version': '3.3'}
    deck_dict = deck.dict()
    deck_dict['charactors'] += [old]
    deck = Deck(**deck_dict)
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
    test_maguu_kenki_old()
    test_maguu_kenki()
