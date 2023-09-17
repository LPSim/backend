from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_collei():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 2 0 0 1 2 3",
            "sw_char 1 0",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "TEST 2 p0 1 status",
            "skill 1 0 1 2",
            "sw_char 1 0",
            "end",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "skill 1 0 1 2",
            "TEST 1 5 88 10 7 80 3",
            "TEST 3 p0 1 catalyzing field",
            "end",
            "skill 2 0 1 2",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "TEST 1 3 88 10 7 66 3",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "TEST 2 p0 0 status",
            "end",
            "skill 1 0 1 2",
            "end",
            "sw_char 1 0",
            "end"
        ],
        [
            "sw_card 0 1 2",
            "choose 0",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "sw_char 0 0",
            "sw_char 2 0",
            "TEST 1 5 90 10 7 90 3",
            "TEST 3 p0 1 cayalyzing field",
            "sw_char 1 0",
            "end",
            "end",
            "end",
            "TEST 1 3 88 10 7 58 3",
            "end",
            "TEST 1 3 88 10 7 49 3",
            "sw_char 2 0",
            "sw_char 0 0",
            "card 2 0 0 1 2",
            "TEST 1 3 82 10 7 49 3",
            "skill 1 0 1 2",
            "TEST 2 p1 0 status",
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
        charactor:Collei
        charactor:Nahida
        charactor:Fischl
        Floral Sidewinder*15
        '''
    )
    # use old version cards
    old = {'name': 'Floral Sidewinder', 'version': '3.3'}
    deck_dict = deck.dict()
    deck_dict['cards'] += [old] * 15
    deck = Deck(**deck_dict)
    # change HP
    # for charactor in deck.charactors:
    #     charactor.hp = 2
    #     charactor.max_hp = 2
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
                snum = int(cmd[3])
                status = match.player_tables[pnum].team_status
                assert len(status) == snum
            elif test_id == 3:
                assert len(match.player_tables[0].team_status) == 1
                assert match.player_tables[0].team_status[0].usage == 1
                assert match.player_tables[
                    0].team_status[0].name == 'Catalyzing Field'
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_collei()
