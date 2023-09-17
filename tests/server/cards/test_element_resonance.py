from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_woven_element():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 dendro pyro anemo hydro dendro "
            "cryo dendro electro dendro pyro",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "card 0 0",
            "TEST 2 color match",
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
        charactor:Nahida*3
        Elemental Resonance: Woven Flames*4
        Elemental Resonance: Woven Ice*4
        Elemental Resonance: Woven Stone*4
        Elemental Resonance: Woven Thunder*4
        Elemental Resonance: Woven Waters*4
        Elemental Resonance: Woven Weeds*4
        Elemental Resonance: Woven Winds*4
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

    record = []
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
                colors = [x.upper() for x in cmd.split(' ')[2:]]
                colors = [colors[:5], colors[5:]]
                for i in range(2):
                    for j in range(5):
                        assert match.player_tables[
                            i].hands[j].element == colors[i][j]  # type: ignore
                record = colors
            elif test_id == 2:
                for table, rec in zip(match.player_tables, record):
                    m = {}
                    for r in rec:
                        m[r] = m.get(r, 0) + 1
                    for color in table.dice.colors:
                        if color != 'OMNI':

                            m[color.name] -= 1
                    for v in m.values():
                        assert v == 0
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_enduring_rock():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "skill 1 0 1 2",
            "card 2 0 0",
            "skill 0 0 1 2",
            "TEST 2 p1 5 full plate",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "skill 2 0 1 2 3",
            "TEST 1 9 10 10 9 10 7",
            "TEST 3 p0 4 crystallize",
            "end",
            "card 3 0 0",
            "skill 0 0 1",
            "end",
            "end",
            "end",
            "card 3 0 0",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "TEST 3 p0 1 elemental resonance: enduring rock",
            "end",
            "card 6 0 15",
            "skill 1 14 13 12",
            "sw_char 2 11",
            "skill 1 10 9 8",
            "TEST 7 p1 usage 4 1",
            "end"
        ],
        [
            "sw_card 1 2 3",
            "choose 2",
            "card 0 0 0",
            "skill 0 0 1 2",
            "TEST 4 p1 1 team status",
            "TEST 5 p0 1 full plate 1 geo",
            "skill 1 0 1 2",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "end",
            "skill 0 0 1 2",
            "TEST 3 p0 6 crystallize",
            "card 0 0 0",
            "card 4 0 0",
            "sw_char 1 0",
            "card 0 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 6 p1 1 rebellious shield",
            "end",
            "end",
            "card 5 0 0",
            "skill 1 0 1 2",
            "TEST 6 p1 5 rebellious shield",
            "end",
            "end",
            "card 5 0 15",
            "sw_char 2 14",
            "sw_char 1 13",
            "skill 0 12 11 10",
            "skill 2 9 8 7"
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
        charactor:PyroMobMage
        charactor:Arataki Itto
        charactor:Noelle
        Elemental Resonance: Enduring Rock*15
        The Bell*15
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
                hps = [int(x) for x in cmd.split(' ')[2:]]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id in [2, 3, 6]:
                cmd = cmd.split(' ')
                pid = int(cmd[2][1])
                usage = int(cmd[3])
                found = False
                for status in match.player_tables[pid].team_status:
                    if status.name.lower() == ' '.join(cmd[4:]):
                        assert status.usage == usage
                        found = True
                assert found
            elif test_id == 4:
                assert len(match.player_tables[1].team_status) == 1
            elif test_id == 5:
                assert len(match.player_tables[0].team_status) == 2
                assert match.player_tables[0].team_status[0].usage == 1
                assert match.player_tables[0].team_status[1].usage == 1
            elif test_id == 7:
                cmd = cmd.split()
                pid = int(cmd[2][1])
                usage = [int(x) for x in cmd[4:]]
                status = match.player_tables[pid].team_status
                assert len(status) == len(usage)
                for i in range(len(status)):
                    assert status[i].usage == usage[i]
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_woven_element()
    test_enduring_rock()
