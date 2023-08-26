from agents.interaction_agent import (
    InteractionAgent_V1_0 as InteractionAgent
)
from agents.nothing_agent import NothingAgent
from server.match import Match, MatchState
from server.deck import Deck
from tests.utils_for_test import (
    check_hp, make_respond, get_random_state
)
from server.interaction import UseSkillRequest


def test_small_elemental_artifacts():
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = InteractionAgent(
        version = '1.0',
        player_id = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "reroll 1 2 3 4 5 6 7",
            "card 4 0 pyro geo",
            # cost decrease
            "skill 0 dendro hydro",
            # check skill cost after first attack (should no cost decrease)
            "tune hydro 1",
            "card 1 0 dendro dendro",
            # after equip second artifact, can use A but not E 
            # (cost is dendro + any)
            "skill 0 omni omni",
            "end",
            "reroll 0 1 2 3 4 5 6 7",
            "card 0 0 anemo",
            "tune hydro 0",
            # next run after tune, 3 skills are available but only normal 
            # any decrease
            "skill 1 dendro dendro omni",
            "tune pyro 0",
            # after skill 1 and tune, still have 1-1 normal attack
            "card 0 0 electro electro",
            "tune hydro 0",
            "skill 2 dendro dendro",
            "end",
            "reroll",
            "sw_char 1 anemo",
            "sw_char 2 anemo",
            "tune dendro 0",
            "skill 0 electro dendro dendro",
            "tune pyro 0",
            "skill 0 electro cryo cryo",
            "end"
            # 85 10 10 99 10 10
        ],
        random_after_no_command = True
    )
    match = Match(random_state = get_random_state())
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
                'hp': 99,
                'max_hp': 99,
            },
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
            },
            {
                'name': 'ElectroMobMage',
                'element': 'ELECTRO',
            },
        ],
        'cards': [
            {
                'name': 'Wine-Stained Tricorne',
            }
        ] * 10 + [
            {
                'name': 'Laurel Coronet',
            }
        ] * 10 + [
            {
                'name': 'Strategize',
            }
        ] * 10,
    }
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):

            # asserts
            if len(agent_1.commands) == 22:
                # cost decrease
                skills = [x for x in match.requests
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 2
                assert skills[0].cost.elemental_dice_number == 0
                assert skills[0].cost.any_dice_number == 2
                assert skills[1].cost.elemental_dice_number == 2
                assert skills[1].cost.any_dice_number == 0
            elif len(agent_1.commands) == 21:
                # check skill cost after first attack (should no cost decrease)
                skills = [x for x in match.requests
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 2
                assert skills[0].cost.elemental_dice_number == 1
                assert skills[0].cost.any_dice_number == 2
                assert skills[1].cost.elemental_dice_number == 3
                assert skills[1].cost.any_dice_number == 0
            elif len(agent_1.commands) == 19:
                # after equip second artifact, can use A but not E 
                # (cost is dendro + any)
                skills = [x for x in match.requests
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 1
                skill: UseSkillRequest = skills[0]
                assert skill.cost.elemental_dice_number == 1
                assert skill.cost.any_dice_number == 1
            elif len(agent_1.commands) == 14:
                # next run after tune, 3 skills are available but only normal 
                # any decrease
                skills = [x for x in match.requests 
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 3
                skills.sort(key = lambda x: x.skill_id)
                assert skills[0].cost.elemental_dice_number == 1
                assert skills[0].cost.any_dice_number == 1
                assert skills[1].cost.elemental_dice_number == 3
                assert skills[1].cost.any_dice_number == 0
                assert skills[2].cost.elemental_dice_number == 3
                assert skills[2].cost.any_dice_number == 0
            elif len(agent_1.commands) == 12:
                # after skill 1 and tune, still have 1-1 normal attack
                skills = [x for x in match.requests 
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 1
                skill: UseSkillRequest = skills[0]
                assert skill.cost.elemental_dice_number == 1
                assert skill.cost.any_dice_number == 1

            make_respond(agent_1, match)
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 4
    check_hp(match, [[85, 10, 10], [99, 10, 10]])
    assert match.player_tables[1].charactors[0].artifact is not None

    assert match.match_state != MatchState.ERROR


if __name__ == '__main__':
    test_small_elemental_artifacts()
