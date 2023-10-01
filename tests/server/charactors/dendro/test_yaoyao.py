from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, check_usage, get_random_state, get_test_id_from_command, 
    make_respond, set_16_omni
)


def test_yaoyao():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "sw_char 1 9",
            "skill 1 8 7 6",
            "sw_char 0 5",
            "end",
            "TEST 1 7 8 10 8 7 10",
            "card 2 0 15 14 13",
            "end",
            "end",
            "TEST 1 8 8 10 7 7 10",
            "skill 2 15 14 13 12",
            "skill 0 11 10 9",
            "skill 0 8 7 6",
            "skill 0 5 4 3",
            "TEST 1 6 8 10 0 7 10",
            "TEST 2 p1 status 2",
            "sw_char 2 2",
            "end",
            "TEST 1 6 8 5 0 8 9",
            "TEST 2 p1 status 1 2",
            "end"
        ],
        [
            "sw_card 2 3",
            "choose 0",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "sw_char 1 9",
            "skill 1 8 7 6",
            "sw_char 0 5",
            "end",
            "skill 1 15 14 13",
            "end",
            "end",
            "skill 2 15 14 13 12",
            "end",
            "choose 2",
            "card 5 0 15 14 13"
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
        charactor:Yaoyao
        charactor:Keqing
        charactor:Nahida
        Beneficent*10
        Sweet Madame*10
        Mondstadt Hash Brown*10
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
                pidx = int(cmd[2][1])
                status = match.player_tables[pidx].team_status
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
    test_yaoyao()
