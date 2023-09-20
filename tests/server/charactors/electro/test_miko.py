from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_miko():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "end",
            "TEST 1 8 10 10 10 8 10",
            "TEST 2 p0 summon 4",
            "TEST 2 p1 summon 2",
            "card 0 0 15 14 13",
            "TEST 1 8 10 10 10 4 7",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "skill 1 6",
            "end",
            "end",
            "end",
            "sw_char 2 15",
            "skill 1 14 13 12",
            "sw_char 0 11",
            "end",
            "skill 1 15 14 13",
            "choose 1",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "skill 2 6 5 4",
            "TEST 1 0 10 10 10 0 0",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13",
            "TEST 1 10 10 10 10 10 10",
            "TEST 2 p0 summon 6",
            "TEST 2 p1 summon 3",
            "skill 0 12 11 10",
            "TEST 1 9 10 10 10 9 10",
            "TEST 2 p0 summon 5",
            "end",
            "TEST 1 8 10 10 10 4 10",
            "sw_char 2 15",
            "sw_char 1 14",
            "skill 1 13 12 11",
            "sw_char 2 10",
            "TEST 2 p1 summon 5",
            "end",
            "end",
            "end",
            "end",
            "sw_char 1 15",
            "skill 2 14 13 12",
            "TEST 1 0 10 10 10 2 1",
            "skill 1 11 10 9",
            "end",
            "choose 2",
            "choose 0"
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
        charactor:Yae Miko
        charactor:Yae Miko
        charactor:Fischl
        The Shrine's Sacred Shade*30
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
                pid = int(cmd[2][1])
                usage = int(cmd[-1])
                assert match.player_tables[pid].summons[0].usage == usage
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_miko()
