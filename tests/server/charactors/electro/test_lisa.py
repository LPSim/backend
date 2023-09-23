from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, check_usage, get_pidx_cidx, get_random_state, 
    get_test_id_from_command, make_respond, set_16_omni
)


def test_lisa():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 0 0 15",
            "sw_char 1 14",
            "skill 0 13 12 11",
            "TEST 1 10 8 10 10 9 10",
            "skill 1 10 9 8",
            "TEST 2 p0c1 status 2",
            "skill 2 7 6 5",
            "TEST 2 p0c1 status 3",
            "sw_char 0 4",
            "sw_char 1 3",
            "skill 1 2 1 0",
            "end",
            "choose 0",
            "TEST 1 10 0 10 6 2 10",
            "end",
            "card 1 0",
            "card 2 0",
            "skill 0 15 14",
            "TEST 1 6 0 10 2 1 9",
            "end"
        ],
        [
            "sw_card 1 2",
            "choose 1",
            "skill 1 15 14 13",
            "TEST 1 10 8 10 10 4 10",
            "TEST 2 p1c1 status",
            "TEST 2 p0c1 status 2",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "sw_char 0 6",
            "TEST 2 p1c0 status",
            "card 3 0 5",
            "sw_char 1 4",
            "TEST 2 p0c1 status 4",
            "sw_char 0 3",
            "end",
            "TEST 2 p0c1 status 4",
            "TEST 2 p1c0 status 3",
            "TEST 1 10 6 10 6 2 10",
            "sw_char 1 15",
            "TEST 2 p0c1 status 4",
            "skill 1 14 13 12",
            "sw_char 0 11",
            "end",
            "sw_char 1 15",
            "skill 1 14 13 12"
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
        charactor:Mona
        charactor:Lisa
        charactor:Yae Miko
        Northern Smoked Chicken*15
        Pulsating Witch*15
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
    test_lisa()
