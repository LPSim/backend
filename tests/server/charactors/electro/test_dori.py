from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, get_pidx_cidx, get_random_state, get_test_id_from_command, 
    make_respond, set_16_omni
)


def test_dori():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "sw_char 2 9",
            "skill 1 8 7 6",
            "sw_char 1 5",
            "skill 2 4 3 2",
            "end",
            "TEST 1 9 4 9 8 4 5",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "sw_char 0 9",
            "skill 0 8 7 6",
            "end",
            "sw_char 2 15",
            "TEST 1 8 4 6 9 0 5",
            "skill 0 14 13 12",
            "skill 0 11 10 9",
            "end",
            "skill 2 15 14 13",
            "skill 1 12 11 10",
            "sw_char 1 9",
            "card 0 0 8 7 6",
            "sw_char 2 5",
            "end",
            "TEST 1 8 4 9 4 0 0",
            "TEST 2 p0c2 charge 2",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "sw_char 2 9",
            "skill 1 8 7 6",
            "TEST 1 10 6 10 9 5 8",
            "end",
            "TEST 1 9 5 9 8 4 5",
            "TEST 2 p0c1 charge 1",
            "sw_char 1 15",
            "card 1 0 14 13 12",
            "end",
            "choose 0",
            "skill 2 15 14 13",
            "skill 0 12 11 10",
            "end",
            "TEST 1 8 4 6 9 0 5",
            "sw_char 2 15",
            "sw_char 0 14",
            "end",
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
        charactor:Xingqiu
        charactor:Dori
        charactor:Mona
        Discretionary Supplement*30
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
                pidx, cidx = get_pidx_cidx(cmd)
                charge = int(cmd[4])
                assert match.player_tables[pidx].charactors[
                    cidx].charge == charge
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_dori()
