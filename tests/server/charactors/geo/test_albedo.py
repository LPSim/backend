from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_albedo():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "TEST 2 skill 0 cost 3",
            "sw_char 1 12",
            "TEST 2 skill 0 cost 2",
            "skill 1 11 10 9",
            "TEST 2 skill 0 cost 3",
            "sw_char 0 8",
            "TEST 2 skill 0 cost 2",
            "skill 0 7 6",
            "sw_char 1 5",
            "TEST 2 skill 0 cost 3",
            "skill 1 4 3 2",
            "sw_char 0 1",
            "end",
            "card 0 0 15 14 13",
            "TEST 1 3 9 10 7 8 10",
            "sw_char 2 12",
            "skill 0 11 10",
            "skill 0 9 8 7",
            "sw_char 1 6",
            "skill 0 5 4",
            "sw_char 0 3",
            "end",
            "choose 2",
            "skill 0 15 14",
            "end",
            "end"
        ],
        [
            "sw_card 1 2",
            "choose 1",
            "TEST 2 skill 0 cost 3",
            "skill 1 15 14 13",
            "sw_char 0 12",
            "skill 1 11 10 9",
            "sw_char 1 8",
            "TEST 2 skill 0 cost 1",
            "card 0 1",
            "TEST 2 skill 0 cost 1",
            "skill 0 7",
            "TEST 2 skill 0 cost 3",
            "sw_char 0 6",
            "skill 0 5 4",
            "end",
            "TEST 2 skill 0 cost 3",
            "sw_char 1 15",
            "TEST 2 skill 0 cost 2",
            "skill 0 14 13",
            "sw_char 2 12",
            "skill 0 11 10 9",
            "sw_char 0 8",
            "skill 2 7 6 5",
            "TEST 1 3 3 9 3 8 7",
            "skill 0 4 3 2",
            "end",
            "skill 0 15 14 13",
            "TEST 1 0 1 9 1 8 7",
            "sw_char 2 12",
            "end",
            "sw_char 0 15",
            "sw_char 1 14",
            "skill 1 13 12 11",
            "sw_char 0 10",
            "skill 2 9 8 7",
            "TEST 1 0 1 3 1 8 5",
            "sw_char 1 6",
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
        charactor:Albedo
        charactor:Arataki Itto
        charactor:Yae Miko
        Northern Smoked Chicken*15
        Descent of Divinity*15
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
                sidx = int(cmd[3])
                cost = int(cmd[-1])
                for req in match.requests:
                    if req.name == 'UseSkillRequest' and req.skill_idx == sidx:
                        assert cost == req.cost.total_dice_cost
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_albedo()
