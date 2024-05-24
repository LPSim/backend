from typing import Literal
from lpsim.server.action import ChargeAction
from lpsim.server.card.equipment.weapon.base import WeaponBase
from lpsim.server.consts import (
    DamageElementalType,
    ObjectPositionType,
    SkillType,
    WeaponType,
)
from lpsim.server.event import ReceiveDamageEventArguments
from lpsim.server.match import Match
from lpsim.server.modifiable_values import DamageIncreaseValue
from lpsim.server.struct import Cost
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class RightfulReward_4_6(WeaponBase):
    name: Literal["Rightful Reward"]
    version: Literal["4.6"] = "4.6"
    weapon_type: WeaponType = WeaponType.POLEARM
    damage_increase: int = 2
    cost: Cost = Cost(same_dice_number=2)
    usage: int = 0

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> DamageIncreaseValue:
        """
        When equipped character is using skill, increase the damage.
        """
        if self.position.area != ObjectPositionType.CHARACTER:
            # not equipped
            return value
        if not value.is_corresponding_character_use_damage_skill(
            self.position, match, SkillType.ELEMENTAL_BURST
        ):
            # not current character using elemental burst
            return value
        if (
            value.damage_elemental_type == DamageElementalType.PIERCING
        ):  # pragma: no cover  # noqa
            # piercing damage
            return value
        # modify damage
        value.damage += self.damage_increase
        return value

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> list[ChargeAction]:
        if self.position.not_satisfy(
            "both pidx=same and target area=character active=true "
            "and source area=character",
            event.final_damage.target_position,
            match,
        ):
            # damage not our active, or target not active character, or source not
            # equipped
            return []
        self.usage += 1
        if self.usage >= 3:
            self.usage -= 3
            return [
                ChargeAction(
                    player_idx=self.position.player_idx,
                    character_idx=self.position.character_idx,
                    charge=1,
                )
            ]
        return []


desc: dict[str, DescDictType] = {
    "WEAPON/Rightful Reward": {
        "names": {"en-US": "Rightful Reward", "zh-CN": "公义的酬报"},
        "descs": {
            "4.6": {
                "en-US": "Character's Elemental Burst deals +2 DMG.\nAfter your active character takes DMG or is healed: Gain 1 Principle of Justice point. If this card has already accumulated 3 such points, consume 3 points and grant this character 1 Energy.\n(Only Polearm Characters can equip this. A character can equip a maximum of 1 Weapon)",  # noqa
                "zh-CN": "角色使用「元素爆发」造成的伤害+2。\n我方出战角色受到伤害或治疗后：累积1点「公义之理」。如果此牌已累积3点「公义之理」，则消耗3点「公义之理」，使角色获得1点充能。\n（「长柄武器」角色才能装备。角色最多装备1件「武器」）",  # noqa
            }
        },
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Modify_Weapon_Gongyichoubao.png",  # noqa
        "id": 311408,
    },
}


register_class(RightfulReward_4_6, desc)
