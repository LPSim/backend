from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_noelle():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2",
            "TEST 1 10 10 10 10 9 10",
            "TEST 5 no status",
            "skill 1 0 1 2",
            "TEST 1 10 10 10 10 8 10",
            "TEST 2 p0 status 1 usage 1",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "end",
            "sw_char 0 0",
            "skill 2 0 1 2 3",
            "TEST 3 p0 team status 1 crystallize",
            "TEST 4 skill 0 cost 2",
            "skill 0 0 1",
            "TEST 4 skill 0 cost 3",
            "TEST 1 10 10 10 6 8 4",
            "skill 1 0 1 2",
            "TEST 1 10 10 10 7 9 5",
            "skill 2 0 1 2 3",
            "TEST 4 skill 0 cost 2",
            "skill 0 0 1",
            "end",
            "TEST 1 10 10 10 4 9 1",
            "TEST 4 skill 0 cost 2",
            "skill 0 0 1",
            "sw_char 1 0",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "TEST 1 4 9 10 5 10 0",
            "sw_char 1 0",
            "sw_char 0 0",
            "TEST 1 2 9 10 5 10 0",
            "end",
            "TEST 5 p0c0 no charactor status",
            "TEST 4 skill 0 cost 3",
            "sw_char 1 0",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 1 0 1 2",
            "skill 0 0 1 2",
            "sw_char 0 0",
            "TEST 6 p1c1 no geo application",
            "sw_char 2 0",
            "end",
            "TEST 1 10 10 10 9 8 4",
            "sw_char 0 0",
            "card 0 0 0 1 2",
            "TEST 1 10 10 10 6 8 4",
            "skill 1 0 1 2",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "end",
            "choose 0",
            "skill 0 0 1 2",
            "skill 1 0 1 2",
            "skill 2 0 1 2 3",
            "skill 0 0 1",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "end",
            "sw_char 0 0",
            "skill 0 0 1",
            "skill 0 0 1 2",
            "TEST 1 2 1 10 7 10 0",
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
        charactor:Noelle
        charactor:PhysicalMob
        charactor:Mona
        I Got Your Back*30
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
                status = match.player_tables[0].team_status
                assert len(status) == 1
                assert status[0].name == 'Full Plate'
                assert status[0].usage == 1
            elif test_id == 3:
                status = match.player_tables[0].team_status
                assert len(status) == 1
                assert status[0].name == 'Crystallize'
                assert status[0].usage == 1
            elif test_id == 4:
                cmd = cmd.strip().split(' ')
                snum = int(cmd[3])
                cnum = int(cmd[5])
                compared = False
                for req in match.requests:
                    if req.name == 'UseSkillRequest':
                        if req.skill_idx == snum:
                            assert req.cost.total_dice_cost == cnum
                            compared = True
                assert compared
            elif test_id == 5:
                status = match.player_tables[0].charactors[0].status
                assert len(status) == 0
            elif test_id == 6:
                assert match.player_tables[1].charactors[
                    1].element_application == []
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_noelle()
