from typing import Dict, Literal

import pytest
from lpsim.server.card.support.companions import CompanionBase
from lpsim.server.card.event.foods import FoodCardBase
from lpsim.server.card.support.base import SupportBase
from lpsim.server.consts import DieColor
from lpsim.server.summon.base import SummonBase
from lpsim.server.character.character_base import CharacterBase
from lpsim.utils.desc_registry import (
    DescDictType,
    desc_exist,
    get_desc_patch,
    update_cost,
    update_desc,
)
from lpsim.utils.class_registry import (
    get_class_list_by_base_class,
    get_instance,
    register_class,
)
from lpsim.server.struct import Cost
from lpsim.server.object_base import EventCardBase


def test_class_registry():
    class Sleep_1_0(EventCardBase):
        name: Literal["Sleep"]
        version: Literal["1.0"] = "1.0"
        cost: Cost = Cost()

    sleep_desc: Dict[str, DescDictType] = {
        "CARD/Sleep": {
            "names": {
                "zh-CN": "睡觉",
                "en-US": "Sleep",
            }
        }
    }

    with pytest.raises(AssertionError):
        # no desc, cannot register
        register_class(Sleep_1_0)
    with pytest.raises(AssertionError):
        # desc without version info, cannot register
        register_class(Sleep_1_0, sleep_desc)
    sleep_desc["CARD/Sleep"]["descs"] = {
        "3.0": {
            "zh-CN": "睡觉",
            "en-US": "Sleep",
        }
    }
    with pytest.raises(AssertionError):
        # desc with wrong version info, cannot register
        register_class(Sleep_1_0, sleep_desc)
    sleep_desc["CARD/Sleep"]["descs"] = {
        "1.0": {
            "zh-CN": "睡觉",
            "en-US": "Sleep",
        }
    }
    register_class(Sleep_1_0, sleep_desc)
    # duplicate, should print warning
    register_class(Sleep_1_0)
    with pytest.raises(AssertionError):
        # duplicate and not same, raise error
        class Sleep2_1_0(EventCardBase):
            name: Literal["Sleep"]
            version: Literal["1.0"] = "1.0"
            cost: Cost = Cost()

        register_class(Sleep2_1_0)
    with pytest.raises(AssertionError):
        # wrong base class, get error
        get_instance(CharacterBase, {"name": "Sleep", "version": "1.0"})
    with pytest.raises(AssertionError):
        # wrong base classes, get error
        get_instance(CharacterBase | SummonBase, {"name": "Sleep", "version": "1.0"})
    # contain right class, get instance
    ins = get_instance(EventCardBase, {"name": "Sleep", "version": "1.0"})
    assert ins.name == "Sleep"
    ins = get_instance(SupportBase | EventCardBase, {"name": "Sleep", "version": "1.0"})
    assert ins.name == "Sleep"
    ins = get_instance(EventCardBase, {"name": "Sleep"})
    assert ins.name == "Sleep"
    with pytest.raises(AssertionError):
        # wrong version, get error
        get_instance(EventCardBase, {"name": "Sleep", "version": "0.1"})


def test_desc_registry():
    sleep_desc: Dict[str, DescDictType] = {
        "CARD/SleepDesc": {
            "names": {
                "zh-CN": "睡觉",
                "en-US": "Sleep",
            },
            "id": 999998,
            "image_path": "http://www.baidu.com",
            "descs": {
                "1.0": {
                    "zh-CN": "睡觉",
                    "en-US": "Sleep",
                }
            },
        }
    }
    assert not desc_exist("CARD", "SleepDesc", "1.0")
    update_desc(sleep_desc)
    assert desc_exist("CARD", "SleepDesc", "1.0")
    assert not desc_exist("CARD", "SleepDesc", "2.0")
    # can add again, but print warning
    update_desc(sleep_desc)
    sleep_desc["CARD/SleepDesc"]["descs"]["1.0"]["zh-CN"] = "睡觉1"
    with pytest.raises(ValueError):
        # duplicate key, raise error
        update_desc(sleep_desc)
    sleep_desc["CARD/SleepDesc"]["descs"]["1.0"]["zh-CN"] = "睡觉"
    sleep_desc["CARD/SleepDesc"]["names"]["zh-CN"] = "睡觉1"
    with pytest.raises(ValueError):
        # duplicate key, raise error
        update_desc(sleep_desc)
    sleep_patch: Dict[str, DescDictType] = {
        "CARD/SleepDesc": {
            "descs": {
                "2.0": {
                    "zh-CN": "睡觉2",
                    "en-US": "Sleep2",
                }
            }
        }
    }
    # only update new version descs
    update_desc(sleep_patch)
    assert desc_exist("CARD", "SleepDesc", "2.0")
    sleep_patch_2: Dict[str, DescDictType] = {
        "CARD/SleepDesc": {
            "descs": {
                "3.0": {
                    "zh-CN": "$CARD/SleepDesc|descs|1.0|zh-CN",
                    "en-US": "$CARD/SleepDesc|descs|1.0|en-US",
                }
            }
        }
    }
    update_desc(sleep_patch_2)
    # use key reference to update
    patch = get_desc_patch()
    assert "CARD/SleepDesc" in patch
    assert "descs" in patch["CARD/SleepDesc"]
    assert patch["CARD/SleepDesc"]["descs"]["3.0"]["zh-CN"] == "睡觉"
    assert patch["CARD/SleepDesc"]["descs"]["2.0"]["zh-CN"] == "睡觉2"
    assert patch["CARD/SleepDesc"]["descs"]["1.0"]["zh-CN"] == "睡觉"
    assert patch["CARD/SleepDesc"]["descs"]["3.0"]["en-US"] == "Sleep"
    assert patch["CARD/SleepDesc"]["descs"]["2.0"]["en-US"] == "Sleep2"
    assert patch["CARD/SleepDesc"]["descs"]["1.0"]["en-US"] == "Sleep"
    sleep_patch_3: Dict[str, DescDictType] = {
        "CARD/SleepDesc": {
            "descs": {
                "3.0": {
                    "zh-CN": "$CARD/SleepDesc|descs|1.0|zh-CN",
                    "en-US": "$CARD/SleepDesc|descs|1.0|en-US",
                }
            }
        }
    }
    # have duplicate key, print warning
    update_desc(sleep_patch_3)
    sleep_patch_4: Dict[str, DescDictType] = {
        "CARD/SleepDesc": {
            "descs": {
                "5.0": {
                    "zh-CN": "$CARD/SleepDesc|descs|4.0|zh-CN",
                    "en-US": "$CARD/SleepDesc|descs|4.0|en-US",
                }
            }
        }
    }
    with pytest.raises(ValueError):
        # wrong key, raise error
        update_desc(sleep_patch_4)
    empty_name: Dict[str, DescDictType] = {
        "CARD/EmptyName": {
            "names": {
                "zh-CN": "",
            }
        }
    }
    with pytest.raises(ValueError):
        # empty name, raise error
        update_desc(empty_name)
    empty_name_2: Dict[str, DescDictType] = {
        "CARD/EmptyName2": {
            "names": {
                "zh-CN": "XXX",
            }
        }
    }
    with pytest.raises(ValueError):
        # empty name, raise error
        update_desc(empty_name_2)


def test_get_class_list():
    nlist = get_class_list_by_base_class(SupportBase, "3.3", set(["NRE"]))
    assert "NRE" not in nlist
    assert "Wangshu Inn" in nlist
    assert len(nlist) == 19  # initial 20 and except NRE
    nlist = get_class_list_by_base_class(SupportBase, "3.3")
    assert "NRE" in nlist
    assert len(nlist) == 20  # initial 20
    nlist = get_class_list_by_base_class(SupportBase | FoodCardBase, "3.3")
    assert len(nlist) == 28  # initial 20 + 8 food cards
    nlist = get_class_list_by_base_class(FoodCardBase, "4.2")
    assert len(nlist) == 12  # in 4.2, there are 12 food cards
    nlist = get_class_list_by_base_class(FoodCardBase, "3.3", set(["NRE"]))
    assert len(nlist) == 8
    nlist = get_class_list_by_base_class(CompanionBase, "3.3")
    assert len(nlist) == 12


def test_existing_cost():
    """
    request existing cost for mobs, Starsigns, and Strategize.
    """
    pyro_skill_cost = Cost(elemental_dice_color=DieColor.PYRO, elemental_dice_number=3)
    hydro_normal_cost = Cost(
        elemental_dice_color=DieColor.HYDRO, elemental_dice_number=1, any_dice_number=2
    )
    dendro_burst_cost = Cost(
        elemental_dice_color=DieColor.DENDRO,
        elemental_dice_number=3,
        charge=2,
    )
    starsigns_cost = Cost(any_dice_number=2)
    strategize_cost = Cost(same_dice_number=1)
    p = get_desc_patch()
    assert "cost" in p["SKILL_PyroMob_ELEMENTAL_SKILL/Pyro Elemental Skill"]
    desc_cost = Cost(
        **p["SKILL_PyroMob_ELEMENTAL_SKILL/Pyro Elemental Skill"]["cost"]["1.0"]
    )
    desc_cost.label = 0
    assert pyro_skill_cost == desc_cost
    assert "cost" in p["SKILL_HydroMobMage_NORMAL_ATTACK/Hydro Normal Attack"]
    desc_cost = Cost(
        **p["SKILL_HydroMobMage_NORMAL_ATTACK/Hydro Normal Attack"]["cost"]["1.0"]
    )
    desc_cost.label = 0
    assert hydro_normal_cost == desc_cost
    assert "cost" in p["SKILL_HydroMob_NORMAL_ATTACK/Physical Normal Attack"]
    desc_cost = Cost(
        **p["SKILL_HydroMob_NORMAL_ATTACK/Physical Normal Attack"]["cost"]["1.0"]
    )
    desc_cost.label = 0
    assert hydro_normal_cost == desc_cost
    assert "cost" in p["SKILL_DendroMob_ELEMENTAL_BURST/Dendro Elemental Burst"]
    desc_cost = Cost(
        **p["SKILL_DendroMob_ELEMENTAL_BURST/Dendro Elemental Burst"]["cost"]["1.0"]
    )
    desc_cost.label = 0
    assert dendro_burst_cost == desc_cost
    assert "cost" in p["CARD/Starsigns"]
    desc_cost = Cost(**p["CARD/Starsigns"]["cost"]["3.3"])
    desc_cost.label = 0
    assert starsigns_cost == desc_cost
    assert "cost" in p["CARD/Strategize"]
    desc_cost = Cost(**p["CARD/Strategize"]["cost"]["3.3"])
    desc_cost.label = 0
    assert strategize_cost == desc_cost


def test_register_cost():
    dd_desc: Dict[str, DescDictType] = {
        "CARD/DD": {
            "names": {
                "zh-CN": "滴滴",
                "en-US": "DD",
            },
            "id": 999998,
            "image_path": "http://www.baidu.com",
            "descs": {
                "1.0": {
                    "zh-CN": "滴滴",
                    "en-US": "DD",
                }
            },
        }
    }
    dd_cost = Cost(same_dice_number=1)
    with pytest.raises(ValueError):
        # no desc, cannot register cost
        update_cost("CARD", "DD", "1.0", dd_cost)
    update_desc(dd_desc)
    p = get_desc_patch()
    assert "CARD/DD" in p
    assert "cost" not in p["CARD/DD"]
    update_cost("CARD", "DD", "1.0", dd_cost)
    p = get_desc_patch()
    assert "CARD/DD" in p
    assert "cost" in p["CARD/DD"]
    assert "1.0" in p["CARD/DD"]["cost"]
    assert p["CARD/DD"]["cost"]["1.0"]["same_dice_number"] == 1
    assert p["CARD/DD"]["cost"]["1.0"]["any_dice_number"] == 0


def test_wrong_id():
    wrong_prefix = ["CHARACTER_STATUS", "SKILL", "SUMMON", "TEAM_STATUS"]
    for wp in wrong_prefix:
        wrong_id_desc: Dict[str, DescDictType] = {
            f"{wp}/DD": {
                "names": {
                    "zh-CN": "滴滴",
                    "en-US": "DD",
                },
                "id": 999998,
                "image_path": "http://www.baidu.com",
                "descs": {
                    "1.0": {
                        "zh-CN": "滴滴",
                        "en-US": "DD",
                    }
                },
            }
        }
        with pytest.raises(ValueError):
            update_desc(wrong_id_desc)
    for wp in wrong_prefix:
        right_desc: Dict[str, DescDictType] = {
            f"{wp}/DDD": {
                "names": {
                    "zh-CN": "滴滴",
                    "en-US": "DD",
                },
                "image_path": "http://www.baidu.com",
                "descs": {
                    "1.0": {
                        "zh-CN": "滴滴",
                        "en-US": "DD",
                    }
                },
            }
        }
        update_desc(right_desc)


if __name__ == "__main__":
    test_class_registry()
    test_desc_registry()
    test_get_class_list()
    test_existing_cost()
    test_register_cost()
    test_wrong_id()
