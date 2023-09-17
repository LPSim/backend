from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_chongyun():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "skill 0 11 10 9",
            "sw_char 0 8",
            "TEST 1 5 7 10 8 8 10",
            "sw_char 2 7",
            "skill 0 6 5 4",
            "TEST 1 5 7 8 8 8 8",
            "sw_char 0 3",
            "end",
            "card 2 0 15 14 13 12",
            "sw_char 1 11",
            "skill 0 10 9 8",
            "sw_char 2 7",
            "TEST 1 2 7 1 5 5 8",
            "end"
        ],
        [
            "sw_card 2 3 4",
            "choose 1",
            "skill 0 15 14 13",
            "sw_char 0 12",
            "TEST 1 8 10 10 8 7 10",
            "TEST 2 p1c0 p1c1 cryo",
            "card 2 1",
            "card 1 0 11 10 9 8",
            "skill 0 7 6 5",
            "sw_char 2 4",
            "skill 0 3 2 1",
            "end",
            "sw_char 0 15",
            "skill 1 14 13 12",
            "sw_char 1 11",
            "TEST 1 2 7 8 5 5 8",
            "sw_char 0 10",
            "skill 2 5 4 3"
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
        charactor:Chongyun
        charactor:Shenhe
        charactor:Fischl
        Steady Breathing*15
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
                for tid, table in enumerate(match.player_tables):
                    for cid, charactor in enumerate(table.charactors):
                        if (tid == 1 and (cid == 0 or cid == 1)):
                            assert charactor.element_application == ['CRYO']
                        else:
                            assert charactor.element_application == []
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_chongyun()
