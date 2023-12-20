from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_four_leaf():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "card 1 1",
            "end",
            "TEST 1 active 1 0",
            "card 2 0",
            "end",
            "TEST 1 active 0 1",
            "card 2 2",
            "end",
            "TEST 1 active 2 0",
            "end",
            "choose 1",
            "TEST 2 card target no 2",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "card 3 0",
            "end",
            "sw_char 2 15",
            "card 1 1",
            "end",
            "card 3 2",
            "end",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "skill 1 11 10 9",
            "skill 1 8 7 6",
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
        default_version:4.3
        charactor:Shenhe
        charactor:Chongyun
        charactor:Nahida
        Flickering Four-Leaf Sigil*10
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
            cmd = agent.commands[0].strip().split(' ')
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                assert int(
                    cmd[-2]) == match.player_tables[0].active_charactor_idx
                assert int(
                    cmd[-1]) == match.player_tables[1].active_charactor_idx
            elif test_id == 2:
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert len(req.targets) == 2
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_four_leaf()
