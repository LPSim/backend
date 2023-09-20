from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, get_pidx_cidx, get_random_state, get_test_id_from_command, 
    make_respond, set_16_omni
)


def test_razor():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "TEST 2 p1c2 charge 2",
            "sw_char 3 12",
            "card 2 0 11 10 9 8",
            "skill 1 7 6 5",
            "skill 2 4 3 2",
            "end",
            "skill 0 15 14 13",
            "skill 1 12 11 10",
            "sw_char 2 9",
            "card 2 0 8 7 6 5",
            "skill 2 4 3 2",
            "TEST 2 p0c1 charge 1",
            "TEST 2 p0c2 charge 0",
            "end",
            "TEST 2 p1c0 charge 1",
            "TEST 2 p1c1 charge 0",
            "sw_char 3 15",
            "skill 1 14 13 12"
        ],
        [
            "sw_card",
            "choose 2",
            "card 1 0 15 14 13 12",
            "sw_char 0 11",
            "skill 1 10 9 8",
            "TEST 2 p0c1 charge 1",
            "TEST 2 p0c3 charge 3",
            "sw_char 3 7",
            "TEST 1 7 10 10 7 4 10 7 5",
            "sw_char 0 6",
            "sw_char 3 5",
            "end",
            "choose 2",
            "sw_char 1 15",
            "TEST 1 7 10 10 7 3 4 6 0",
            "sw_char 0 14",
            "sw_char 1 13",
            "TEST 1 7 10 10 7 3 1 6 0",
            "TEST 2 p0c1 charge 1",
            "TEST 2 p0c2 charge 2",
            "end",
            "choose 2",
            "skill 1 15 14 13",
            "sw_char 0 12",
            "choose 2",
            "TEST 2 p0c1 charge 2",
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
        charactor:Chongyun
        charactor:Keqing
        charactor:Razor
        charactor:Razor@3.3
        Awakening*30
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
                hps = [hps[:4], hps[4:]]
                check_hp(match, hps)
            elif test_id == 2:
                cmd = cmd.split()
                pidx, cidx = get_pidx_cidx(cmd)
                assert match.player_tables[pidx].charactors[
                    cidx].charge == int(cmd[4])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_razor()
