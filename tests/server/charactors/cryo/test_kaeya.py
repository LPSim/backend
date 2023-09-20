from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_kaeya():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 0 0 0 1 2 3",
            "skill 1 0 1 2",
            "TEST 1 5 10 10 6 10 10",
            "skill 2 0 1 2 3",
            "end",
            "skill 1 0 1 2",
            "TEST 1 3 10 10 4 10 10",
            "skill 1 0 1 2",
            "choose 1",
            "TEST 1 0 8 10 0 10 10",
            "end",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "choose 2",
            "skill 0 0 1 2"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 0 1 2 3",
            "card 0 0 1 2 3 4",
            "TEST 2 p0 team usage 3",
            "skill 2 0 1 2 3",
            "end",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "choose 1",
            "skill 0 0 1 2",
            "end",
            "TEST 1 0 6 10 0 6 9",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 3 no skill",
            "sw_char 2 0",
            "sw_char 1 0",
            "TEST 1 0 0 9 0 1 9",
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
        charactor:Kaeya
        charactor:Mona
        charactor:ElectroMobMage
        Cold-Blooded Strike*30
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
                assert len(match.player_tables[0].team_status) == 1
                assert match.player_tables[0].team_status[0].usage == 3
            elif test_id == 3:
                for req in match.requests:
                    assert req.name != 'UseSkillRequest'
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_kaeya_wind_and_freedom():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 2 0 0 1 2 3",
            "skill 0 0 1 2",
            "end",
            "skill 0 0 1 2",
            "skill 2 0 1 2 3",
            "card 0 0 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "choose 1",
            "TEST 1 0 6 9 0 8 8",
            "end"
        ],
        [
            "sw_card 0 1 2",
            "choose 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "end",
            "skill 2 0 1 2 3",
            "skill 0 0 1 2",
            "choose 1",
            "card 2 0 0",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "sw_char 1 0"
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
        charactor:Kaeya
        charactor:Mona
        charactor:ElectroMobMage
        Cold-Blooded Strike*15
        Wind and Freedom*15
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
    test_kaeya()
