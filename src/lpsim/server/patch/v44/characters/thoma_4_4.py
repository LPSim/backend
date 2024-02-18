from typing import Dict, List, Literal

from ....action import (
    ActionTypes,
    Actions,
    CreateObjectAction,
    MakeDamageAction,
    RemoveObjectAction,
)
from .....utils.class_registry import register_class
from ....event import SkillEndEventArguments
from ....status.team_status.base import (
    ExtraAttackTeamStatus,
    ShieldTeamStatus,
    UsageTeamStatus,
)
from ....match import Match
from ....struct import Cost, ObjectPosition
from ....consts import (
    DamageElementalType,
    DieColor,
    ElementType,
    FactionType,
    IconType,
    ObjectPositionType,
    SkillType,
    WeaponType,
)
from ....character.character_base import (
    CharacterBase,
    ElementalBurstBase,
    ElementalSkillBase,
    PhysicalNormalAttackBase,
    SkillTalent,
)
from .....utils.desc_registry import DescDictType


class BlazingBarrier_4_4(ShieldTeamStatus):
    name: Literal["Blazing Barrier"] = "Blazing Barrier"
    version: Literal["4.4"] = "4.4"
    usage: int = 1
    max_usage: int = 3


class ScorchingOoyoroi_4_4(ExtraAttackTeamStatus, UsageTeamStatus):
    name: Literal["Scorching Ooyoroi"] = "Scorching Ooyoroi"
    version: Literal["4.4"] = "4.4"
    damage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.PYRO
    trigger_skill_type: SkillType = SkillType.NORMAL_ATTACK
    usage: int = 2
    max_usage: int = 2
    decrease_usage: bool = True
    icon_type: IconType = IconType.OTHERS

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[MakeDamageAction | RemoveObjectAction | CreateObjectAction]:
        skill = match.get_object(event.action.position)
        assert skill is not None
        if skill.name == "Crimson Ooyoroi":
            # Thoma use burst Crimson Ooyoroi
            return []
        ret: List[MakeDamageAction | RemoveObjectAction | CreateObjectAction] = []
        ret += super().event_handler_SKILL_END(event, match)
        if len(ret) == 0:
            return ret
        damage_action = ret[0]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        ret.append(
            CreateObjectAction(
                object_name="Blazing Barrier",
                object_position=ObjectPosition(
                    player_idx=self.position.player_idx,
                    area=ObjectPositionType.TEAM_STATUS,
                    id=0,
                ),
                object_arguments={},
            )
        )
        return ret


class BlazingBlessing(ElementalSkillBase):
    name: Literal["Blazing Blessing"] = "Blazing Blessing"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(elemental_dice_color=DieColor.PYRO, elemental_dice_number=3)

    def get_actions(self, match: Match) -> List[Actions]:
        return super().get_actions(match) + [self.create_team_status("Blazing Barrier")]


class CrimsonOoyoroi(ElementalBurstBase):
    name: Literal["Crimson Ooyoroi"] = "Crimson Ooyoroi"
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color=DieColor.PYRO, elemental_dice_number=3, charge=2
    )

    def get_actions(self, match: Match) -> List[Actions]:
        status_args = {
            "usage": 2,
            "max_usage": 2,
        }
        if self.is_talent_equipped(match):
            status_args = {
                "usage": 3,
                "max_usage": 3,
            }
        return super().get_actions(match) + [
            self.create_team_status("Blazing Barrier"),
            self.create_team_status("Scorching Ooyoroi", status_args),
        ]


class ASubordinatesSkills_4_4(SkillTalent):
    name: Literal["A Subordinate's Skills"]
    version: Literal["4.4"] = "4.4"
    character_name: Literal["Thoma"] = "Thoma"
    skill: Literal["Crimson Ooyoroi"] = "Crimson Ooyoroi"
    cost: Cost = Cost(
        elemental_dice_color=DieColor.PYRO, elemental_dice_number=3, charge=2
    )


class Thoma_4_4(CharacterBase):
    name: Literal["Thoma"]
    version: Literal["4.4"] = "4.4"
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[PhysicalNormalAttackBase | BlazingBlessing | CrimsonOoyoroi] = []
    faction: List[FactionType] = [FactionType.INAZUMA]
    weapon_type: WeaponType = WeaponType.POLEARM

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name="Swiftshatter Spear",
                cost=PhysicalNormalAttackBase.get_cost(self.element),
            ),
            BlazingBlessing(),
            CrimsonOoyoroi(),
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTER/Thoma": {
        "names": {"en-US": "Thoma", "zh-CN": "托马"},
        "descs": {"4.4": {"en-US": "", "zh-CN": ""}},
        "image_path": "cardface/Char_Avatar_Tohma.png",  # noqa: E501
        "id": 1311,
    },
    "SKILL_Thoma_NORMAL_ATTACK/Swiftshatter Spear": {
        "names": {"en-US": "Swiftshatter Spear", "zh-CN": "迅破枪势"},
        "descs": {
            "4.4": {"en-US": "Deals 2 Physical DMG.", "zh-CN": "造成2点物理伤害。"}
        },
    },
    "SKILL_Thoma_ELEMENTAL_SKILL/Blazing Blessing": {
        "names": {"en-US": "Blazing Blessing", "zh-CN": "烈烧佑命之侍护"},
        "descs": {
            "4.4": {
                "en-US": "Deals 2 Pyro DMG, creates 1 Blazing Barrier.",
                "zh-CN": "造成2点火元素伤害，生成烈烧佑命护盾。",
            }
        },
    },
    "TEAM_STATUS/Blazing Barrier": {
        "names": {"en-US": "Blazing Barrier", "zh-CN": "烈烧佑命护盾"},
        "descs": {
            "4.4": {
                "en-US": "Shield\nGrants 1 Shield point to your active character. (Can stack. Max 3 points.)",  # noqa: E501
                "zh-CN": "护盾\n为我方出战角色提供1点护盾。（可叠加，最多叠加到3点）",  # noqa: E501
            }
        },
    },
    "SKILL_Thoma_ELEMENTAL_BURST/Crimson Ooyoroi": {
        "names": {"en-US": "Crimson Ooyoroi", "zh-CN": "真红炽火之大铠"},
        "descs": {
            "4.4": {
                "en-US": "Deals 2 Pyro DMG, creates 1 Blazing Barrier and Scorching Ooyoroi.",  # noqa: E501
                "zh-CN": "造成2点火元素伤害，生成烈烧佑命护盾和炽火大铠。",
            }
        },
    },
    "TEAM_STATUS/Scorching Ooyoroi": {
        "names": {"en-US": "Scorching Ooyoroi", "zh-CN": "炽火大铠"},
        "descs": {
            "4.4": {
                "en-US": "After your character uses a Normal Attack: Deal 1 Pyro DMG and create a Blazing Barrier.\nUsage(s): 2",  # noqa: E501
                "zh-CN": "我方角色普通攻击后：造成1点火元素伤害，生成烈烧佑命护盾。\n可用次数：2",  # noqa: E501
            }
        },
        "image_path": "status/Tohma_E.png",
    },
    "TALENT_Thoma/A Subordinate's Skills": {
        "names": {"en-US": "A Subordinate's Skills", "zh-CN": "僚佐的才巧"},
        "descs": {
            "4.4": {
                "en-US": "Combat Action: When your active character is Thoma, equip this card.\nAfter Thoma equips this card, immediately use Crimson Ooyoroi once.\nWhen your Thoma, who has this card equipped, creates a Scorching Ooyoroi, its starting Usage(s) +1.\n(You must have Thoma in your deck to add this card to your deck.)",  # noqa: E501
                "zh-CN": "战斗行动：我方出战角色为托马时，装备此牌。\n托马装备此牌后，立刻使用一次真红炽火之大铠。\n装备有此牌的托马生成的炽火大铠，初始可用次数+1。\n（牌组中包含托马，才能加入牌组）",  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Constellation_Thoma.png",  # noqa: E501
        "id": 213111,
    },
}


register_class(
    BlazingBarrier_4_4 | ScorchingOoyoroi_4_4 | ASubordinatesSkills_4_4 | Thoma_4_4,
    desc,
)
