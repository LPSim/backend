
from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_rhodeia():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "skill 2 0 1 2 3 4",
            "TEST 2 p0 summon 2 usage",
            "TEST 2 p1 summon 2 usage",
            "skill 2 0 1 2 3 4",
            "end",
            "TEST 2 p0 summon 3 usage",
            "TEST 2 p1 summon 2 usage",
            "skill 2 0 1 2 3 4",
            "TEST 2 p0 summon 3 usage 0 2 3",
            "TEST 2 p1 summon 3 usage 2 2 2",
            "TEST 1 10 87 10 10 89 10",
            "card 0 0 0 1 2 3",
            "TEST 2 p0 summon 3 usage 0 3 4",
            "TEST 2 p1 summon 3 usage 3 3 2",
            "skill 0 0 1 2",
            "end",
            "TEST 1 10 74 10 10 78 10",
            "TEST 2 p0 summon 2 usage",
            "TEST 2 p1 summon 2 usage",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "skill 3 0 1 2",
            "TEST 1 8 68 10 9 66 9",
            "TEST 2 p0 summon 4 usage 3 4 3 3",
            "end",
            "end",
            "end",
            "end",
            "end",
            "end",
            "skill 2 0 1 2 3 4",
            "skill 1 0 1 2",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 2 0 1 2 3 4",
            "skill 2 0 1 2 3 4",
            "end",
            "skill 2 0 1 2 3 4",
            "card 0 0 0 1 2 3",
            "skill 0 0 1 2",
            "end",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 3 0 1 2",
            "end",
            "TEST 2 p0 summon 4 usage 2 3 2 1",
            "TEST 1 8 67 10 8 61 8",
            "end",
            "end",
            "end",
            "end",
            "skill 1 0 1 2",
            "skill 2 0 1 2 3 4",
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
        charactor:Fischl
        charactor:Rhodeia of Loch
        charactor:Nahida
        # Mushroom Pizza*30
        Streaming Surge*30
        '''
    )
    deck.charactors[1].hp = 90
    deck.charactors[1].max_hp = 90
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
                pnum = int(cmd[2][1])
                snum = int(cmd[4])
                unum = [int(x) for x in cmd[6:]]
                summons = match.player_tables[pnum].summons
                assert len(summons) == snum
                for s, u in zip(summons, unum):
                    assert s.usage == u
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_rhodeia()
