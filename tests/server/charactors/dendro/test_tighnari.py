from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_tighnari():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "skill 0 6 5 4",
            "skill 0 3 2 1",
            "end",
            "sw_char 1 15",
            "sw_char 2 14",
            "sw_char 1 13",
            "TEST 2 p1 summon 2",
            "sw_char 0 12",
            "skill 0 11 10 9",
            "skill 1 8 7 6",
            "skill 0 5 4 3",
            "sw_char 1 2",
            "end",
            "sw_char 0 15",
            "skill 0 14 13 12",
            "sw_char 1 11",
            "TEST 1 0 1 7 1 4 5",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "sw_char 0 15",
            "TEST 1 10 10 10 8 8 10",
            "TEST 3 p1c0 ele app",
            "skill 1 14 13 12",
            "card 3 0 11 10 9 8",
            "skill 0 7 6",
            "TEST 2 p0 summon 2",
            "TEST 2 p1 summon 1",
            "skill 0 5 4",
            "end",
            "card 0 0 15 14 13 12",
            "skill 0 11 10",
            "skill 0 9 8",
            "sw_char 1 7",
            "sw_char 2 6",
            "sw_char 1 5",
            "sw_char 2 4",
            "end",
            "sw_char 1 15",
            "sw_char 2 14",
            "TEST 2 p0 summon 1",
            "sw_char 0 13",
            "skill 2 12 11 10"
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
        charactor:Tighnari
        charactor:Fischl
        charactor:Collei
        Keen Sight*30
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
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].summons) == 1
                assert match.player_tables[pidx].summons[
                    0].usage == int(cmd[-1])
            elif test_id == 3:
                assert match.player_tables[1].charactors[
                    0].element_application == []
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_tighnari()
