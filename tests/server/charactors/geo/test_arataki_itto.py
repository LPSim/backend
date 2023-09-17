from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_arataki_itto():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "end",
            "sw_char 0 0",
            "sw_char 1 0",
            "sw_char 2 0",
            "sw_char 1 0",
            "sw_char 2 0",
            "TEST 1 10 9 78 10 10 90",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "end",
            "end",
            "end",
            "sw_char 1 0",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "skill 1 0 1 2",
            "choose 2",
            "TEST 1 0 9 40 7 8 90",
            "TEST 2 p1c0 status 2 usage 2 2",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "skill 1 0 1 2",
            "TEST 3 skill 0 cost 3",
            "skill 0 0 1 2",
            "TEST 2 p1c0 status 0 usage ",
            "TEST 1 10 10 84 10 10 90",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "TEST 2 p1c0 status 1 usage 2",
            "end",
            "TEST 3 skill 0 cost 2",
            "skill 1 0 1 2",
            "TEST 3 skill 0 cost 3",
            "sw_char 1 0",
            "sw_char 2 0",
            "sw_char 0 0",
            "TEST 3 skill 0 cost 2",
            "skill 0 0 1",
            "sw_char 1 0",
            "TEST 1 10 9 78 10 8 90",
            "TEST 2 p1c0 status 1 usage 3",
            "sw_char 0 0",
            "end",
            "skill 2 0 1 2",
            "sw_char 1 0",
            "sw_char 2 0",
            "sw_char 0 0",
            "TEST 3 skill 0 cost 2",
            "TEST 2 p1c0 status 2 usage 3 2",
            "skill 0 0 1",
            "TEST 1 10 9 67 10 8 90",
            "TEST 2 p1c0 status 2 usage 3 2",
            "skill 0 0 1",
            "TEST 2 p1c0 status 2 usage 2 2",
            "skill 0 0 1",
            "skill 2 0 1 2",
            "TEST 4 burst status renew usage",
            "end",
            "skill 1 0 1 2",
            "TEST 2 p1c0 status 2 usage 2 1",
            "skill 0 0 1 2",
            "TEST 2 p1c0 status 2 usage 3 1",
            "TEST 5 card cost 3",
            "card 0 0 0 1 2",
            "TEST 1 10 9 41 10 8 90",
            "end",
            "skill 2 0 1 2",
            "skill 0 0 1 2",
            "TEST 2 p1c0 status 2 usage 3 2",
            "skill 0 0 1"
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
        charactor:PhysicalMob
        charactor:Mona
        Arataki Ichiban*30
        '''
    )
    deck.charactors[2].hp = 90
    deck.charactors[2].max_hp = 90
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
                cmd = cmd.strip().split()
                pc = cmd[2]
                status = int(cmd[4])
                usage = [int(x) for x in cmd[6:]]
                pidx = int(pc[1])
                cidx = int(pc[3])
                charactor = match.player_tables[pidx].charactors[cidx]
                assert len(charactor.status) == status
                for s, u in zip(charactor.status, usage):
                    assert s.usage == u
            elif test_id == 3:
                cmd = cmd.strip().split()
                sidx = int(cmd[3])
                cost = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseSkillRequest':
                        if req.skill_idx == sidx:
                            assert req.cost.total_dice_cost == cost
                            assert req.cost.elemental_dice_number == 1
            elif test_id == 4:
                charactor = match.player_tables[1].charactors[0]
                for status in charactor.status:
                    if status.name == 'Raging Oni King':
                        assert status.status_increase_usage == 1
            elif test_id == 5:
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        assert req.cost.total_dice_cost == 3
                        assert req.cost.elemental_dice_number == 1
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_arataki_itto_2():
    cmd_records = [
        [
            "sw_card",
            "choose 2",
            "end",
            "end",
            "end",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
        ],
        [
            "sw_card 0 1 2 3",
            "choose 1",
            "skill 1 0 1 2",
            "skill 0 0 1 2",
            "card 0 0 0 1 2",
            "TEST 1 10 10 83 10 10 90",
            "end",
            "card 0 1 0",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "skill 0 0 1 2",
            "skill 0 0 1",
            "TEST 1 10 10 74 10 10 90",
            "end",
            "skill 0 0 1 2",
            "TEST 1 10 10 70 10 10 90",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 10 10 66 10 10 90",
            "end",
            "skill 1 0 1 2",
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
        charactor:PhysicalMob
        charactor:Arataki Itto
        charactor:Mona
        Arataki Ichiban*15
        Lotus Flower Crisp*15
        '''
    )
    deck.charactors[2].hp = 90
    deck.charactors[2].max_hp = 90
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
    test_arataki_itto()
    test_arataki_itto_2()
