from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, check_name, get_random_state, get_test_id_from_command, 
    make_respond, set_16_omni
)


def test_barbara():
    cmd_records = [
        [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2",
            "end",
            "TEST 1 9 10 10 10 9 10",
            "TEST 2 only p0c0 hydro",
            "sw_char 1 0",
            "end",
            "TEST 3 sw_char 1 cost",
            "skill 1 0 1 2",
            "TEST 3 sw_char 1 cost",
            "sw_char 0 0",
            "sw_char 1 0",
            "end",
            "TEST 3 sw_char 1 cost",
            "skill 1 0 1 2",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "TEST 4 summon loop2 oz2",
            "end",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "skill 1 0 1 2",
            "end",
            "TEST 1 7 10 10 0 10 10",
            "TEST 5 team status 1 field",
            "end"
        ],
        [
            "sw_card",
            "choose 1",
            "skill 1 0 1 2",
            "end",
            "end",
            "TEST 1 9 10 10 9 8 9",
            "TEST 3 sw_char 1 cost",
            "card 0 0 0 1 2 3",
            "TEST 3 sw_char 0 cost",
            "sw_char 2",
            "TEST 3 sw_char 1 cost",
            "skill 2 0 1 2 3 4",
            "end",
            "TEST 1 5 9 10 10 8 10",
            "TEST 2 p0c1 p1c1 p1c2 hydro",
            "TEST 3 sw_char 0 cost",
            "sw_char 1",
            "skill 0 0 1 2",
            "TEST 3 sw_char 1 cost",
            "sw_char 0 0",
            "end",
            "TEST 3 sw_char 1 cost",
            "sw_char 1 0",
            "skill 1 0 1 2",
            "TEST 3 sw_char 0 cost",
            "sw_char 0",
            "end",
            "choose 1",
            "TEST 1 7 10 10 0 6 9",
            "skill 2 0 1 2"
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
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        '''
        default_version:4.0
        charactor:Fischl
        charactor:Barbara
        charactor:Nahida
        # Gambler's Earrings*2
        # Wine-Stained Tricorne*2
        # Vanarana
        # Timmie*2
        # Rana*2
        # Covenant of Rock
        # Wind and Freedom
        # The Bestest Travel Companion!*2
        # Changing Shifts*2
        # Toss-Up
        # Strategize*2
        # I Haven't Lost Yet!*2
        # Leave It to Me!
        # Calx's Arts*2
        # Adeptus' Temptation*2
        # Lotus Flower Crisp*2
        # Mondstadt Hash Brown*2
        # Tandoori Roast Chicken
        Glorious Season*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    match.config.random_first_player = False
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
            if test_id == 1:
                hps = [int(x) for x in cmd.strip().split()[2:]]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                parts = cmd.strip().split()
                found_part = set()
                for part in parts:
                    if len(part) == 4 and part[0] == 'p' and part[2] == 'c':
                        found_part.add(part)
                for player_idx in range(2):
                    for charactor_idx in range(3):
                        charactor = match.player_tables[
                            player_idx].charactors[charactor_idx]
                        part = f'p{player_idx}c{charactor_idx}'
                        if part in found_part:
                            assert charactor.element_application == ['HYDRO']
                        else:
                            assert charactor.element_application == []
            elif test_id == 3:
                cost = int(cmd.strip().split()[3])
                for req in match.requests:
                    if req.name == 'SwitchCharactorRequest':
                        assert req.cost.any_dice_number == cost
            elif test_id == 4:
                summons = match.player_tables[0].summons
                assert len(summons) == 2
                check_name('Melody Loop', summons)
                check_name('Oz', summons)
                for summon in summons:
                    assert summon.usage == 2
            elif test_id == 5:
                team_status = match.player_tables[0].team_status
                assert len(team_status) == 1
                assert team_status[0].name == 'Catalyzing Field'
                assert team_status[0].usage == 1
            else:
                break
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert match.state != MatchState.ERROR


def test_barbara_2():
    cmd_records = [
        [
            "sw_card",
            "choose 1",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "end",
            "sw_char 1 0",
            "sw_char 0 0",
            "skill 2 0 1 2",
            "TEST 1 6 10 10 7 7 1",
            "skill 1 0 1 2",
            "end",
            "sw_char 1 0",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "TEST 1 4 10 10 10 9 0",
            "sw_char 1 0",
            "card 0 0 0 1 2 3",
            "TEST 3 sw_char 0 cost",
            "sw_char 0",
            "TEST 3 sw_char 1 cost",
            "sw_char 1 0"
        ],
        [
            "sw_card",
            "choose 1",
            "card 0 0 0 1 2 3",
            "TEST 3 sw_char 0 cost",
            "sw_char 2",
            "card 0 0 0 1 2 3",
            "TEST 3 sw_char 0 cost",
            "TEST 2 1 summon",
            "end",
            "TEST 3 sw_char 0 cost",
            "TEST 1 8 10 10 9 9 5",
            "sw_char 0",
            "TEST 3 sw_char 0 cost",
            "sw_char 2",
            "TEST 3 sw_char 1 cost",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "choose 1",
            "skill 1 0 1 2",
            "skill 0 0 1 2",
            "end",
            "TEST 3 sw_char 0 cost",
            "sw_char 0",
            "TEST 3 sw_char 1 cost",
            "sw_char 1 0",
            "TEST 1 4 10 10 8 5 0",
            "skill 2 0 1 2",
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
        charactor:Barbara*2
        Glorious Season*30
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
                hps = [int(x) for x in cmd.strip().split()[2:]]
                hps = [hps[:3], hps[3:]]
                check_hp(match, hps)
            elif test_id == 2:
                summons = match.player_tables[1].summons
                assert len(summons) == 1
                assert summons[0].name == 'Melody Loop'
                assert summons[0].usage == 2
            elif test_id == 3:
                cost = int(cmd.strip().split()[3])
                for req in match.requests:
                    if req.name == 'SwitchCharactorRequest':
                        assert req.cost.any_dice_number == cost
            else:
                raise AssertionError(f'Unknown test id {test_id}')
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_barbara()
    test_barbara_2()
