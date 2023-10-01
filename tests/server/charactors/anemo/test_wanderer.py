from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, check_usage, get_pidx_cidx, get_random_state, 
    get_test_id_from_command, make_respond, set_16_omni
)


def test_wanderer():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "TEST 1 27 29 29 30 28 27",
            "TEST 2 p0c0 usage 1",
            "skill 0 9 8 7",
            "TEST 1 26 26 28 30 25 27",
            "skill 2 6 5 4",
            "TEST 1 24 25 27 24 25 27",
            "sw_char 2 3",
            "TEST 1 23 24 19 24 25 27",
            "TEST 2 p1c0 usage",
            "end",
            "sw_char 0 15",
            "skill 0 14 13 12",
            "end",
            "sw_char 2 15",
            "TEST 1 18 23 17 25 25 27",
            "card 0 0 14",
            "end",
            "card 2 0 15",
            "sw_char 1 14",
            "sw_char 0 13",
            "skill 0 12 11 10",
            "card 2 0 9 8 7 6",
            "skill 0 5 4 3",
            "end",
            "TEST 1 16 13 14 23 24 27",
            "sw_char 1",
            "sw_char 2 15",
            "skill 0 14 13 12",
            "end",
            "sw_char 0 15",
            "skill 1 14 13 12",
            "skill 0 11 10 9",
            "TEST 3 sw_char cost 0",
            "skill 0 8 7 6",
            "TEST 3 sw_char cost 0",
            "end",
            "sw_char 0 15",
            "TEST 1 2 10 12 19 17 27",
            "TEST 3 sw_char cost 0",
            "sw_char 1",
            "end",
            "sw_char 2 15",
            "skill 1 14 13 12",
            "sw_char 0 11",
            "choose 1",
            "sw_char 2 10",
            "sw_char 1 9",
            "skill 0 8 7 6",
            "end",
            "TEST 1 0 4 0 15 17 26",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "TEST 1 29 30 30 30 28 27",
            "sw_char 0 12",
            "skill 1 11 10 9",
            "TEST 1 27 29 29 30 25 27",
            "TEST 2 p0c0 usage",
            "skill 0 8 7 6",
            "TEST 1 26 26 28 24 25 27",
            "skill 1 5 4 3",
            "skill 2 2 1 0",
            "end",
            "end",
            "card 6 0 15 14 13 12",
            "card 6 0 11",
            "TEST 3 sw cost 1",
            "skill 0 10 9 8",
            "card 6 0 7",
            "TEST 3 sw_char cost 1",
            "skill 0 6 5 4",
            "TEST 3 sw_char cost 1",
            "skill 0 3 2 1",
            "TEST 3 sw_char cost 1",
            "end",
            "card 4 0",
            "skill 1 15 14 13",
            "TEST 3 sw_char cost 1",
            "skill 0 12 11 10",
            "TEST 3 sw_char cost 1",
            "skill 0 9 8 7",
            "TEST 3 sw_char cost 0",
            "end",
            "TEST 3 sw_char cost 0",
            "sw_char 1",
            "TEST 4 p0 dice 16",
            "TEST 4 p1 dice 16",
            "TEST 1 16 13 14 23 23 27",
            "sw_char 0 15",
            "skill 1 14 13 12",
            "skill 0 11 10 9",
            "skill 0 8 7 6",
            "TEST 3 sw_char cost 0",
            "end",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "sw_char 2",
            "skill 1 6 5 4",
            "end",
            "TEST 1 2 10 12 19 17 26",
            "end",
            "sw_char 0 15",
            "sw_char 0 14",
            "skill 2 13 12 11",
            "skill 1 10 9 8",
            "skill 1 7 6 5",
            "skill 0 4 3 2",
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
        default_version:4.1
        charactor:Wanderer
        charactor:Mona
        charactor:Jean
        Gales of Reverie*10
        # Beneficent*10
        Sweet Madame*10
        Mondstadt Hash Brown*10
        '''
    )
    for charactor in deck.charactors:
        charactor.hp = 30
        charactor.max_hp = 30
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
                status = match.player_tables[pidx].charactors[cidx].status
                check_usage(status, cmd[4:])
            elif test_id == 3:
                find = 0
                for req in match.requests:
                    if req.name == 'SwitchCharactorRequest':
                        find += 1
                        assert req.cost.total_dice_cost == int(cmd[-1])
                assert find > 0
            elif test_id == 4:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[
                    pidx].dice.colors) == int(cmd[-1])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_wanderer()
