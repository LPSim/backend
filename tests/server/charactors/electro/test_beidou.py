from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, get_pidx_cidx, get_random_state, get_test_id_from_command, 
    make_respond, set_16_omni
)


def test_beidou():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "TEST 1 10 8 10 10 10 10 9 10",
            "TEST 2 p0c1 charge 1",
            "skill 1 12 11 10",
            "skill 1 9 8 7",
            "TEST 1 10 4 10 10 10 10 7 10",
            "skill 3 6 5 4",
            "TEST 1 10 2 10 10 10 10 5 10",
            "sw_char 0 3",
            "skill 1 2 1 0",
            "end",
            "skill 0 15 14 13",
            "TEST 1 4 1 9 9 4 9 4 9",
            "sw_char 2 12",
            "skill 1 11 10 9",
            "card 5 0 8 7 6",
            "TEST 3 skill 0 cost 3",
            "sw_char 1 5",
            "skill 0 4 3 2",
            "choose 2",
            "TEST 1 4 0 9 9 1 7 1 8",
            "TEST 4 no skill can use",
            "end",
            "skill 1 15 14 13",
            "TEST 3 skill 0 cost 3",
            "sw_char 3 12",
            "sw_char 0 11",
            "sw_char 2 10",
            "skill 0 9 8 7",
            "sw_char 3 6",
            "card 3 1",
            "card 4 1",
            "card 0 0",
            "end",
            "skill 1 15 14 13",
            "TEST 1 2 0 3 4 2 7 2 9",
            "sw_char 0 12"
        ],
        [
            "sw_card 1 2 3",
            "choose 2",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "skill 1 9 8 7",
            "skill 3 6 5 4 3",
            "sw_char 0 2",
            "end",
            "TEST 1 10 2 10 10 8 10 5 10",
            "skill 1 15 14 13",
            "TEST 1 8 2 10 10 4 9 4 9",
            "skill 0 12 11 10",
            "sw_char 1 9",
            "sw_char 2 8",
            "sw_char 1 7",
            "sw_char 0 6",
            "sw_char 1 5",
            "card 1 0 4 3 2",
            "TEST 3 skill 0 cost 2",
            "end",
            "skill 1 15 14 13",
            "skill 0 12 11",
            "skill 0 10 9",
            "TEST 3 skill 0 cost 3",
            "skill 1 8 7 6",
            "TEST 3 skill 0 cost 3",
            "end",
            "card 2 2",
            "card 1 0",
            "card 1 0",
            "card 1 0",
            "skill 1 15 14 13",
            "TEST 3 skill 0 cost 2",
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
        charactor:Beidou
        charactor:Beidou@3.5
        charactor:Razor
        Lightning Storm*15
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
                hps = [hps[:4], hps[4:]]
                check_hp(match, hps)
            elif test_id == 2:
                cmd = cmd.split()
                pidx, cidx = get_pidx_cidx(cmd)
                assert match.player_tables[pidx].charactors[
                    cidx].charge == int(cmd[4])
            elif test_id == 3:
                cmd = cmd.split()
                sidx = int(cmd[3])
                cost = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseSkillRequest' and req.skill_idx == sidx:
                        assert req.cost.total_dice_cost == cost
            elif test_id == 4:
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


if __name__ == '__main__':
    test_beidou()
