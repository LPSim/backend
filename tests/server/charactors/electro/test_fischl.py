from src.lpsim.agents.interaction_agent import InteractionAgent
from src.lpsim.agents.nothing_agent import NothingAgent
from src.lpsim.server.match import Match, MatchState
from src.lpsim.server.deck import Deck
from tests.utils_for_test import (
    check_hp, make_respond, get_random_state
)


def test_fischl():
    """
    first: test equip talent, Oz will attack when normal attack, and this
    attack can go to next charactor, other charactor cannot trigger Oz attack,
    when run out of Oz, Oz will disappear immediately, Oz can trigger
    catalyzing field.
    """
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 1",
            "reroll pyro cryo hydro anemo",
            "sw_char 0 7",
            "card 1 0 2 3 4",
            "skill 0 1 2 3",
            "end",
            "reroll 1 2 3 4 5 6 7",
            "skill 0 0 5 6",
            "end",
            "reroll 0 1 2 3 4 5 6 7",
            "tune 0 dendro",
            "tune 0 dendro",
            "tune 0 dendro",
            "skill 1 0 1 2",
            "tune 0 anemo",
            "skill 0 0 1 2",
            "end",
            "reroll 0 1 2 3 4 5 6 7",
            "tune 0 pyro",
            "tune 0 6",
            "skill 2 0 1 2",
            "sw_char 1 cryo",
            "sw_char 0 pyro",
            "end",
            "reroll 3 4 5 6 7",
            "skill 1 1 2 3",
            "sw_char 1 4",
            "skill 0 0 2 3",
            "sw_char 0 0",
            "end",
            "reroll",
            "skill 0 0 1 2"
        ],
        only_use_command = True
    )
    match = Match(version = '0.0.1', random_state = get_random_state())
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'Fischl',
            },
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
            },
            {
                'name': 'PyroMobMage',
                'element': 'PYRO',
            },
        ],
        'cards': [
            {
                'name': 'Stellar Predator',
            }
        ] * 30,
    }
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            if len(agent_1.commands) == 16:
                # Oz attack on next charactor
                check_hp(match, [[0, 8, 10], [10, 10, 10]])
                assert len(
                    match.player_tables[0].charactors[1].element_application
                ) == 1
                assert len(
                    match.player_tables[0].charactors[2].element_application
                ) == 0
                assert match.player_tables[0].charactors[
                    1
                ].element_application[0] == 'ELECTRO'
                # should have Oz and usage 2
                assert len(match.player_tables[1].summons) == 1
                assert match.player_tables[1].summons[0].name == 'Oz'
                assert match.player_tables[1].summons[0].usage == 1
            elif len(agent_1.commands) == 11:
                # enemy hp 0 3 8 and only c1 have electro application
                check_hp(match, [[0, 3, 8], [10, 10, 10]])
                assert len(
                    match.player_tables[0].charactors[1].element_application
                ) == 1
                assert len(
                    match.player_tables[0].charactors[2].element_application
                ) == 0
                assert match.player_tables[0].charactors[
                    1
                ].element_application[0] == 'ELECTRO'
            elif len(agent_1.commands) == 4:
                # should have Oz and usage 2
                assert len(match.player_tables[1].summons) == 1
                assert match.player_tables[1].summons[0].name == 'Oz'
                assert match.player_tables[1].summons[0].usage == 2
            elif len(agent_1.commands) == 1:
                # should have Oz
                assert len(match.player_tables[1].summons) == 1
                assert match.player_tables[1].summons[0].name == 'Oz'
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 6
    check_hp(match, [[0, 0, 1], [10, 10, 10]])
    assert len(match.player_tables[1].dice.colors) == 5
    assert len(match.player_tables[1].summons) == 0

    assert match.state != MatchState.ERROR


def test_fischl_2():
    """
    second: when no talent or talent on other Fischl, cannot trigger Oz attack.
    re-summon Oz will refresh usage. Can equip talent multiple times.
    """
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "reroll 4 5 6 7",
            "card 0 0 2 3 4",
            "sw_char 1 4",
            "tune 0 3",
            "skill 1 0 1 2",
            "end",
            "reroll 1 2 3 4 5 6 7",
            "skill 0 0 2 3",
            "sw_char 0 4",
            "tune 0 1",
            "tune 0 2",
            "card 0 0 0 1 2",
            "end",
            "reroll 0 1 2 3 4 5 6 7",
            "tune 0 7",
            "tune 0 7",
            "tune 0 7",
            "tune 0 7",
            "sw_char 1 7",
            "skill 0 0 5 6",
            "skill 2 0 1 2"
        ],
        only_use_command = True
    )
    match = Match(version = '0.0.1', random_state = get_random_state())
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'Fischl',
            },
        ] * 3,
        'cards': [
            {
                'name': 'Stellar Predator',
            }
        ] * 30,
    }
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.random_first_player = False
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            if len(agent_1.commands) == 16:
                # should be Oz and usage 2
                assert len(match.player_tables[1].summons) == 1
                assert match.player_tables[1].summons[0].name == 'Oz'
                assert match.player_tables[1].summons[0].usage == 2
            elif len(agent_1.commands) == 10:
                # should be Oz and usage 1
                assert len(match.player_tables[1].summons) == 1
                assert match.player_tables[1].summons[0].name == 'Oz'
                assert match.player_tables[1].summons[0].usage == 1
            elif len(agent_1.commands) == 9:
                # should be Oz and usage 1
                assert len(match.player_tables[1].summons) == 1
                assert match.player_tables[1].summons[0].name == 'Oz'
                assert match.player_tables[1].summons[0].usage == 2
                check_hp(match, [[4, 10, 10], [10, 10, 10]])
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 3
    check_hp(match, [[0, 8, 8], [10, 10, 10]])

    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    test_fischl()
