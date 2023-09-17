from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_venti():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2",
            "TEST 2 p0 team usage 2",
            "skill 0 0 1 2",
            "card 2 0",
            "sw_char 1",
            "sw_char 0",
            "skill 1 0 1 2",
            "end",
            "card 0 0 0 1 2",
            "sw_char 1",
            "TEST 2 p0 team usage 2",
            "sw_char 0",
            "TEST 2 p0 team usage 1 1",
            "end",
            "sw_char 1",
            "TEST 2 p0 team usage 1",
            "TEST 3 skill 0 cost 2",
            "sw_char 2 0",
            "TEST 3 skill 0 cost 2",
            "sw_char 0 0",
            "TEST 3 skill 0 cost 2",
            "skill 2 0 1 2",
            "skill 0 1 0",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "end",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "skill 0 0 1 2",
            "TEST 4 p0 summon1 element anemo",
            "skill 0 0 1 2",
            "sw_char 0 1",
            "skill 1 0 1 2",
            "TEST 4 p0 summon element hydro",
            "end",
            "end",
            "sw_char 1",
            "sw_char 0",
            "skill 2 0 1 2",
            "TEST 4 p0 summon element hydro",
            "skill 0 1 2",
            "skill 0 1 2 3",
            "skill 2 0 1 2",
            "TEST 4 p0 summon element anemo",
            "end",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "end",
            "skill 0 0 1 2",
            "skill 1 0 1 2",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "skill 0 0 1 2",
            "end",
            "skill 2 0 1 2",
            "sw_char 2",
            "end",
            "sw_char 0",
            "TEST 2 p1 team usage 1",
            "end",
            "sw_char 1 0",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "TEST 4 p1 summon element anemo",
            "end",
            "skill 1 0 1 2",
            "skill 2 0 1 2",
            "sw_char 2",
            "end",
            "sw_char 2",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "sw_char 1 0",
            "sw_char 0 0",
            "TEST 2 p0 team usage 1 1",
            "sw_char 1 0",
            "end",
            "TEST 2 p0 team usage 1 2",
            "end",
            "TEST 2 p0 team usage 1",
            "end",
            "TEST 5 p1 active 2",
            "sw_char 1 0",
            "end",
            "TEST 1 20 90 8 14 67 5",
            "sw_char 1 0",
            "sw_char 0 0",
            "end",
            "sw_char 1 0",
            "end",
            "sw_char 2 0",
            "end",
            "choose 1",
            "end",
            "end",
            "TEST 5 p1 active 0",
            "skill 1 0 1 2",
            "sw_char 1",
            "sw_char 0",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "card 8 0 1 2 3",
            "end",
            "skill 2 0 1 2",
            "end",
            "end",
            "choose 1",
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
        charactor:Venti
        charactor:Barbara
        charactor:Fischl
        Changing Shifts*15
        Embrace of Winds*15
        '''
    )
    deck.charactors[2].hp = 8
    deck.charactors[2].max_hp = 8
    deck.charactors[1].hp = 90
    deck.charactors[1].max_hp = 90
    deck.charactors[0].hp = 20
    deck.charactors[0].max_hp = 20
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
                pidx = int(cmd[2][1])
                usage = [int(x) for x in cmd[5:]]
                status = match.player_tables[pidx].team_status
                assert len(status) == len(usage)
                for s, u in zip(status, usage):
                    assert s.usage == u
            elif test_id == 3:
                cmd = cmd.split()
                sid = int(cmd[3])
                c = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseSkillRequest':
                        if req.skill_idx == sid:
                            assert req.cost.total_dice_cost == c
            elif test_id == 4:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                element = cmd[5].upper()
                assert match.player_tables[pidx].summons[
                    0].damage_elemental_type == element
            elif test_id == 5:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                active = int(cmd[4])
                assert match.player_tables[pidx].active_charactor_idx == active
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_venti_2():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "card 0 0 0 1 2",
            "end",
            "sw_char 0",
            "card 1 0",
            "TEST 3 skill 0 cost 1",
            "skill 0 0",
            "TEST 2 p0 team usage 1 1",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "sw_char 1 0",
            "skill 1 0 1 2",
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
        charactor:Arataki Itto
        charactor:Venti
        charactor:Nahida
        Northern Smoked Chicken*15
        Embrace of Winds*15
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
            elif test_id == 2:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                usage = [int(x) for x in cmd[5:]]
                status = match.player_tables[pidx].team_status
                assert len(status) == len(usage)
                for s, u in zip(status, usage):
                    assert s.usage == u
            elif test_id == 3:
                cmd = cmd.split()
                sid = int(cmd[3])
                c = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseSkillRequest':
                        if req.skill_idx == sid:
                            assert req.cost.total_dice_cost == c
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_venti_2()
