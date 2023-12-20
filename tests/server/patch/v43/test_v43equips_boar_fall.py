import os

from src.lpsim.server.deck import Deck
from src.lpsim.server.match import Match
from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim import MatchState
from tests.utils_for_test import (
    check_hp, check_usage, get_pidx_cidx, get_random_state, 
    get_test_id_from_command, make_respond, set_16_omni, read_from_log_json
)


def test_v43equips_boar_fall():
    match, agent_0, agent_1 = read_from_log_json(
        os.path.join(os.path.dirname(__file__), 'jsons', 'test_11card.json')
    )
    # modify hp
    # for i in range(2):
    #     charactors = match.player_tables[i].player_deck_information.charactors  # noqa: E501
    #     for c in charactors:
    #         c.hp = c.max_hp = 30
    # add omnipotent guide
    set_16_omni(match)
    match.start()
    match.step()
    new_commands = [[], []]

    while True:
        if match.need_respond(0):
            agent = agent_0
            nc = new_commands[0]
        elif match.need_respond(1):
            agent = agent_1
            nc = new_commands[1]
        else:
            raise AssertionError('No need respond.')
        # do tests
        while True:
            nc.append(agent.commands[0])
            cmd = agent.commands[0].strip().split(' ')
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                hps = cmd[2:]
                hps = [int(x) for x in hps]
                hps = [hps[:5], hps[5:]]
                check_hp(match, hps)
            elif test_id == 2:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].summons, cmd[3:])
            elif test_id == 3:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].supports, cmd[3:])
            elif test_id == 4:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].team_status, cmd[3:])
            elif test_id == 5:
                pidx, cidx = get_pidx_cidx(cmd)
                check_usage(match.player_tables[pidx].charactors[cidx].status, 
                            cmd[3:])
            elif test_id == 6:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].hands) == int(cmd[3])
            elif test_id == 7:
                pidx = int(cmd[2][1])
                d = {}
                for c in match.player_tables[pidx].dice.colors:
                    d[c.value] = d.get(c.value, 0) + 1
                for c in cmd[3:]:
                    d[c] -= 1
                    if d[c] == 0:
                        del d[c]
                assert len(d) == 0
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_boar_princess():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 1 0",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "skill 1 11 10 9",
            "skill 1 8 7 6",
            "TEST 1 p0 status 2 2",
            "TEST 1 p1 status 2 2",
            "end",
            "TEST 1 p0 status 1",
            "TEST 1 p1 status 1",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "card 1 0",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "skill 1 11 10 9",
            "skill 1 8 7 6",
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
        default_version:4.3
        charactor:Shenhe
        charactor:Chongyun
        charactor:Nahida
        The Boar Princess*10
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
            cmd = agent.commands[0].strip().split(' ')
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].team_status, cmd[4:])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_glow_defeated_no_draw():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "sw_char 1 12",
            "skill 1 11 10 9",
            "skill 1 8 7 6"
        ],
        [
            "sw_card",
            "choose 0",
            "skill 1 15 14 13",
            "skill 0 12 11 10",
            "card 0 0 9",
            "skill 2 8 7 6",
            "choose 1",
            "TEST 1 p1 hand 4",
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
        default_version:4.3
        charactor:Shenhe
        charactor:Chongyun
        charactor:Nahida
        Vourukasha's Glow*10
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
            cmd = agent.commands[0].strip().split(' ')
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 1:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].hands) == int(cmd[4])
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    # test_v43equips_boar_fall()
    test_boar_princess()
    test_glow_defeated_no_draw()
