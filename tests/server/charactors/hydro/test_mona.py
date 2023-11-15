from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.agents.nothing_agent import NothingAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_test_id_from_command, make_respond, get_random_state, 
    set_16_omni
)


def test_mona():
    """
    first: quick switch two times and slow switch one time. equip artifact
    and check card can cost less. multiple summon will renew old one. 
    Double damage will affect after elemental reaction, and only affect once.
    """
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "reroll",
            "sw_char 1 2",
            "sw_char 0 6",
            "TEST 7 player 0 not ended",
            "sw_char 2 5",
            "TEST 6 player 0 ended",
            "sw_char 0 4",
            "card 0 0 1 2",
            "skill 1 hydro omni",
            "TEST 4 one summon usage 1",
            "TEST 5 hp 9 10 10",
            "end",
            "reroll 1 2 3 4 5 6 7",
            "skill 1 1 2",
            "skill 1 1 0 2",
            "tune 0 0",
            "tune 1 1",
            "tune 1 2",
            "skill 1 0 1 2",
            "TEST 4 one summon usage 1",
            "end",
            "reroll 1 2 3 4 5 6 7",
            "tune 2 6",
            "tune 3 6",
            "TEST 3 talent can decrease cost",
            "sw_char 1 6",
            "TEST 2 talent cannot decrease cost",
            "sw_char 0 6",
            "TEST 3 talent can decrease cost",
            "end",
            "reroll 1 2 3 4 5 6 7",
            "end",
            "reroll 4 5 6 7",
            "skill 1 2 3",
            "card 0 0 0 1 2",
            "end",
            "TEST 1 hp 0 9 10",
            "reroll 1 3 4 5 6 7",
            "sw_char 2 7",
            "tune 0 1",
            "card 2 0 0 1 2",
            "tune 0 0",
            "tune 2 2",
            "tune 2 2",
            "skill 1 0 1 2",
            "end"
        ],
        only_use_command = True
    )
    match = Match(version = '0.0.1', random_state = get_random_state())
    deck = Deck.from_str(
        """
        charactor:Mona*2
        charactor:Fischl
        Prophecy of Submersion*10
        Stellar Predator*10
        Wine-Stained Tricorne*10
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    assert match.start()[0]
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    check_hp(match, [[0, 9, 10], [10, 10, 10]])
                elif test_id == 2:
                    hands = match.player_tables[1].hands
                    requests = [x for x in match.requests 
                                if x.name == 'UseCardRequest'
                                and hands[x.card_idx].name 
                                == 'Prophecy of Submersion']
                    assert len(requests) == 0
                    # assert requests[0].cost.elemental_dice_number == 3
                elif test_id == 3:
                    hands = match.player_tables[1].hands
                    requests = [x for x in match.requests 
                                if x.name == 'UseCardRequest'
                                and hands[x.card_idx].name 
                                == 'Prophecy of Submersion']
                    assert len(requests) > 0
                    assert requests[0].cost.elemental_dice_number == 2
                elif test_id == 4:
                    summons = match.player_tables[1].summons
                    assert len(summons) == 1
                    assert summons[0].usage == 1
                elif test_id == 5:
                    check_hp(match, [[9, 10, 10], [10, 10, 10]])
                elif test_id == 6:
                    assert match.player_tables[0].has_round_ended
                elif test_id == 7:
                    assert not match.player_tables[0].has_round_ended
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 7
    check_hp(match, [[0, 3, 9], [10, 10, 10]])

    assert match.state != MatchState.ERROR


def test_mona_2():
    """
    when shield of Reflection becomes 0, will not disappear; summon twice
    will recover shield; artifact can effect talent card; attack that 
    equip talent will trigger talent; Bubble and talent can work 
    simultaneously, with damage: (1 + 1electrocharge + 2) * 2 = 8.
    """
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card 1 3 4",
            "choose 0",
            "reroll",
            "tune 0 7",
            "skill 1 0 1 2",
            "sw_char 1 1",
            "sw_char 0 1",
            "sw_char 1 1",
            "end",
            "reroll",
            "end",
            "reroll",
            "sw_char 2 7",
            "end",
            "reroll",
            "end",
            "TEST 1 hp 7 4 1",
            "reroll 1 2 3 4 5 6 7",
            "sw_char 1 7",
            "choose 0",
            "skill 0 0 1 5",
            "skill 1 0 1 2",
            "end",
            "reroll",
            "skill 0 0 6 7"
        ],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "reroll 2 3 4 5 6 7",
            "skill 1 1 2 3",
            "card 0 0 3 4",
            "tune 3 2",
            "skill 1 0 1",
            "end",
            "reroll 3 4 5 6 7",
            "skill 0 0 1",
            "sw_char 2 0",
            "tune 1 0",
            "tune 1 2",
            "card 2 0 0 1 2",
            "sw_char 0 0",
            "end",
            "reroll 1 2 3 4 5 6 7",
            "end",
            "reroll 1 2 3 4 5 6 7",
            "card 1 0 0 1",
            "end",
            "reroll 4 5 6 7",
            "skill 1 2 3",
            "tune 0 3",
            "skill 1 0 1 2",
            "end",
            "reroll 2 3 4 5 6 7",
            "sw_char 2 7",
            "tune 2 6",
            "tune 2 6",
            "card 0 2 5 6",
            "skill 1 0 1 2"
        ],
        only_use_command = True
    )
    match = Match(version = '0.0.1', random_state = get_random_state())
    deck = Deck.from_str(
        """
        charactor:Mona*2
        charactor:Fischl
        Prophecy of Submersion*10
        Stellar Predator*10
        Wine-Stained Tricorne*10
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    assert match.start()[0]
    match.step()

    while True:
        if match.need_respond(0):
            while True:
                test_id = get_test_id_from_command(agent_0)
                if test_id == 1:
                    check_hp(match, [[7, 4, 1], [9, 10, 10]])
                else:
                    break
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_0.commands) == 0 and len(agent_1.commands) == 0
    assert match.round_number == 6
    check_hp(match, [[3, 0, 0], [8, 10, 9]])

    assert match.state != MatchState.ERROR


def test_mona_q_enemy_attack():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "skill 1 0 1 2",
            "end",
            "skill 1 0 1 2",
        ],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card 0 1 2",
            "choose 0",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "card 4 0 0 1 2",
            "card 0 0",
            "end",
        ],
        only_use_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        """
        charactor:Mona*2
        charactor:Fischl
        Sweet Madame*15
        Prophecy of Submersion*15
        """
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    set_16_omni(match)
    match.config.random_first_player = False
    assert match.start()[0]
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_0.commands) == 0 and len(agent_1.commands) == 0
    assert match.round_number == 2
    assert len(match.player_tables[1].team_status) == 1
    assert match.player_tables[1].team_status[0].name == 'Illusory Bubble'
    check_hp(match, [[3, 10, 10], [9, 10, 10]])

    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_mona()
    test_mona_q_enemy_attack()
