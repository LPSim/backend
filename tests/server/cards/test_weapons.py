from agents.interaction_agent import InteractionAgent
from server.match import Match, MatchState
from server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_random_state, get_test_id_from_command, make_respond, 
    set_16_omni
)


def test_vanilla_weapons():
    # use frontend and FastAPI server to perform commands, and test commands 
    # that start with TEST. NO NOT put TEST at the end of command list!
    # If a command is succesfully performed, frontend will print history 
    # commands in console. Note that frontend cannot distinguish if a new
    # match begins, so you need to refresh the page before recording a new
    # match, otherwise the history commands will be mixed.
    #
    # for tests, it starts with TEST and contains a test id, which is used to
    # identify the test. Other texts in the command are ignored, but you can
    # parse them if you want. Refer to the following code.
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "end",
            "end",
            "end",
            "TEST 2 weapon target right",
            "card 0 0 0 1",
            "skill 1 0 1 2",
            "TEST 1 10 10 90 10 10 8 10 90 10 10",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "end",
            "TEST 1 10 10 85 10 10 8 10 90 10 9",
            "end",
            "card 1 0 0 1",
            "card 3 0 0 1",
            "sw_char 1 0",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "end",
            "end",
            "end",
            "TEST 1 10 10 90 10 10 8 10 90 10 10",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "TEST 1 10 10 89 10 10 8 10 90 10 10",
            "sw_char 1 0",
            "sw_char 0 0",
            "card 5 0 0 1",
            "skill 0 0 1",
            "TEST 1 10 10 89 10 10 8 10 90 10 10",
            "sw_char 4 0",
            "skill 1 0 1 2",
            "end",
            "sw_char 0 0",
            "skill 2 0 1 2",
            "TEST 1 10 10 78 10 10 8 10 90 10 9",
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
        charactor:Barbara
        charactor:Noelle
        charactor:PhysicalMob
        charactor:Fischl
        Magic Guide*2
        Raven Bow*2
        Traveler's Handy Sword*2
        White Iron Greatsword*2
        White Tassel*2
        '''
    )
    deck.charactors[2].hp = 90
    deck.charactors[2].max_hp = 90
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
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
                hps = [hps[:5], hps[5:]]
                check_hp(match, hps)
            elif test_id == 2:
                cards = match.player_tables[0].hands
                for req in match.requests:
                    if req.name == 'UseCardRequest':
                        card = cards[req.card_idx]
                        targets = req.targets
                        for target in targets:
                            assert target.charactor_idx != 3  # 3 is mob
                        if card.name == 'Magic Guide':
                            assert len(targets) == 1
                            assert targets[0].charactor_idx == 1
                        elif card.name == 'White Iron Greatsword':
                            assert len(targets) == 2
                            assert targets[0].charactor_idx == 0
                            assert targets[1].charactor_idx == 2
                        elif card.name == 'Raven Bow':
                            assert len(targets) == 1
                            assert targets[0].charactor_idx == 4
                        else:
                            raise AssertionError('Other weapon cannot use')
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


def test_the_bell():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "card 0 1 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 p1 status 1 usage 1",
            "end",
            "end",
            "end",
            "sw_char 1 0",
            "TEST 1 p1 status 1 usage 2",
            "skill 1 0 1 2",
            "TEST 1 p1 status 1 usage 2",
            "end"
        ],
        [
            "sw_card",
            "choose 0",
            "TEST 1 p0 status 0 usage 0",
            "card 0 0 0 1 2",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 p1 status 1 usage 1",
            "end",
            "skill 1 0 1 2",
            "TEST 1 p1 status 1 usage 2",
            "end",
            "end",
            "skill 1 0 1 2",
            "card 0 0 0 1 2",
            "skill 1 0 1 2"
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
        charactor:Barbara
        charactor:Noelle
        The Bell*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
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
                cmd = cmd.strip().split()
                pid = int(cmd[2][1])
                snum = int(cmd[4])
                usage = int(cmd[6])
                status = match.player_tables[pid].team_status
                assert len(status) == snum
                if snum:
                    assert status[0].usage == usage
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_vanilla_weapons()
    test_the_bell()
