from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_jean():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "sw_char 0 12",
            "skill 0 11 10 9",
            "skill 0 8 7 6",
            "card 0 0",
            "sw_char 2 5",
            "skill 1 4 3 2",
            "end",
            "sw_char 0 15",
            "TEST 1 4 10 8 6 10 9",
            "card 0 0",
            "sw_char 2 14",
            "sw_char 1 13",
            "TEST 1 5 9 8 6 10 9",
            "sw_char 0 12",
            "card 0 0 11 10 9 8",
            "sw_char 0 7",
            "sw_char 0 6",
            "skill 1 5 4 3",
            "skill 1 2 1 0",
            "TEST 1 1 10 10 2 10 5",
            "end",
            "choose 1",
            "end",
            "TEST 1 0 7 9 2 8 5",
            "sw_char 2 15",
            "skill 1 14 13 12",
            "skill 1 11 10 9",
            "sw_char 2 8",
            "skill 1 7 6 5",
            "skill 1 4 3 2",
            "end",
            "sw_char 1 15",
            "sw_char 2 14",
            "sw_char 1 13",
            "card 5 1",
            "card 3 0",
            "end",
            "card 8 1",
            "TEST 1 0 3 3 5 4 0",
            "end",
            "card 3 0",
            "end",
            "card 4 0",
            "end",
            "card 4 0",
            "skill 1 15 14 13",
            "end"
        ],
        [
            "sw_card 1 3",
            "choose 0",
            "sw_char 0 15",
            "skill 1 14 13 12",
            "skill 0 11 10 9",
            "skill 0 8 7 6",
            "card 3 0",
            "sw_char 2 5",
            "skill 1 4 3 2",
            "end",
            "sw_char 0 15",
            "skill 2 14 13 12 11",
            "sw_char 2 10",
            "skill 0 9 8 7",
            "skill 1 6 5 4",
            "skill 1 3 2 1",
            "end",
            "TEST 1 0 10 10 2 8 5",
            "skill 1 15 14 13",
            "end",
            "sw_char 2 15",
            "sw_char 2 14",
            "skill 1 13 12 11",
            "sw_char 1 10",
            "sw_char 2 9",
            "sw_char 0 8",
            "skill 0 7 6 5",
            "skill 0 4 3 2",
            "end",
            "skill 0 15 14 13",
            "skill 2 12 11 10 9",
            "end",
            "skill 1 15 14 13",
            "end",
            "end",
            "end",
            "sw_char 0 15",
            "skill 1 14 13 12"
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
        charactor:Jean
        charactor:Mona
        charactor:Sucrose
        Lands of Dandelion*15
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
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_jean()
