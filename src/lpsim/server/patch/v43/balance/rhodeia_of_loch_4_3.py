from typing import Dict, List, Literal

from ....struct import ObjectPosition

from ....action import ChargeAction, CreateRandomObjectAction

from .....utils.desc_registry import DescDictType

from .....utils.class_registry import register_class

from ....character.character_base import ElementalNormalAttackBase

from ....summon.base import DefendSummonBase

from ....consts import ELEMENT_TO_DAMAGE_TYPE, DamageElementalType, ObjectPositionType

from ....match import Match
from ....character.hydro.rhodeia_4_2 import (
    RhodeiaOfLoch_4_2,
    RhodeiaElementSkill as RES_4_2,
    TideAndTorrent,
)


class Frog_4_3(DefendSummonBase):
    name: Literal["Oceanic Mimic: Frog"] = "Oceanic Mimic: Frog"
    version: Literal["4.3"] = "4.3"
    usage: int = 1
    max_usage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 2
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1
    attack_until_run_out_of_usage: bool = True


mimic_names = [
    "Oceanic Mimic: Squirrel",
    "Oceanic Mimic: Frog",
    "Oceanic Mimic: Raptor",
]


class RhodeiaElementSkill(RES_4_2):
    version: Literal["4.3"] = "4.3"

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.name == "Oceanid Mimic Summoning":
            pass
        else:
            assert self.name == "The Myriad Wilds"
            self._summon_number = 2
            self.cost.elemental_dice_number = 5

    def get_actions(
        self, match: Match
    ) -> List[ChargeAction | CreateRandomObjectAction]:
        """
        create object
        """
        exist_names, unexist_names = self._get_exist_unexist_names(match)
        ret: List[ChargeAction | CreateRandomObjectAction] = []
        target_position = ObjectPosition(
            player_idx=self.position.player_idx, area=ObjectPositionType.SUMMON, id=-1
        )
        if len(exist_names) == 2:
            # already 2, only refresh existing
            ret.append(
                CreateRandomObjectAction(
                    object_names=exist_names,
                    object_position=target_position,
                    object_arguments={"version": self.version},
                    number=self._summon_number,
                )
            )
        elif (
            len(unexist_names) >= self._summon_number
            and self._summon_number + len(exist_names) <= 2
        ):
            # enough unexist and will not exceed 2
            ret.append(
                CreateRandomObjectAction(
                    object_names=unexist_names,
                    object_position=target_position,
                    object_arguments={"version": self.version},
                    number=self._summon_number,
                )
            )
        else:
            # not enough unexist, create all - 1 unexist and refresh random exist
            ret.append(
                CreateRandomObjectAction(
                    object_names=unexist_names,
                    object_position=target_position,
                    object_arguments={"version": self.version},
                    number=len(unexist_names) - 1,
                )
            )
            ret.append(
                CreateRandomObjectAction(
                    object_names=exist_names,
                    object_position=target_position,
                    object_arguments={"version": self.version},
                    number=self._summon_number - len(unexist_names) + 1,
                )
            )
        ret.append(self.charge_self(1))
        return ret


class RhodeiaOfLoch_4_3(RhodeiaOfLoch_4_2):
    version: Literal["4.3"] = "4.3"
    skills: List[ElementalNormalAttackBase | RhodeiaElementSkill | TideAndTorrent] = []

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name="Surge",
                damage_type=ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost=ElementalNormalAttackBase.get_cost(self.element),
            ),
            RhodeiaElementSkill(
                name="Oceanid Mimic Summoning",
            ),
            RhodeiaElementSkill(
                name="The Myriad Wilds",
            ),
            TideAndTorrent(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTER/Rhodeia of Loch": {
        "descs": {"4.3": {"zh-CN": "", "en-US": ""}},
    },
    "SKILL_Rhodeia of Loch_ELEMENTAL_BURST/Tide and Torrent": {
        "descs": {
            "4.3": {
                "zh-CN": "$SKILL_Rhodeia of Loch_ELEMENTAL_BURST/Tide and Torrent|descs|4.2|zh-CN",  # noqa: E501
                "en-US": "$SKILL_Rhodeia of Loch_ELEMENTAL_BURST/Tide and Torrent|descs|4.2|en-US",  # noqa: E501
            }
        }
    },
    "SKILL_Rhodeia of Loch_ELEMENTAL_SKILL/Oceanid Mimic Summoning": {
        "descs": {
            "4.3": {
                "zh-CN": "随机召唤1种纯水幻形。（最多生成2种，超过时随机生成已存在的纯水幻形）",  # noqa: E501
                "en-US": "Randomly summons 1 Oceanid Mimic (Maximum 2 types of mimics. If exceeded, randomly generate preexisting ones.).",  # noqa: E501
            }
        }
    },
    "SKILL_Rhodeia of Loch_ELEMENTAL_SKILL/The Myriad Wilds": {
        "descs": {
            "4.3": {
                "zh-CN": "随机召唤2种纯水幻形。（最多生成2种，超过时随机生成已存在的纯水幻形）",  # noqa: E501
                "en-US": "Randomly summons 2 Oceanid Mimic (Maximum 2 types of mimics. If exceeded, randomly generate preexisting ones.).",  # noqa: E501
            }
        }
    },
    "SKILL_Rhodeia of Loch_NORMAL_ATTACK/Surge": {
        "descs": {
            "4.3": {"zh-CN": "造成1点水元素伤害。", "en-US": "Deals 1 Hydro DMG."}
        }
    },
    "SUMMON/Oceanic Mimic: Frog": {
        "descs": {
            "4.3": {
                "zh-CN": "我方出战角色受到伤害时：抵消1点伤害。\n可用次数：1，耗尽时不弃置此牌。\n\n结束阶段：如果可用次数已耗尽：弃置此牌，造成2点水元素伤害。",  # noqa: E501
                "en-US": "When your active character takes DMG: Decrease DMG taken by 1. When the Usages are depleted, this card will not be discarded. At the End Phase, if Usage(s) have been depleted: Discard this card, deal 2 Hydro DMG. Usage(s): 1",  # noqa: E501
            }
        },
    },
}


register_class(RhodeiaOfLoch_4_3 | Frog_4_3, desc)
