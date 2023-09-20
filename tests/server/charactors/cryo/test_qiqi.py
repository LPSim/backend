from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_qiqi():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "end",
            "choose 0",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "sw_char 1 9",
            "sw_char 0 8",
            "skill 0 7 6 5",
            "skill 0 4 3 2",
            "TEST 1 8 6 0 6 8 10",
            "end",
            "skill 2 15 14 13",
            "skill 0 12 11 10",
            "sw_char 1 9",
            "skill 1 8 7 6 5 4",
            "TEST 1 5 1 0 3 3 7",
            "sw_char 0 3",
            "skill 0 2 1 0",
            "end",
            "skill 1 15 14 13",
            "card 0 0 12 11 10 9 8",
            "skill 0 7 6 5",
            "skill 0 4 3 2",
            "sw_char 2 1",
            "end",
            "sw_char 0 15",
            "skill 1 14 13 12",
            "skill 1 11 10 9",
            "skill 1 8 7 6",
            "skill 2 5 4 3",
            "end",
            "sw_char 2 15",
            "TEST 1 4 2 1 3 3 3",
            "end",
            "choose 0",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "skill 1 9 8 7",
            "skill 2 6 5 4",
            "skill 1 3 2 1",
            "end",
            "sw_char 2 15",
            "choose 1",
            "skill 1 14 13 12 11 10",
            "choose 0",
            "TEST 1 7 0 0 5 2 4",
            "skill 1 9 8 7",
            "skill 1 6 5 4",
            "skill 2 3 2 1"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 1 15 14 13 12 11",
            "skill 1 10 9 8 7 6",
            "end",
            "sw_char 0 15",
            "TEST 1 8 8 0 8 8 10",
            "skill 1 14 13 12",
            "skill 0 11 10 9",
            "skill 0 8 7 6",
            "end",
            "sw_char 2 15",
            "TEST 1 6 5 0 5 8 7",
            "sw_char 0 14",
            "card 4 0 13 12 11 10 9",
            "sw_char 1 8",
            "skill 1 7 6 5 4 3",
            "sw_char 2 2",
            "end",
            "sw_char 0 15",
            "skill 1 14 13 12",
            "TEST 1 6 2 2 2 3 4",
            "TEST 2 p0cp skill2 revive usage 1",
            "skill 1 11 10 9",
            "sw_char 2 8",
            "TEST 1 10 2 4 2 3 2",
            "end",
            "sw_char 0 15",
            "skill 1 14 13 12",
            "TEST 3 p0 usage 1",
            "skill 1 11 10 9",
            "sw_char 2 8",
            "skill 0 7 6 5",
            "choose 0",
            "TEST 1 8 2 3 2 3 0",
            "skill 2 4 3 2",
            "end",
            "skill 0 15 14 13",
            "end",
            "skill 1 15 14 13",
            "skill 1 12 11 10",
            "skill 2 9 8 7",
            "TEST 1 7 2 2 3 3 3",
            "skill 1 6 5 4",
            "skill 1 3 2 1",
            "end",
            "skill 0 15 14 13",
            "skill 2 12 11 10",
            "skill 0 9 8 7",
            "skill 1 6 5 4",
            "skill 1 3 2 1",
            "TEST 1 9 0 0 5 1 3",
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
        charactor:Qiqi
        charactor:Electro Hypostasis
        charactor:Fischl
        Rite of Resurrection*30
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
                charactor = match.player_tables[0].charactors[0]
                skill = charactor.skills[2]
                assert skill.revive_usage == 1  # type: ignore
            elif test_id == 3:
                assert len(match.player_tables[0].team_status) == 1
                assert match.player_tables[0].team_status[0].usage == 1
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_qiqi()
