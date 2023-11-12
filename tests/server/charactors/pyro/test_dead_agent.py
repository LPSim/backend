from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_dead_agent():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "TEST 2 p0 2 3 p1 2 3",
            "skill 0 0 1 2",
            "TEST 2 p0 0 3 p1 2 1",
            "TEST 3 p0c0 pyro",
            "card 0 0 0 1 2",
            "skill 1 0 1 2",
            "TEST 1 7 10 10 10 9 8 10 10",
            "skill 2 0 1 2",
            "sw_char 1 0",
            "TEST 1 7 9 10 10 4 8 10 10",
            "TEST 3 p1c1 pyro",
            "skill 1 0 1 2",
            "end",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "TEST 2 p0 1 3 p1 2 2",
            "TEST 1 10 10 10 10 10 8 10 10",
            "skill 0 0 1 2",
            "TEST 1 8 10 10 10 10 8 10 10",
            "TEST 2 p0 3 3 p1 2 0",
            "sw_char 0 0",
            "TEST 1 8 10 10 10 9 8 10 10",
            "skill 1 0 1 2",
            "TEST 1 7 10 10 10 4 8 10 10",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "sw_char 3 0",
            "end",
            "skill 1 0 1 2",
            "TEST 1 7 6 10 10 4 6 10 10",
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
        charactor:Fatui Pyro Agent*2
        charactor:Nahida
        charactor:Fischl
        Paid in Full*30
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
    # equip talent initially for agent c1
    for table in match.player_tables:
        charactor = table.charactors[1]
        assert charactor.name == 'Fatui Pyro Agent'
        from src.lpsim.server.charactor.pyro.fatui_pyro_agent_3_3 import (
            PaidinFull_3_3
        )
        from src.lpsim.server.consts import ObjectPositionType
        from src.lpsim.server.struct import ObjectPosition
        charactor.talent = PaidinFull_3_3(name = 'Paid in Full')
        charactor.talent.position = ObjectPosition(
            player_idx = charactor.position.player_idx,
            charactor_idx = charactor.position.charactor_idx,
            area = ObjectPositionType.CHARACTOR,
            id = charactor.talent.id
        )
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
                cmd = cmd.strip().split(' ')[3:]
                cmd = cmd[:2] + cmd[3:]
                data = [int(x) for x in cmd]
                data = [data[:2], data[2:]]
                for table, d in zip(match.player_tables, data):
                    for c, u in zip(table.charactors, d):
                        if u == 0:
                            assert len(c.status) == 0
                            continue
                        assert c.status[0].usage == u
            elif test_id == 3:
                cmd = cmd.strip().split(' ')[2]
                pid = int(cmd[1])
                cid = int(cmd[3])
                assert match.player_tables[pid].charactors[
                    cid].element_application == ['PYRO']
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_dead_agent()
