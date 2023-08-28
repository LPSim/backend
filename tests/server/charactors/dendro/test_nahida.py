from agents.interaction_agent import InteractionAgent
from agents.nothing_agent import NothingAgent
from server.match import Match, MatchState
from server.consts import DamageElementalType
from server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_test_id_from_command, make_respond, get_random_state,
    set_16_omni
)


def test_fischl_mona_nahida():
    """
    3335 + E + talent
    """
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "card 1 0 0 1",
            "skill 1 0 1 2",
            "sw_char 1 1",
            "skill 1 omni omni hydro",
            "end",
            "TEST 1 hp 4 8 8",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "skill 2 omni omni dendro omni omni",
            "TEST 2 hp 0 7 7 and 1 seed for alive",
            "end",
            "TEST 3 hp 0 1 5",
            "skill 1 0 1 2",
            "card 0 0 0 1 2"
        ],
        random_after_no_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        """
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        Rana*10
        Wine-Stained Tricorne*10
        The Seed of Stored Knowledge*10
        """
    )
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    check_hp(match, [[4, 8, 8], [10, 10, 10]])
                elif test_id == 2:
                    check_hp(match, [[0, 7, 7], [10, 10, 10]])
                    for charactor in match.player_tables[0].charactors:
                        if charactor.is_alive:
                            assert len(charactor.status) == 1
                            assert charactor.status[
                                0].name == "Seed of Skandha"
                        else:
                            assert len(charactor.status) == 0
                elif test_id == 3:
                    check_hp(match, [[0, 1, 5], [10, 10, 10]])
                else:
                    break
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 3
    check_hp(match, [[0, 0, 1], [10, 10, 10]])
    assert len(match.player_tables[1].team_status) == 1
    assert match.player_tables[1].team_status[0].name == 'Shrine of Maya'
    assert match.player_tables[1].team_status[0].usage == 3

    assert match.match_state != MatchState.ERROR


def test_fischl_mona_nahida_no_talent():
    """
    3335 + EQ
    """
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "card 1 0 0 1",
            "skill 1 0 1 2",
            "sw_char 1 1",
            "skill 1 omni omni hydro",
            "end",
            "TEST 1 hp 4 8 8",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "skill 2 omni omni dendro omni omni",
            "TEST 2 hp 0 7 7 and 1 seed for alive",
            "end",
            "TEST 3 hp 0 1 5",
            "skill 1 0 1 2",
            "skill 3 0 1 2"
        ],
        random_after_no_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        """
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        Rana*10
        Wine-Stained Tricorne*10
        The Seed of Stored Knowledge*10
        """
    )
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    check_hp(match, [[4, 8, 8], [10, 10, 10]])
                elif test_id == 2:
                    check_hp(match, [[0, 7, 7], [10, 10, 10]])
                    for charactor in match.player_tables[0].charactors:
                        if charactor.is_alive:
                            assert len(charactor.status) == 1
                            assert charactor.status[
                                0].name == "Seed of Skandha"
                        else:
                            assert len(charactor.status) == 0
                elif test_id == 3:
                    check_hp(match, [[0, 1, 5], [10, 10, 10]])
                else:
                    break
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 3
    check_hp(match, [[0, 0, 1], [10, 10, 10]])
    assert len(match.player_tables[1].team_status) == 1
    assert match.player_tables[1].team_status[0].name == 'Shrine of Maya'
    assert match.player_tables[1].team_status[0].usage == 2

    assert match.match_state != MatchState.ERROR


def test_nahida_talents():
    """
    first: with no pyro hydro electro ally
    """
    agent_0 = InteractionAgent(
        player_id = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "sw_char 1 0",
            "sw_char 0 0",
            "end",
            "sw_char 2 0",
            "sw_char 0 0",
            "sw_char 1 0",
            "sw_char 2 0",
            "sw_char 1 0",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "end",
            "end"
        ],
        random_after_no_command = True
    )
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 2",
            "skill 1 0 1 2",
            "TEST 1 only p0c1 2seed",
            "skill 1 0 1 2",
            "TEST 2 p0c0 p0c1 2seed",
            "skill 1 0 1 2",
            "TEST 3 all 2seed hp 6 8 10",
            "end",
            "card 5 0 0 1 2",
            "TEST 4 maya 2 seed all 2",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "TEST 5 hp 5 4 5 mid no element",
            "sw_char 2 0",
            "skill 1 0 1 2",
            "TEST 6 hp 5 2 5 all dendro 2seed",
            "sw_char 1 0",
            "sw_char 2 0",
            "sw_char 1 0",
            "sw_char 2 0",
            "end",
            "TEST 7 hp 4 1 1, ele DDN, all 1seed, burining flame, 1 maya",
            "sw_char 0 0"
        ],
        random_after_no_command = True
    )
    match = Match(version = '0.0.1', random_state = get_random_state())
    deck1 = Deck.from_str('''
        charactor:ElectroMobMage
        charactor:PyroMobMage
        charactor:HydroMobMage
        Rana*10
        Wine-Stained Tricorne*10
        The Seed of Stored Knowledge*10
    ''')
    deck2 = Deck.from_str(
        """
        charactor:DendroMobMage
        charactor:DendroMobMage
        charactor:Nahida
        Rana*10
        Wine-Stained Tricorne*10
        The Seed of Stored Knowledge*10
        """
    )
    match.set_deck([deck1, deck2])
    match.match_config.max_same_card_number = 30
    match.match_config.random_first_player = False
    set_16_omni(match)
    assert match.start()
    match.player_tables[1].charactors[0].skills[
        0].damage_type = DamageElementalType.PYRO  # can do pyro damage
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    charactors = match.player_tables[0].charactors
                    assert len(charactors[0].status) == 0
                    assert len(charactors[1].status) == 1
                    assert charactors[1].status[0].name == "Seed of Skandha"
                    assert charactors[1].status[0].usage == 2
                    assert len(charactors[2].status) == 0
                elif test_id == 2:
                    charactors = match.player_tables[0].charactors
                    assert len(charactors[0].status) == 1
                    assert charactors[0].status[0].name == "Seed of Skandha"
                    assert charactors[0].status[0].usage == 2
                    assert len(charactors[1].status) == 1
                    assert charactors[1].status[0].name == "Seed of Skandha"
                    assert charactors[1].status[0].usage == 2
                    assert len(charactors[2].status) == 0
                elif test_id == 3:
                    charactors = match.player_tables[0].charactors
                    for charactor in charactors:
                        assert len(charactor.status) == 1
                        assert charactor.status[0].name == "Seed of Skandha"
                        assert charactor.status[0].usage == 2
                    for charactor in charactors[:2]:
                        assert charactor.element_application == ['DENDRO']
                    assert charactors[2].element_application == []
                    check_hp(match, [[6, 8, 10], [10, 10, 10]])
                elif test_id == 4:
                    charactors = match.player_tables[0].charactors
                    for charactor in charactors:
                        assert len(charactor.status) == 1
                        assert charactor.status[0].name == "Seed of Skandha"
                        assert charactor.status[0].usage == 2
                    for charactor in charactors:
                        assert charactor.element_application == ['DENDRO']
                    assert len(match.player_tables[1].team_status) == 1
                    assert match.player_tables[1].team_status[0].name == (
                        'Shrine of Maya'
                    )
                    assert match.player_tables[1].team_status[0].usage == 2
                elif test_id == 5:
                    charactors = match.player_tables[0].charactors
                    for cid, charactor in enumerate(charactors):
                        assert len(charactor.status) == 1
                        assert charactor.status[0].name == "Seed of Skandha"
                        assert charactor.status[0].usage == 1
                        if cid == 1:
                            assert charactor.element_application == []
                        else:
                            assert charactor.element_application == ['DENDRO']
                    check_hp(match, [[5, 4, 5], [10, 10, 10]])
                elif test_id == 6:
                    # TEST 6 hp 5 2 5 all dendro 2seed
                    charactors = match.player_tables[0].charactors
                    for charactor in charactors:
                        assert len(charactor.status) == 1
                        assert charactor.status[0].name == "Seed of Skandha"
                        assert charactor.status[0].usage == 2
                        assert charactor.element_application == ['DENDRO']
                    check_hp(match, [[5, 2, 5], [10, 10, 10]])
                elif test_id == 7:
                    # hp 4 1 1, ele DDN, all 1seed, burining flame, 1 maya
                    charactors = match.player_tables[0].charactors
                    for cid, charactor in enumerate(charactors):
                        assert len(charactor.status) == 1
                        assert charactor.status[0].name == "Seed of Skandha"
                        assert charactor.status[0].usage == 1
                        if cid == 2:
                            assert charactor.element_application == []
                        else:
                            assert charactor.element_application == ['DENDRO']
                    check_hp(match, [[4, 1, 1], [10, 7, 10]])
                    assert len(match.player_tables[1].team_status) == 1
                    assert match.player_tables[1].team_status[0].name == (
                        'Shrine of Maya'
                    )
                    assert match.player_tables[1].team_status[0].usage == 1
                    assert len(match.player_tables[1].summons) == 1
                    assert match.player_tables[1].summons[0].name == (
                        'Burning Flame'
                    )
                    assert match.player_tables[1].summons[0].usage == 1
                else:
                    break
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 3
    check_hp(match, [[4, 1, 1], [10, 7, 10]])

    assert match.match_state != MatchState.ERROR

    """
    second: with pyro electro (hydro tested above)
    """
    agent_0 = InteractionAgent(
        player_id = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 1",
            "skill 1 0 1 2",
            "sw_char 0 0",
            "end",
            "sw_char 2 0",
            "sw_char 0 0",
            "sw_char 2 0",
            "sw_char 1 0",
            "sw_char 2 0",
            "end",
            "end"
        ],
        random_after_no_command = True
    )
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 2",
            "skill 1 0 1 2",
            "TEST 1 only p0c1 2seed",
            "skill 1 0 1 2",
            "TEST 2 p0c0 p0c1 2seed",
            "skill 1 0 1 2",
            "TEST 3 all 2seed hp 6 8 10",
            "end",
            "card 5 0 0 1 2",
            "TEST 4 maya 2 seed all 3, p1c2 seed 2",
            "skill 1 0 1 2",
            "TEST 4 maya 2 seed all 3, p1c2 seed 2",
            "sw_char 0 0",
            "skill 0 0 1 2",
            "TEST 5 hp 3 4 5 all dendro",
            "sw_char 2 0",
            "end",
            "TEST 7 hp 4 3 1, all dendro, all 1seed, burining flame, 1 maya",
            "sw_char 0 0"
        ],
        random_after_no_command = True
    )
    match = Match(version = '0.0.1', random_state = get_random_state())
    deck1 = Deck.from_str('''
        charactor:ElectroMobMage
        charactor:Nahida
        charactor:HydroMobMage
        Rana*10
        Wine-Stained Tricorne*10
        The Seed of Stored Knowledge*10
    ''')
    deck2 = Deck.from_str(
        """
        charactor:PyroMobMage
        charactor:ElectroMobMage
        charactor:Nahida
        Rana*10
        Wine-Stained Tricorne*10
        The Seed of Stored Knowledge*10
        """
    )
    match.set_deck([deck1, deck2])
    match.match_config.max_same_card_number = 30
    match.match_config.random_first_player = False
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    charactors = match.player_tables[0].charactors
                    assert len(charactors[0].status) == 0
                    assert len(charactors[1].status) == 1
                    assert charactors[1].status[0].name == "Seed of Skandha"
                    assert charactors[1].status[0].usage == 2
                    assert len(charactors[2].status) == 0
                elif test_id == 2:
                    charactors = match.player_tables[0].charactors
                    assert len(charactors[0].status) == 1
                    assert charactors[0].status[0].name == "Seed of Skandha"
                    assert charactors[0].status[0].usage == 2
                    assert len(charactors[1].status) == 1
                    assert charactors[1].status[0].name == "Seed of Skandha"
                    assert charactors[1].status[0].usage == 2
                    assert len(charactors[2].status) == 0
                elif test_id == 3:
                    charactors = match.player_tables[0].charactors
                    for charactor in charactors:
                        assert len(charactor.status) == 1
                        assert charactor.status[0].name == "Seed of Skandha"
                        assert charactor.status[0].usage == 2
                    for charactor in charactors[:2]:
                        assert charactor.element_application == ['DENDRO']
                    assert charactors[2].element_application == []
                    check_hp(match, [[6, 8, 10], [10, 10, 8]])
                elif test_id == 4:
                    charactors = match.player_tables[0].charactors
                    for charactor in charactors:
                        assert len(charactor.status) == 1
                        assert charactor.status[0].name == "Seed of Skandha"
                        assert charactor.status[0].usage == 3
                    for charactor in charactors:
                        assert charactor.element_application == ['DENDRO']
                    assert len(match.player_tables[1].team_status) == 1
                    assert match.player_tables[1].team_status[0].name == (
                        'Shrine of Maya'
                    )
                    assert match.player_tables[1].team_status[0].usage == 2
                    assert match.player_tables[1].charactors[2].status[
                        0].name == 'Seed of Skandha'
                    assert match.player_tables[1].charactors[2].status[
                        0].usage == 2
                elif test_id == 5:
                    charactors = match.player_tables[0].charactors
                    for cid, charactor in enumerate(charactors):
                        assert len(charactor.status) == 1
                        assert charactor.status[0].name == "Seed of Skandha"
                        assert charactor.status[0].usage == 2
                        assert charactor.element_application == ['DENDRO']
                    check_hp(match, [[3, 4, 5], [10, 10, 8]])
                elif test_id == 7:
                    # hp 4 1 1, ele DDN, all 1seed, burining flame, 1 maya
                    charactors = match.player_tables[0].charactors
                    for cid, charactor in enumerate(charactors):
                        assert len(charactor.status) == 1
                        assert charactor.status[0].name == "Seed of Skandha"
                        assert charactor.status[0].usage == 1
                        assert charactor.element_application == ['DENDRO']
                    check_hp(match, [[2, 3, 1], [10, 10, 8]])
                    assert len(match.player_tables[1].team_status) == 1
                    assert match.player_tables[1].team_status[0].name == (
                        'Shrine of Maya'
                    )
                    assert match.player_tables[1].team_status[0].usage == 1
                    assert len(match.player_tables[1].summons) == 1
                    assert match.player_tables[1].summons[0].name == (
                        'Burning Flame'
                    )
                    assert match.player_tables[1].summons[0].usage == 1
                else:
                    break
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 3
    check_hp(match, [[2, 3, 1], [10, 10, 8]])

    assert match.match_state != MatchState.ERROR


def test_nahida_apply_seed_to_defeated():
    """
    try to apply seed to defeated charactor.
    """
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 2",
            "skill 1 0 1 2",
            "skill 1 0 1 2",
            "skill 3 0 1 2",
            "skill 1 0 1 2",
            "end",
            "skill 1 0 1 2",
            "skill 2 0 1 2 3 4",
            "end",
        ],
        random_after_no_command = True
    )
    match = Match(random_state = get_random_state())
    deck = Deck.from_str(
        """
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        Rana*10
        Wine-Stained Tricorne*10
        The Seed of Stored Knowledge*10
        """
    )
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 3
    check_hp(match, [[0, 5, 10], [10, 10, 10]])
    assert len(match.player_tables[1].team_status) == 0
    for charactor in match.player_tables[0].charactors:
        if charactor.is_alive:
            assert len(charactor.status) == 1
            assert charactor.status[0].name == "Seed of Skandha"
            assert charactor.status[0].usage == 2
        else:
            assert len(charactor.status) == 0

    assert match.match_state != MatchState.ERROR


if __name__ == '__main__':
    test_nahida_apply_seed_to_defeated()
