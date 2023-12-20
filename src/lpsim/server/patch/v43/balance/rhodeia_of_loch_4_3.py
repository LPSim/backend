from typing import Dict, List, Literal

from .....utils.desc_registry import DescDictType

from .....utils.class_registry import register_class

from ....charactor.charactor_base import ElementalNormalAttackBase

from ....summon.base import DefendSummonBase

from ....consts import ELEMENT_TO_DAMAGE_TYPE, DamageElementalType

from ....match import Match
from ....charactor.hydro.rhodeia_4_2 import (
    RhodeiaOfLoch_4_2, RhodeiaElementSkill as RES_4_2, TideAndTorrent
)


class Frog_4_3(DefendSummonBase):
    name: Literal['Oceanic Mimic: Frog'] = 'Oceanic Mimic: Frog'
    version: Literal['4.3'] = '4.3'
    usage: int = 1
    max_usage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.HYDRO
    damage: int = 2
    min_damage_to_trigger: int = 1
    max_in_one_time: int = 1
    attack_until_run_out_of_usage: bool = True


mimic_names = [
    'Oceanic Mimic: Squirrel',
    'Oceanic Mimic: Frog',
    'Oceanic Mimic: Raptor'
]


class RhodeiaElementSkill(RES_4_2):
    version: Literal['4.3'] = '4.3'

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.name == 'Oceanid Mimic Summoning':
            pass
        else:
            assert self.name == 'The Myriad Wilds'
            self.summon_number = 2
            self.cost.elemental_dice_number = 5

    def get_next_summon_names(
        self, match: Match, occupied: List[int]
    ) -> int:
        """
        Get next summon names randomly, but fit the rule that try to avoid
        summoning the same type. And maximum summon number should be 2, if
        exceed, randomly re-generate existing summon.
        """
        summons = match.player_tables[self.position.player_idx].summons
        summon_names = [x.name for x in summons]
        select_idx = []
        exist_idx = []
        for idx, name in enumerate(mimic_names):
            if name not in summon_names and idx not in occupied:
                select_idx.append(idx)
            if name in summon_names:
                exist_idx.append(idx)
        if len(select_idx) <= 1:
            # exist at least 2, get one from not occupied and exist
            select_idx = [x for x in exist_idx if x not in occupied]
        if match.config.recreate_mode:
            sname = match.config.random_object_information['rhodeia'].pop(0)
            s_idx = -1
            for idx, name in enumerate(mimic_names):
                if sname.lower() in name.lower():
                    s_idx = idx
                    break
            else:
                raise AssertionError(f'Unknown summon name {sname}')
            assert s_idx in select_idx
            return s_idx
        return select_idx[int(match._random() * len(select_idx))]


class RhodeiaOfLoch_4_3(RhodeiaOfLoch_4_2):
    version: Literal['4.3'] = '4.3'
    skills: List[
        ElementalNormalAttackBase
        | RhodeiaElementSkill | TideAndTorrent
    ] = []

    def _init_skills(self) -> None:
        self.skills = [
            ElementalNormalAttackBase(
                name = 'Surge',
                damage_type = ELEMENT_TO_DAMAGE_TYPE[self.element],
                cost = ElementalNormalAttackBase.get_cost(self.element),
            ),
            RhodeiaElementSkill(
                name = 'Oceanid Mimic Summoning',
            ),
            RhodeiaElementSkill(
                name = 'The Myriad Wilds',
            ),
            TideAndTorrent(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTOR/Rhodeia of Loch": {
        "descs": {
            "4.3": {
                "zh-CN": "",
                "en-US": ""
            }
        },
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
                "en-US": "Randomly summons 1 Oceanid Mimic (Maximum 2 types of mimics. If exceeded, randomly generate preexisting ones.)."  # noqa: E501
            }
        }
    },
    "SKILL_Rhodeia of Loch_ELEMENTAL_SKILL/The Myriad Wilds": {
        "descs": {
            "4.3": {
                "zh-CN": "随机召唤2种纯水幻形。（最多生成2种，超过时随机生成已存在的纯水幻形）",  # noqa: E501
                "en-US": "Randomly summons 2 Oceanid Mimic (Maximum 2 types of mimics. If exceeded, randomly generate preexisting ones.)."  # noqa: E501
            }
        }
    },
    "SKILL_Rhodeia of Loch_NORMAL_ATTACK/Surge": {
        "descs": {
            "4.3": {
                "zh-CN": "造成1点水元素伤害。",
                "en-US": "Deals 1 Hydro DMG."
            }
        }
    },
    "SUMMON/Oceanic Mimic: Frog": {
        "descs": {
            "4.3": {
                "zh-CN": "我方出战角色受到伤害时：抵消1点伤害。\n可用次数：1，耗尽时不弃置此牌。\n\n结束阶段：如果可用次数已耗尽：弃置此牌，造成2点水元素伤害。",  # noqa: E501
                "en-US": "When your active character takes DMG: Decrease DMG taken by 1. When the Usages are depleted, this card will not be discarded. At the End Phase, if Usage(s) have been depleted: Discard this card, deal 2 Hydro DMG. Usage(s): 1"  # noqa: E501
            }
        },
    },
}


register_class(RhodeiaOfLoch_4_3 | Frog_4_3, desc)
