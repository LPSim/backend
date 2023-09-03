from agents.interaction_agent import InteractionAgent
from server.match import Match, MatchState
from server.deck import Deck
from tests.utils_for_test import (
    get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_seelie():
    # use frontend and FastAPI server to perform commands, and test commands 
    # that start with TEST. NO NOT put TEST at the end of command list!
    # If a command is succesfully performed, frontend will print history 
    # commands in console. Note that frontend cannot distinguish if a new
    # match begins, so you need to refresh the page before recording a new
    # match, otherwise the history commands will be mixed.
    #
    # for tests, it starts with TEST and contains a test id, which is used to
    # identify the test. Other texts in the command are ignored, but you can
    # parse them if you want. Refer to the following code.
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "card 0 0 0",
            "skill 1 0 1 2",
            "skill 0 0 1 2",
            "end",
            "skill 0 0 1 2",
            "TEST 2 card number 9 10",
            "end"
        ],
        [
            "sw_card",
            "choose 2",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "card 0 0 0",
            "card 0 0 0",
            "skill 1 0 1 2",
            "TEST 1 all support usage 1",
            "skill 1 0 1 2",
            "end",
            "sw_char 0 0",
            "TEST 3 card number 9 5",
            "skill 0 0 1 2"
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
        charactor:Noelle*3
        Treasure-Seeking Seelie*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
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
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                num = [1, 2]
                for table, n in zip(match.player_tables, num):
                    assert n == len(table.supports)
                    for support in table.supports:
                        assert support.usage == 1
            elif test_id == 2:
                assert len(match.player_tables[0].hands) == 9
                assert len(match.player_tables[1].hands) == 10
            elif test_id == 3:
                assert len(match.player_tables[0].hands) == 9
                assert len(match.player_tables[1].hands) == 5
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_seelie()
