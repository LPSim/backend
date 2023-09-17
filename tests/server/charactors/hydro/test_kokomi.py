from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_kokomi():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "sw_char 2 11",
            "sw_char 1 10",
            "skill 0 9 8 7",
            "TEST 1 9 7 10 10 10 10",
            "skill 0 6 5 4",
            "TEST 1 9 5 10 10 10 10",
            "end",
            "TEST 1 9 4 10 10 10 10",
            "skill 2 15 14 13",
            "sw_char 0 12",
            "skill 0 11 10 9",
            "skill 2 8 7 6",
            "TEST 1 10 5 10 10 4 10",
            "skill 0 5 4 3",
            "skill 0 2 1 0",
            "end",
            "sw_char 2 15",
            "skill 0 14 13 12",
            "end",
            "TEST 1 10 7 1 10 0 10",
            "sw_char 0 15",
            "TEST 2 p1 summon 2",
            "end",
            "end",
            "skill 1 15 14 13",
            "end",
            "end",
            "TEST 1 4 7 1 9 0 10",
            "end"
        ],
        [
            "sw_card 2 3",
            "choose 1",
            "TEST 3 p0c0 ele app hydro",
            "skill 0 15 14 13",
            "skill 1 12 11 10",
            "sw_char 2 9",
            "sw_char 1 8",
            "card 3 0",
            "card 1 0 7 6 5",
            "skill 0 4 3 2",
            "end",
            "end",
            "choose 2",
            "TEST 1 10 7 10 10 0 9",
            "sw_char 0 15",
            "skill 1 14 13 12",
            "skill 0 11 10 9",
            "card 1 0 8 7 6",
            "skill 0 5 4 3",
            "skill 0 2 1 0",
            "end",
            "skill 2 15 14 13",
            "end",
            "skill 1 15 14 13",
            "end",
            "end",
            "skill 1 15 14 13",
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
        charactor:Sangonomiya Kokomi
        charactor:Sangonomiya Kokomi@3.5
        charactor:Qiqi
        Tamakushi Casket*15
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
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                assert len(match.player_tables[1].summons) == 1
                assert match.player_tables[1].summons[0].usage == 2
            elif test_id == 3:
                assert match.player_tables[0].charactors[
                    0].element_application == ['HYDRO']
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_kokomi()
