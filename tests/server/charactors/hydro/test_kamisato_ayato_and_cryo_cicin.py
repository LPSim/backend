from src.lpsim.agents import InteractionAgent
from src.lpsim import Deck, Match, MatchState
from tests.utils_for_test import (
    check_hp, check_usage, get_pidx_cidx, get_random_state, 
    get_test_id_from_command, make_respond, set_16_omni
)


def test_ayato_fatui_cryo_cicin():
    cmd_records = [
        [
            "sw_card 1 2",
            "choose 0",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7",
            "skill 0 6 5 4",
            "skill 0 3 2 1",
            "TEST 1 2 10 10 10 6 3 8 10",
            "sw_char 1 0",
            "TEST 1 2 7 10 10 6 3 8 10",
            "end",
            "sw_char 2 15",
            "sw_char 3 14",
            "skill 1 13 12 11",
            "sw_char 2 10",
            "TEST 1 2 7 4 9 6 2 8 9",
            "TEST 4 p0 summon usage 1 1",
            "TEST 4 p1 summon usage 2 3",
            "sw_char 1 9",
            "TEST 1 2 2 4 9 6 2 8 9",
            "sw_char 0 8",
            "choose 2",
            "card 2 1",
            "TEST 1 0 2 5 9 6 2 8 9",
            "end",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "choose 2",
            "TEST 4 p0 summon usage 2",
            "sw_char 3 11",
            "TEST 4 p0 summon usage 1",
            "card 5 1",
            "end",
            "TEST 1 0 0 1 5 4 3 8 9",
            "skill 0 15 14 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7",
            "TEST 3 p0c3 eleapp",
            "end",
            "skill 1 15 14 13",
            "card 3 0 12 11 10",
            "sw_char 2 9",
            "sw_char 3 8",
            "end",
            "card 6 1",
            "card 8 0",
            "end",
            "skill 1 15 14 13"
        ],
        [
            "sw_card 2 3",
            "choose 2",
            "sw_char 0 15",
            "skill 0 14 13 12",
            "TEST 1 8 10 10 10 6 11 8 10",
            "TEST 2 p0c0 usage 2",
            "sw_char 1 11",
            "card 3 0 10 9 8",
            "skill 0 7 6 5",
            "skill 0 4 3 2",
            "card 0 1",
            "end",
            "skill 2 15 14 13",
            "sw_char 3 12",
            "card 3 0 11 10 9",
            "skill 0 8 7 6",
            "skill 0 5 4 3",
            "skill 2 2 1 0",
            "card 0 1",
            "end",
            "sw_char 0 15",
            "skill 1 14 13 12",
            "skill 1 11 10 9",
            "end",
            "sw_char 1 15",
            "sw_char 2 14",
            "TEST 1 0 0 1 5 3 1 2 9",
            "sw_char 0 13",
            "end",
            "sw_char 1 15",
            "choose 2",
            "choose 0",
            "TEST 1 0 0 1 5 2 0 0 9",
            "end",
            "sw_char 3 15",
            "card 6 1",
            "card 4 0",
            "end",
            "TEST 1 0 0 2 6 2 0 0 8",
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
        default_version:4.1
        charactor:Kamisato Ayato
        charactor:Kamisato Ayato@3.6
        charactor:Fatui Cryo Cicin Mage
        charactor:Fatui Cryo Cicin Mage@3.7
        Sweet Madame*10
        Cicin's Cold Glare*10
        Kyouka Fuushi*10
        '''
    )
    # bug in usage, so modify deck p1c1 max hp.
    deck2 = deck.copy(deep = True)
    deck2.charactors[1].max_hp = deck2.charactors[1].hp = 11
    match.set_deck([deck, deck2])
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
                hps = [hps[:4], hps[4:]]
                check_hp(match, hps)
            elif test_id == 2:
                cmd = cmd.split()
                pidx, cidx = get_pidx_cidx(cmd)
                status = match.player_tables[pidx].charactors[cidx].status
                check_usage(status, cmd[4:])
            elif test_id == 3:
                assert match.player_tables[0].charactors[
                    0].element_application == []
            elif test_id == 4:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                status = match.player_tables[pidx].summons
                check_usage(status, cmd[5:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_ayato_fatui_cryo_cicin()
