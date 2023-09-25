from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, check_usage, get_random_state, get_test_id_from_command, 
    make_respond, set_16_omni
)


def test_abyss_fire():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "card 4 0",
            "card 0 0 9 8",
            "skill 2 7 6 5 4",
            "skill 1 3 2 1",
            "TEST 1 4 8 10 2 8 2",
            "TEST 2 p0c0 status 1 2",
            "end",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "card 1 0",
            "end"
        ],
        [
            "sw_card 2 1",
            "choose 2",
            "card 3 0 15 14",
            "skill 1 13 12 11",
            "skill 1 10 9 8",
            "TEST 1 4 8 10 6 8 2",
            "sw_char 0 7",
            "skill 0 6 5 4",
            "end",
            "TEST 2 p1c0 status 3",
            "skill 1 15 14 13",
            "TEST 1 2 8 10 3 7 1",
            "TEST 2 p1c0 status 2",
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
        charactor:Abyss Lector: Fathomless Flames
        charactor:Electro Hypostasis
        charactor:Klee
        Sweet Madame*15
        Embers Rekindled*15
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
                pidx, cidx = int(cmd[2][1]), int(cmd[2][3])
                status = match.player_tables[pidx].charactors[cidx].status
                check_usage(status, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_abyss_fire()
