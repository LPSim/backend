from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_vermillion_shimenawa():
    cmd_records = [
        [
            "sw_card 1",
            "choose 0",
            "card 2 0 15 14 13",
            "TEST 2 skill 1 cost 2",
            "TEST 2 skill 0 cost 3",
            "skill 1 12 11",
            "TEST 2 skill 1 cost 3",
            "TEST 1 10 10 10 10 8 10",
            "skill 1 10 9 8",
            "TEST 3 p1c0 status 1",
            "skill 0 7 6 5",
            "TEST 1 8 10 10 7 6 10",
            "skill 2 4 3 2",
            "TEST 1 6 10 10 6 6 10",
            "TEST 4 p0 team usage 3",
            "end",
            "sw_char 1 15",
            "sw_char 2 14",
            "sw_char 1 13",
            "sw_char 0 12",
            "TEST 3 p1c0 usage 1",
            "sw_char 1 11",
            "skill 1 10 9 8",
            "TEST 1 4 8 10 6 7 10",
            "end"
        ],
        [
            "sw_card 1",
            "choose 1",
            "card 1 1 15 14",
            "TEST 2 skill 0 cost 2",
            "TEST 2 skill 1 cost 3",
            "skill 1 13 12 11",
            "card 0 0 10 9 8",
            "sw_char 0 7",
            "TEST 1 10 10 10 7 6 10",
            "skill 0 6 5",
            "TEST 1 8 10 10 6 6 10",
            "skill 0 4 3 2",
            "end",
            "sw_char 2 15",
            "sw_char 0 14",
            "sw_char 1 13",
            "sw_char 0 12",
            "sw_char 1 11",
            "skill 0 10 9"
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
        charactor:Xingqiu
        charactor:Qiqi
        charactor:Yae Miko
        Capricious Visage*5
        Shimenawa's Reminiscence*5
        Thundering Poise*5
        Vermillion Hereafter*5
        Capricious Visage@3.7*5
        Shimenawa's Reminiscence@3.7*5
        Thundering Poise@3.7*5
        Vermillion Hereafter@3.7*5
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
                sid = int(cmd[3])
                cost = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseSkillRequest' and req.skill_idx == sid:
                        assert req.cost.total_dice_cost == cost
            elif test_id == 3:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                cidx = int(cmd[2][3])
                usage = [int(x) for x in cmd[4:]]
                status = match.player_tables[pidx].charactors[cidx].status
                assert len(usage) == len(status)
                for u, s in zip(usage, status):
                    assert u == s.usage
            elif test_id == 4:
                cmd = cmd.split()
                pidx = int(cmd[2][1])
                usage = [int(x) for x in cmd[5:]]
                status = match.player_tables[pidx].team_status
                assert len(usage) == len(status)
                for u, s in zip(usage, status):
                    assert u == s.usage
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_vermillion_shimenawa_2():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "card 3 1 15 14 13",
            "TEST 2 card 0 cost 1",
            "sw_char 0 12",
            "card 0 0 11",
            "sw_char 1",
            "skill 1 10 9 8",
            "TEST 1 10 7 10 10 6 10",
            "end",
            "card 0 0 0 1 2",
            "card 3 0 0",
            "TEST 2 card 1 cost 2",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "card 3 1 15 14",
            "TEST 2 card 0 cost 1",
            "sw_char 2 13",
            "sw_char 1 12",
            "card 1 0 11",
            "skill 1 10 9 8",
            "card 0 0 7 6",
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
        charactor:Xingqiu
        charactor:Kamisato Ayaka
        charactor:Yae Miko
        Capricious Visage*5
        Shimenawa's Reminiscence*5
        Thundering Poise*5
        Vermillion Hereafter*5
        Kanten Senmyou Blessing*20
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
                cid = int(cmd[3])
                cost = int(cmd[5])
                for req in match.requests:
                    if req.name == 'UseCardRequest' and req.card_idx == cid:
                        assert req.cost.total_dice_cost == cost
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_vermillion_shimenawa()
    test_vermillion_shimenawa_2()
