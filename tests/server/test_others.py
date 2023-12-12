from typing import Dict, Literal
import pytest
from src.lpsim.utils.desc_registry import DescDictType

from src.lpsim.server.status.team_status.base import (
    ElementalInfusionTeamStatus, TeamStatusBase
)
from src.lpsim.utils.class_registry import get_instance, register_class

from src.lpsim.agents.random_agent import RandomAgent
from src.lpsim.agents.nothing_agent import NothingAgent
from src.lpsim.server.action import (
    CreateDiceAction, DrawCardAction, MoveObjectAction
)
from src.lpsim.server.consts import DamageElementalType, ObjectPositionType
from src.lpsim.server.deck import Deck
from src.lpsim.server.interaction import SwitchCardResponse
from src.lpsim.server.object_base import ObjectBase
from src.lpsim.server.struct import ObjectPosition
from src.lpsim.server.match import Match, MatchConfig


def test_object_position_validation():
    p1 = ObjectPosition(
        player_idx = 0,
        charactor_idx = 1,
        area = ObjectPositionType.CHARACTOR_STATUS,
        id = 345,
    )
    p2 = ObjectPosition(
        player_idx = 1,
        charactor_idx = 0,
        area = ObjectPositionType.CHARACTOR,
        id = 123
    )
    match = Match()
    match.player_tables[0].active_charactor_idx = 1
    match.player_tables[1].active_charactor_idx = 0
    assert p1.check_position_valid(p2, match)
    assert not p1.check_position_valid(p2, match, player_idx_same = True)
    assert not p1.check_position_valid(p2, match, charactor_idx_same = True)
    assert not p1.check_position_valid(p2, match, player_idx_same = True, 
                                       charactor_idx_same = True)
    assert not p1.check_position_valid(p2, match, area_same = True)
    assert not p1.check_position_valid(p2, match, id_same = True)
    assert p1.check_position_valid(p2, match, area_same = False)
    assert p1.check_position_valid(p2, match, id_same = False)
    assert p1.check_position_valid(
        p2, match, source_area = ObjectPositionType.CHARACTOR_STATUS)
    assert p1.check_position_valid(
        p2, match, target_area = ObjectPositionType.CHARACTOR)
    assert p1.check_position_valid(
        p2, match, source_is_active_charactor = True)
    assert p1.check_position_valid(
        p2, match, target_is_active_charactor = True)
    assert not p1.check_position_valid(
        p2, match, source_area = ObjectPositionType.CHARACTOR)
    assert not p1.check_position_valid(
        p2, match, target_area = ObjectPositionType.CHARACTOR_STATUS)
    assert not p1.check_position_valid(
        p2, match, source_is_active_charactor = False)
    assert not p1.check_position_valid(
        p2, match, target_is_active_charactor = False)
    assert p1.check_position_valid(
        p2, match, player_idx_same = False)
    assert p1.check_position_valid(
        p2, match, player_idx_same = False, charactor_idx_same = False)
    assert not p1.check_position_valid(
        p2, match, player_idx_same = True, charactor_idx_same = False)
    assert not p1.check_position_valid(
        p2, match, player_idx_same = False, charactor_idx_same = True)


def test_objectbase_wrong_handler_name():
    class WrongEventHandler(ObjectBase):
        name: Literal['WrongEventHandler'] = 'WrongEventHandler'
        position: ObjectPosition = ObjectPosition(
            player_idx = -1,
            area = ObjectPositionType.INVALID,
            id = -1,
        )

        def event_handler_NOT_EXIST(self, event):
            ...  # pragma: no cover

    with pytest.raises(ValueError):
        _ = WrongEventHandler()

    class WrongValueModifier(ObjectBase):
        name: Literal['WrongValueModifier'] = 'WrongValueModifier'
        position: ObjectPosition = ObjectPosition(
            player_idx = -1,
            area = ObjectPositionType.INVALID,
            id = -1,
        )

        def value_modifier_NOT_EXIST(self, value, match, mode):
            ...  # pragma: no cover

    with pytest.raises(ValueError):
        _ = WrongValueModifier()


def test_match_config_and_match_errors():
    config = MatchConfig()
    assert config.check_config()
    config.initial_hand_size = 11
    assert not config.check_config()
    config.initial_hand_size = 5
    config.initial_card_draw = 11
    assert not config.check_config()
    config.max_hand_size = 999
    config.card_number = 10
    assert not config.check_config()
    config.initial_card_draw = 2
    config.initial_dice_number = 20
    assert not config.check_config()
    config.initial_dice_number = 8
    config = MatchConfig(initial_hand_size = -1)
    assert not config.check_config()
    config = MatchConfig(initial_card_draw = -1)
    assert not config.check_config()
    config = MatchConfig(initial_dice_number = -1)
    assert not config.check_config()
    config = MatchConfig(initial_dice_reroll_times = -1)
    assert not config.check_config()
    config = MatchConfig(card_number = -1)
    assert not config.check_config()
    config = MatchConfig(max_same_card_number = -1)
    assert not config.check_config()
    config = MatchConfig(charactor_number = -1)
    assert not config.check_config()
    config = MatchConfig(max_round_number = 0)
    assert not config.check_config()
    config = MatchConfig(max_round_number = -1)
    assert not config.check_config()
    config = MatchConfig(max_hand_size = -1)
    assert not config.check_config()
    config = MatchConfig(max_dice_number = -1)
    assert not config.check_config()
    config = MatchConfig(max_summon_number = -1)
    assert not config.check_config()
    config = MatchConfig(max_support_number = -1)
    assert not config.check_config()
    config = MatchConfig(history_level = -1)
    assert not config.check_config()
    match = Match()
    match.config = config
    assert not match.start()[0]
    match = Match()
    match.player_tables = []
    assert not match.start()[0]
    match = Match()
    deck = Deck.from_str(
        '''
        default_version:4.0
        charactor:GeoMob*3
        Strategize*100
        '''
    )
    with pytest.raises(AssertionError):
        match.set_deck([])
    match.set_deck([deck, deck])
    assert not match.start()[0]
    deck = Deck.from_str(
        '''
        default_version:4.0
        charactor:GeoMob*3
        Strategize*30
        '''
    )
    match = Match()
    match.config.max_same_card_number = 30
    match.set_deck([deck, deck])
    assert match.start()[0]
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = RandomAgent(player_idx = 1)
    non_exist_tested = False
    respond_no_request = False
    req = None
    resp = None
    for _ in range(30):
        if (
            len(match.requests) == 0 
            and not respond_no_request 
            and non_exist_tested
        ):
            assert not match.need_respond(0)
            assert not match.need_respond(1)
            assert resp is not None
            with pytest.raises(ValueError):
                match.respond(resp)
        if match.need_respond(0):
            if not non_exist_tested:
                assert match.need_respond(1)
                non_exist_tested = True
                req = match.requests[0].copy(deep = True)
                assert match.check_request_exist(req)
                resp = SwitchCardResponse(
                    request = req, card_idxs = [-1])  # type: ignore
                with pytest.raises(ValueError):
                    match.respond(resp)
                resp.card_idxs = []
                resp.request.player_idx = 2
                with pytest.raises(ValueError):
                    match.respond(resp)
            resp = agent_0.generate_response(match)
            assert resp is not None
            match.respond(resp)
        elif match.need_respond(1):
            resp = agent_1.generate_response(match)
            assert resp is not None
            match.respond(resp)
        if len(match.requests) == 0:
            match.step(run_continuously = False)


def test_create_dice():
    match = Match()
    act = CreateDiceAction(
        player_idx = 0,
        number = 4,
        random = True,
        different = True
    )
    with pytest.raises(ValueError):
        match._act(act)
    act = CreateDiceAction(
        player_idx = 0,
        number = 4,
    )
    with pytest.raises(ValueError):
        match._act(act)
    act = CreateDiceAction(
        player_idx = 0,
        number = 8,
        different = True,
    )
    with pytest.raises(ValueError):
        # different over maximum color number
        match._act(act)
    act = CreateDiceAction(
        player_idx = 0,
        number = 7,
        different = True,
    )
    match._act(act)
    assert len(match.player_tables[0].dice.colors) == 7
    assert len(set(match.player_tables[0].dice.colors)) == 7
    match.player_tables[0].dice.colors.clear()
    for i in range(50):
        act = CreateDiceAction(
            player_idx = 0,
            number = 3,
            different = True,
        )
        match._act(act)
        assert len(match.player_tables[0].dice.colors) == 3
        assert len(set(match.player_tables[0].dice.colors)) == 3
        for color in match.player_tables[0].dice.colors:
            assert color != 'OMNI'
        match.player_tables[0].dice.colors.clear()


def test_id_wont_duplicate():
    s = set()
    position = ObjectPosition(
        player_idx = -1,
        area = ObjectPositionType.INVALID,
        id = -1,
    )
    for _ in range(50000):
        o = ObjectBase(
            name = 'Test object',
            position = position,
        )
        assert o.id not in s
        s.add(o.id)


def test_remove_non_exist_equip():
    match = Match()
    deck = Deck.from_str(
        '''
        default_version:4.0
        charactor:GeoMob*3
        Strategize*30
        '''
    )
    match.set_deck([deck, deck])
    match.config.max_same_card_number = None
    match.config.charactor_number = None
    match.config.card_number = None
    match.config.check_deck_restriction = False
    assert match.start()[0]
    with pytest.raises(AssertionError):
        match._action_move_object(
            MoveObjectAction(
                object_position = ObjectPosition(
                    player_idx = 0,
                    charactor_idx = 0,
                    area = ObjectPositionType.CHARACTOR,
                    id = 0,
                ),
                target_position = ObjectPosition(
                    player_idx = 0,
                    area = ObjectPositionType.HAND,
                    id = 0,
                ),
            )
        )


def test_immutable_position():
    position = ObjectPosition(
        player_idx = 0,
        area = ObjectPositionType.SUMMON,
        id = 0
    )
    with pytest.raises(AttributeError):
        position.player_idx = 1
    with pytest.raises(AttributeError):
        del position.area


def test_get_non_exist_object():
    match = Match()
    deck_str = """
    charactor:Nahida
    Strategize*30
    """
    deck = Deck.from_str(deck_str)
    match.config.charactor_number = None
    match.config.max_same_card_number = 999
    match.set_deck([deck, deck])
    assert match.start()[0]
    match.step()
    assert match.get_object(ObjectPosition(
        player_idx = 0,
        id = 0,
        area = ObjectPositionType.DECK
    )) is None
    assert match.get_object(ObjectPosition(
        player_idx = 0,
        id = 0,
        area = ObjectPositionType.SUPPORT
    )) is None


def test_vanilla_element_infusion_team_status():
    class EIC_3_3(ElementalInfusionTeamStatus):
        version: Literal['3.3'] = '3.3'
        position: ObjectPosition = ObjectPosition(
            player_idx = -1,
            area = ObjectPositionType.INVALID,
            id = -1,
        )
        usage: int = 2
        max_usage: int = 2
    desc: Dict[str, DescDictType] = {
        'TEAM_STATUS/Electro Elemental Infusion': {
            'names': {
                'zh-CN': '雷元素附魔',
                'en-US': 'Electro Elemental Infusion',
            },
            'descs': {
                '3.3': {
                    'zh-CN': '雷元素附魔',
                    'en-US': 'Electro Elemental Infusion',
                },
            }
        },
        'TEAM_STATUS/Geo Elemental Infusion': {
            'names': {
                'zh-CN': '岩元素附魔',
                'en-US': 'Geo Elemental Infusion',
            },
            'descs': {
                '3.3': {
                    'zh-CN': '岩元素附魔',
                    'en-US': 'Geo Elemental Infusion',
                },
            }
        },
        'TEAM_STATUS/Pyro Elemental Infusion': {
            'names': {
                'zh-CN': '火元素附魔',
                'en-US': 'Pyro Elemental Infusion',
            },
            'descs': {
                '3.3': {
                    'zh-CN': '火元素附魔',
                    'en-US': 'Pyro Elemental Infusion',
                },
            }
        },
        'TEAM_STATUS/Hydro Elemental Infusion': {
            'names': {
                'zh-CN': '水元素附魔',
                'en-US': 'Hydro Elemental Infusion',
            },
            'descs': {
                '3.3': {
                    'zh-CN': '水元素附魔',
                    'en-US': 'Hydro Elemental Infusion',
                },
            }
        },
        'TEAM_STATUS/Cryo Elemental Infusion': {
            'names': {
                'zh-CN': '冰元素附魔',
                'en-US': 'Cryo Elemental Infusion',
            },
            'descs': {
                '3.3': {
                    'zh-CN': '冰元素附魔',
                    'en-US': 'Cryo Elemental Infusion',
                },
            }
        },
        'TEAM_STATUS/Anemo Elemental Infusion': {
            'names': {
                'zh-CN': '风元素附魔',
                'en-US': 'Anemo Elemental Infusion',
            },
            'descs': {
                '3.3': {
                    'zh-CN': '风元素附魔',
                    'en-US': 'Anemo Elemental Infusion',
                },
            }
        },
        'TEAM_STATUS/Dendro Elemental Infusion': {
            'names': {
                'zh-CN': '草元素附魔',
                'en-US': 'Dendro Elemental Infusion',
            },
            'descs': {
                '3.3': {
                    'zh-CN': '草元素附魔',
                    'en-US': 'Dendro Elemental Infusion',
                },
            }
        },
    }
    register_class(EIC_3_3, desc)
    electro_ele_status = get_instance(TeamStatusBase, {
        'name': 'Electro Elemental Infusion'
    })
    assert (
        electro_ele_status.infused_elemental_type
        == DamageElementalType.ELECTRO
    )
    geo_ele_status = get_instance(TeamStatusBase, {
        'name': 'Geo Elemental Infusion'
    })
    assert (
        geo_ele_status.infused_elemental_type
        == DamageElementalType.GEO
    )
    pyro_ele_status = get_instance(TeamStatusBase, {
        'name': 'Pyro Elemental Infusion'
    })
    assert (
        pyro_ele_status.infused_elemental_type
        == DamageElementalType.PYRO
    )
    hydro_ele_status = get_instance(TeamStatusBase, {
        'name': 'Hydro Elemental Infusion'
    })
    assert (
        hydro_ele_status.infused_elemental_type
        == DamageElementalType.HYDRO
    )
    cryo_ele_status = get_instance(TeamStatusBase, {
        'name': 'Cryo Elemental Infusion'
    })
    assert (
        cryo_ele_status.infused_elemental_type
        == DamageElementalType.CRYO
    )
    anemo_ele_status = get_instance(TeamStatusBase, {
        'name': 'Anemo Elemental Infusion'
    })
    assert (
        anemo_ele_status.infused_elemental_type
        == DamageElementalType.ANEMO
    )
    dendro_ele_status = get_instance(TeamStatusBase, {
        'name': 'Dendro Elemental Infusion'
    })
    assert (
        dendro_ele_status.infused_elemental_type
        == DamageElementalType.DENDRO
    )


def test_blacklist_draw_card():
    match = Match()
    deck_str = """
    charactor:Nahida
    Strategize*29
    Fresh Wind of Freedom
    """
    deck = Deck.from_str(deck_str)
    match.config.charactor_number = None
    match.config.max_same_card_number = 999
    match.set_deck([deck, deck])
    assert match.start()[0]
    match.step()
    match.respond(SwitchCardResponse(
        request = match.requests[0],  # type: ignore
        card_idxs = [1, 2, 3, 4]
    ))
    match.respond(SwitchCardResponse(
        request = match.requests[0],  # type: ignore
        card_idxs = [1, 2, 3, 4]
    ))
    assert len(match.player_tables[0].hands) == 5
    assert len(match.player_tables[1].hands) == 5
    for i in range(1, 5):
        assert match.player_tables[0].hands[i].name == 'Strategize'
        assert match.player_tables[1].hands[i].name == 'Strategize'
    # then test whitelist draw card but not enough
    match._action_draw_card(DrawCardAction(
        player_idx = 0,
        number = 2,
        whitelist_names = ['Fresh Wind of Freedom'],
        draw_if_filtered_not_enough = False
    ))
    assert len(match.player_tables[0].hands) == 5
    match._action_draw_card(DrawCardAction(
        player_idx = 0,
        number = 2,
        whitelist_names = ['Fresh Wind of Freedom'],
        draw_if_filtered_not_enough = True
    ))
    assert len(match.player_tables[0].hands) == 7


if __name__ == '__main__':
    # test_object_position_validation()
    # test_match_config_and_match_errors()
    # test_objectbase_wrong_handler_name()
    # test_create_dice()
    # test_id_wont_duplicate()
    # test_remove_non_exist_equip()
    test_vanilla_element_infusion_team_status()
    test_blacklist_draw_card()
