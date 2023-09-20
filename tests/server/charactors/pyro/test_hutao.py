from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_hutao():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "sw_char 0 15",
            "TEST 1 10 10 10 10 10 10",
            "skill 0 14 13 12",
            "skill 1 11 10",
            "sw_char 1 9",
            "skill 0 8 7 6",
            "skill 0 5 4 3",
            "skill 0 2 1 0",
            "card 2 1",
            "end",
            "TEST 1 6 6 10 5 10 10",
            "sw_char 2 15",
            "TEST 1 6 6 3 8 10 10",
            "sw_char 0 14",
            "skill 0 13 12 11",
            "skill 2 10 9 8",
            "skill 1 7 6",
            "skill 1 5 4",
            "skill 1 3 2",
            "end",
            "skill 2 15 14 13",
            "skill 1 12 11",
            "skill 1 10 9",
            "card 0 0 8 7",
            "skill 2 6 5 4",
            "TEST 1 10 6 3 0 0 10",
            "end",
            "end",
            "skill 0 15 14 13",
            "TEST 1 5 6 3 0 0 8",
            "end"
        ],
        [
            "sw_card 2 3",
            "choose 0",
            "card 3 0 15 14",
            "skill 0 13 12 11",
            "skill 1 10 9",
            "skill 2 8 7 6",
            "skill 1 5 4",
            "skill 1 3 2",
            "skill 1 1 0",
            "card 1 0",
            "end",
            "skill 2 15 14 13",
            "end",
            "choose 1",
            "end",
            "choose 2",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "end",
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
        charactor:Hu Tao
        charactor:Keqing
        charactor:Qiqi
        Sweet Madame*15
        Sanguine Rouge*15
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
    test_hutao()
