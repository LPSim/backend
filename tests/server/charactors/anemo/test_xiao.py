from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_xiao():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "skill 0 9 8 7",
            "sw_char 1 6",
            "skill 0 5 4 3",
            "skill 0 2 1 0",
            "TEST 1 30 19 28 29 25 29",
            "card 0 0",
            "card 0 0",
            "end",
            "skill 2 15 14 13",
            "skill 0 12 11 10",
            "TEST 1 30 15 29 27 21 24",
            "sw_char 2",
            "sw_char 0 9",
            "sw_char 2 8",
            "sw_char 0 7",
            "end",
            "sw_char 2 15",
            "sw_char 1 14",
            "sw_char 0",
            "sw_char 1 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7",
            "skill 1 6 5 4",
            "TEST 1 22 10 16 27 7 24",
            "end",
            "sw_char 2",
            "sw_char 1 15",
            "sw_char 2 14",
            "sw_char 1 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7",
            "sw_char 2",
            "sw_char 1 6"
        ],
        [
            "sw_card 2",
            "choose 0",
            "sw_char 2 15",
            "sw_char 1 14",
            "skill 0 13 12 11",
            "skill 1 10 9 8",
            "TEST 1 30 27 28 29 27 29",
            "skill 2 7 6 5",
            "skill 1 4 3 2",
            "sw_char 2",
            "sw_char 1 1",
            "sw_char 2 0",
            "end",
            "sw_char 1 15",
            "TEST 1 30 20 29 27 21 24",
            "skill 0 14 13 12",
            "card 1 0 11 10 9",
            "skill 1 8 7",
            "skill 1 6 5",
            "skill 1 4 3 2",
            "end",
            "skill 1 15 14 13",
            "sw_char 2",
            "sw_char 1 12",
            "skill 0 11 10 9",
            "TEST 1 22 10 16 27 16 24",
            "end",
            "sw_char 2 15",
            "sw_char 1 14",
            "sw_char 2 13",
            "sw_char 1 12",
            "sw_char 0 11",
            "sw_char 2 10",
            "sw_char 0 9",
            "sw_char 2 8",
            "TEST 1 22 10 16 21 5 18",
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
        charactor:Amber
        charactor:Xiao
        charactor:Yae Miko
        Conqueror of Evil: Guardian Yaksha*15
        Sweet Madame*15
        '''
    )
    # change HP
    for charactor in deck.charactors:
        charactor.max_hp = 30
        charactor.hp = 30
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
    test_xiao()
