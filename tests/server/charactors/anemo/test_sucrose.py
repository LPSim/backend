from src.lpsim.server.charactor.anemo.sucrose_3_3 import LargeWindSpirit_3_3
from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from src.lpsim.server.consts import DamageElementalType
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_sucrose():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "skill 1 15 14 13",
            "sw_char 2 12",
            "skill 1 11 10 9",
            "skill 1 8 7 6",
            "sw_char 1 5",
            "skill 1 4 3 2",
            "sw_char 2 1",
            "end",
            "TEST 2 p1 summon hydro",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "skill 1 9 8 7",
            "skill 1 6 5 4",
            "skill 1 3 2 1",
            "card 3 2",
            "end",
            "sw_char 1 15",
            "sw_char 2 14",
            "card 2 0 13 12 11",
            "TEST 1 18 18 8 17 18 0",
            "sw_char 1 10",
            "sw_char 2 9",
            "skill 0 8 7 6",
            "TEST 1 18 18 8 17 18 0",
            "sw_char 1 5",
            "skill 1 4 3 2",
            "end",
            "TEST 1 16 12 6 12 17 0",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "sw_char 2 15",
            "skill 1 14 13 12",
            "sw_char 0 11",
            "skill 0 10 9 8",
            "sw_char 1 7",
            "skill 1 6 5 4",
            "end",
            "sw_char 2 15",
            "skill 2 14 13 12",
            "sw_char 2 11",
            "skill 0 10 9 8",
            "sw_char 2 7",
            "sw_char 2 6",
            "sw_char 2 5",
            "skill 0 4 3 2",
            "end",
            "card 0 0 15 14 13",
            "choose 1",
            "TEST 1 18 18 10 17 18 0",
            "skill 1 12 11 10",
            "sw_char 0 9",
            "end",
            "TEST 1 18 14 8 12 17 0",
            "skill 1 15 14 13"
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
        charactor:Venti
        charactor:Mona
        charactor:Sucrose
        Chaotic Entropy*15
        Sweet Madame*15
        '''
    )
    # change HP
    for charactor in deck.charactors:
        charactor.max_hp = 20
        charactor.hp = 20
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
                summons = match.player_tables[1].summons
                assert len(summons) == 1
                summon = summons[0]
                assert isinstance(summon, LargeWindSpirit_3_3)
                assert (
                    summon.damage_elemental_type
                    == DamageElementalType.HYDRO
                )
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_sucrose_2():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7",
            "skill 0 6 5 4",
            "skill 0 3 2 1",
            "end",
            "skill 2 15 14 13",
            "sw_char 1 12",
            "end",
            "sw_char 2 15",
            "skill 1 14 13 12",
            "skill 1 11 10 9",
            "skill 1 8 7 6",
            "card 4 0 5 4 3",
            "skill 1 2 1 0",
            "end",
            "choose 1"
        ],
        [
            "sw_card",
            "choose 2",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7",
            "skill 0 6 5 4",
            "skill 0 3 2 1",
            "end",
            "skill 2 15 14 13",
            "end",
            "choose 0",
            "sw_char 1 15",
            "sw_char 1 14",
            "sw_char 1 13",
            "sw_char 1 12",
            "choose 0",
            "end",
            "TEST 1 10 8 0 5 0 0",
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
        charactor:Venti
        charactor:Mona
        charactor:Sucrose
        Chaotic Entropy*15
        Sweet Madame*15
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
    test_sucrose()
