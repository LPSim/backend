from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_candace():
    cmd_records = [
        [
            "sw_card",
            "choose 3",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "skill 1 9 8 7",
            "TEST 1 10 10 10 7 10 10 10 10 7 9 7 10",
            "sw_char 1 6",
            "skill 0 5 4 3",
            "sw_char 2 2",
            "end",
            "TEST 1 10 10 7 7 10 10 10 10 7 10 7 10",
            "sw_char 3 15",
            "sw_char 0 14",
            "TEST 1 7 10 7 5 10 10 10 10 7 10 7 10",
            "sw_char 4 13",
            "TEST 1 7 10 7 5 9 10 10 10 7 10 7 10",
            "TEST 2 p0c0 eleapp hydro",
            "TEST 2 p0c4 eleapp hydro",
            "sw_char 5 12",
            "TEST 1 7 10 7 5 9 7 10 10 7 10 7 10",
            "TEST 2 p0c5 eleapp",
            "sw_char 3 11",
            "TEST 1 7 10 7 5 9 7 10 10 7 10 7 10",
            "card 1 0 10 9 8 7",
            "sw_char 1 6",
            "skill 0 5 4 3",
            "skill 0 2 1 0",
            "end",
            "skill 0 15 14 13",
            "TEST 1 7 6 7 5 9 7 8 4 6 6 7 10",
            "sw_char 3 12",
            "skill 1 11 10 9",
            "skill 1 8 7 6",
            "skill 2 5 4 3",
            "choose 4",
            "TEST 1 7 6 7 0 9 7 8 4 3 2 4 10",
            "skill 1 2 1 0",
            "end"
        ],
        [
            "sw_card 3 4",
            "choose 2",
            "TEST 1 10 10 10 10 10 10 10 10 10 10 10 10",
            "sw_char 4 15",
            "TEST 1 10 10 10 10 10 10 10 10 10 10 7 10",
            "sw_char 2 14",
            "skill 0 13 12 11",
            "TEST 1 10 10 10 10 10 10 10 10 7 10 7 10",
            "sw_char 3 10",
            "skill 1 9 8 7",
            "skill 1 6 5 4",
            "card 1 1",
            "end",
            "skill 2 15 14 13",
            "skill 0 12 11 10",
            "sw_char 5 9",
            "skill 0 8 7 6",
            "sw_char 0 5",
            "sw_char 2 4",
            "TEST 1 7 10 7 5 9 7 8 10 6 10 7 10",
            "sw_char 3 3",
            "TEST 1 7 10 7 5 9 7 8 10 6 6 7 10",
            "sw_char 1 2",
            "TEST 1 7 10 7 5 9 7 8 8 6 6 7 10",
            "end",
            "skill 0 15 14 13",
            "TEST 1 7 8 7 5 9 7 8 4 6 6 7 10",
            "sw_char 3 12",
            "skill 1 11 10 9",
            "skill 2 8 7 6",
            "sw_char 2 5",
            "TEST 1 7 6 7 2 9 7 8 4 3 2 7 10",
            "sw_char 4 4",
            "skill 0 3 2 1",
            "choose 5",
            "TEST 1 7 6 7 0 9 7 8 4 3 2 0 10",
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
        charactor:Candace
        charactor:CryoMobMage
        charactor:Candace*2
        charactor:Diluc
        charactor:Fischl
        Sweet Madame*15
        The Overflow*15
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
                hps = [hps[:6], hps[6:]]
                check_hp(match, hps)
            elif test_id == 2:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                cidx = int(cmd[2][3])
                ele = [x.upper() for x in cmd[4:]]
                assert match.player_tables[pidx].charactors[
                    cidx].element_application == ele
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_candace()
