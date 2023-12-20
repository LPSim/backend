from typing import Dict, List, Literal

from ....status.charactor_status.base import UsageCharactorStatus

from .....utils.class_registry import register_class
from ....charactor.charactor_base import SkillBase
from ....modifiable_values import CostValue, DamageIncreaseValue
from ....action import (
    Actions, CreateDiceAction, CreateObjectAction, RemoveObjectAction
)
from ....match import Match
from ....event import (
    ReceiveDamageEventArguments, RoundEndEventArguments, 
    RoundPrepareEventArguments, SkillEndEventArguments
)
from ....consts import (
    DamageType, IconType, ObjectPositionType, SkillType, WeaponType
)
from ....struct import Cost
from ....card.equipment.weapon.base import RoundEffectWeaponBase, WeaponBase
from .....utils.desc_registry import DescDictType


class LostPrayerToTheSacredWinds_4_3(WeaponBase):
    name: Literal["Lost Prayer to the Sacred Winds"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost(same_dice_number = 3)
    weapon_type: Literal[WeaponType.CATALYST] = WeaponType.CATALYST
    damage_increase: int = 0
    max_damage: int = 2

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Match
    ) -> List[Actions]:
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return []
        self.damage_increase = min(self.damage_increase + 1, self.max_damage)
        return []


class TulaytullahsRemembrance_4_3(RoundEffectWeaponBase):
    name: Literal["Tulaytullah's Remembrance"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost(same_dice_number = 3)
    weapon_type: Literal[WeaponType.CATALYST] = WeaponType.CATALYST
    max_usage_per_round: int = 2

    def value_modifier_COST(
        self, value: CostValue, match: Match, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        """
        If self use charged attack, and has usage, decrease one unaligned die 
        cost.
        """
        if self.usage <= 0:
            # not enough usage, not modify
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True, 
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR
        ):
            # not this charactor use skill, or not equipped, not modify
            return value
        skill: SkillBase = match.get_object(value.position)  # type: ignore
        assert skill is not None
        skill_type: SkillType = skill.skill_type
        if skill_type != SkillType.NORMAL_ATTACK:
            # not normal attack, not modify
            return value
        if not match.player_tables[self.position.player_idx].charge_satisfied:
            # not charged attack, not modify
            return value
        # try decrease any cost
        value.cost.decrease_cost(None)
        if mode == 'REAL':
            self.usage -= 1
        return value


class BeaconOfTheReedSeaStatus_4_3(UsageCharactorStatus):
    # TODO: in official implementation, two status are separated.
    name: Literal["Beacon of the Reed Sea"] = "Beacon of the Reed Sea"
    version: Literal["4.3"] = "4.3"
    usage: int = 1
    max_usage: int = 999

    icon_type: IconType = IconType.ATK_UP

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Match,
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        When equipped charactor is using skill, increase the damage.
        """
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not current charactor using skill
            return value
        # modify damage
        assert mode == 'REAL'
        value.damage += self.usage
        self.usage = 0
        return value

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[RemoveObjectAction]:
        """
        In prepare, remove self
        """
        self.usage = 0
        return self.check_should_remove()


class BeaconOfTheReedSea_4_3(RoundEffectWeaponBase):
    name: Literal["Beacon of the Reed Sea"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost(same_dice_number = 3)
    weapon_type: Literal[WeaponType.CLAYMORE] = WeaponType.CLAYMORE
    max_usage_per_round: int = 1  # usage for elemental skill

    receive_damage_usage: int = 1
    max_receive_damage_usage_per_round: int = 1

    def equip(self, match: Match) -> List[Actions]:
        self.usage = self.max_usage_per_round
        self.receive_damage_usage = self.max_receive_damage_usage_per_round
        return []

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        self.usage = self.max_usage_per_round
        self.receive_damage_usage = self.max_receive_damage_usage_per_round
        return []

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[CreateObjectAction]:
        if self.receive_damage_usage == 0:
            # already used
            return []
        if not self.position.check_position_valid(
            event.final_damage.target_position, match, player_idx_same = True,
            charactor_idx_same = True, area_same = True,
            source_area = ObjectPositionType.CHARACTOR,
        ):
            # not equipped, or not self receive damage
            return []
        if event.final_damage.damage_type != DamageType.DAMAGE:
            # not damage
            return []
        # create status
        self.receive_damage_usage -= 1
        return [CreateObjectAction(
            object_name = self.name,
            object_position = self.position.set_area(
                ObjectPositionType.CHARACTOR_STATUS
            ),
            object_arguments = {}
        )]

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[CreateObjectAction]:
        if self.usage == 0:
            # already used
            return []
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR
        ):
            # not self, or not equipped
            return []
        skill: SkillBase = match.get_object(
            event.action.position)  # type: ignore
        assert skill is not None
        if skill.skill_type != SkillType.ELEMENTAL_SKILL:
            # not elemental skill
            return []
        self.usage -= 1
        return [CreateObjectAction(
            object_name = self.name,
            object_position = self.position.set_area(
                ObjectPositionType.CHARACTOR_STATUS
            ),
            object_arguments = {}
        )]


class PrimordialJadeWingedSpear_4_3(WeaponBase):
    name: Literal["Primordial Jade Winged-Spear"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost(same_dice_number = 3)
    weapon_type: Literal[WeaponType.POLEARM] = WeaponType.POLEARM
    max_damage: int = 3

    def equip(self, match: Match) -> List[Actions]:
        self.damage_increase = 1
        return []

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> List[Actions]:
        # reset damage increase
        self.damage_increase = 1
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[CreateObjectAction]:
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR
        ):
            # not self, or not equipped
            return []
        # increase damage
        self.damage_increase = min(self.damage_increase + 1, self.max_damage)
        return []


class LightOfFoliarIncision_4_3(RoundEffectWeaponBase):
    name: Literal["Light of Foliar Incision"]
    version: Literal["4.3"] = "4.3"
    cost: Cost = Cost(same_dice_number = 3)
    weapon_type: Literal[WeaponType.SWORD] = WeaponType.SWORD
    max_usage_per_round: int = 2

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Match
    ) -> List[CreateDiceAction]:
        if self.usage == 0:
            # out of usage
            return []
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL,
            source_area = ObjectPositionType.CHARACTOR
        ):
            # not self, or not equipped
            return []
        skill: SkillBase = match.get_object(
            event.action.position)  # type: ignore
        assert skill is not None
        if skill.skill_type != SkillType.NORMAL_ATTACK:
            # not normal attack
            return []
        self.usage -= 1
        return [CreateDiceAction(
            player_idx = self.position.player_idx,
            number = 1,
            different = True
        )]


desc: Dict[str, DescDictType] = {
    "WEAPON/Lost Prayer to the Sacred Winds": {
        "names": {
            "en-US": "Lost Prayer to the Sacred Winds",
            "zh-CN": "四风原典"
        },
        "descs": {
            "4.3": {
                "en-US": "For each point of \"Bonus DMG\" this card has, character deals +1 DMG.\nEnd Phase: This card gains 1 point of \"Bonus DMG.\" (Max 2 points)\n(Can only be equipped by Catalyst Characters. Each Character can equip at most 1 Weapon.",  # noqa: E501
                "zh-CN": "此牌每有1点「伤害加成」，角色造成的伤害+1。\n结束阶段：此牌累积1点「伤害加成」。（最多累积到2点）\n（「法器」角色才能装备。角色最多装备1件「武器」）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Weapon_Yuandian.png",  # noqa: E501
        "id": 311106
    },
    "WEAPON/Tulaytullah's Remembrance": {
        "names": {
            "en-US": "Tulaytullah's Remembrance",
            "zh-CN": "图莱杜拉的回忆"
        },
        "descs": {
            "4.3": {
                "en-US": "The character deals +1 DMG.\nWhen the character uses a Charged Attack: Spend 1 less Unaligned Element. (Can be triggered up to twice per Round)\n(Only Catalyst Characters can equip this. A character can equip a maximum of 1 Weapon)",  # noqa: E501
                "zh-CN": "角色造成的伤害+1。\n角色进行重击时：少花费1个无色元素。（每回合最多触发2次）\n（「法器」角色才能装备。角色最多装备1件「武器」）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Weapon_Tulaidu.png",  # noqa: E501
        "id": 311107
    },
    "CHARACTOR_STATUS/Beacon of the Reed Sea": {
        "names": {
            "en-US": "Beacon of the Reed Sea",
            "zh-CN": "苇海信标"
        },
        "descs": {
            "4.3": {
                "en-US": "Increase DMG dealt by character this Round the next time they deal DMG by the usage of this status.",  # noqa: E501
                "zh-CN": "本回合内，角色下次造成的伤害额外增加该状态的使用次数点。"  # noqa: E501
            }
        },
    },
    "WEAPON/Beacon of the Reed Sea": {
        "names": {
            "en-US": "Beacon of the Reed Sea",
            "zh-CN": "苇海信标"
        },
        "descs": {
            "4.3": {
                "en-US": "The character deals +1 DMG.\nAfter the character uses an Elemental Skill: +1 additional DMG dealt by character this Round the next time they deal DMG. (Once per Round)\nAfter this character takes DMG: +1 additional DMG dealt by character this Round the next time they deal DMG. (Once per Round)\n(Only Claymore Characters can equip this. A character can equip a maximum of 1 Weapon)",  # noqa: E501
                "zh-CN": "角色造成的伤害+1。\n角色使用「元素战技」后：本回合内，角色下次造成的伤害额外+1。（每回合1次）\n角色受到伤害后：本回合内，角色下次造成的伤害额外+1。（每回合1次）\n（「双手剑」角色才能装备。角色最多装备1件「武器」）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Weapon_Xinbiao.png",  # noqa: E501
        "id": 311306
    },
    "WEAPON/Primordial Jade Winged-Spear": {
        "names": {
            "en-US": "Primordial Jade Winged-Spear",
            "zh-CN": "和璞鸢"
        },
        "descs": {
            "4.3": {
                "en-US": "The character deals +1 DMG.\nAfter this character uses a Skill: Until the end of this Round, +1 additional DMG provided by this card. (Up to +2 DMG total.)\n(Only Polearm Characters can equip this. A character can equip a maximum of 1 Weapon)",  # noqa: E501
                "zh-CN": "角色造成的伤害+1。\n角色使用技能后：直到回合结束前，此牌所提供的伤害加成值额外+1。（最多累积到+2）\n（「长柄武器」角色才能装备。角色最多装备1件「武器」）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Weapon_Hepuyuan.png",  # noqa: E501
        "id": 311407
    },
    "WEAPON/Light of Foliar Incision": {
        "names": {
            "en-US": "Light of Foliar Incision",
            "zh-CN": "裁叶萃光"
        },
        "descs": {
            "4.3": {
                "en-US": "The character deals +1 DMG.\nAfter the character uses a Normal Attack: Create 1 random Elemental Die. (Can be triggered up to twice per Round)\n(Only Sword Characters can equip this. A character can equip a maximum of 1 Weapon)",  # noqa: E501
                "zh-CN": "角色造成的伤害+1。\n角色使用「普通攻击」后：生成1个随机类型的元素骰。（每回合最多触发2次）\n（「单手剑」角色才能装备。角色最多装备1件「武器」）"  # noqa: E501
            }
        },
        "image_path": "cardface/Modify_Weapon_Caiye.png",  # noqa: E501
        "id": 311506
    },
}


register_class(
    LostPrayerToTheSacredWinds_4_3 | TulaytullahsRemembrance_4_3
    | BeaconOfTheReedSea_4_3 | PrimordialJadeWingedSpear_4_3
    | LightOfFoliarIncision_4_3 | BeaconOfTheReedSeaStatus_4_3, desc
)
