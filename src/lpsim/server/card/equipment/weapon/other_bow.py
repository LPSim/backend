
from typing import Any, List, Literal

from ....modifiable_values import DamageIncreaseValue

from ....action import CreateObjectAction

from ....consts import ObjectPositionType, WeaponType

from ....struct import Cost
from .base import RoundEffectWeaponBase, WeaponBase


class KingsSquire(WeaponBase):
    name: Literal["King's Squire"]
    desc: str = (
        'The character deals +1 DMG. When played: The character to which this '
        'is attached will spend 2 less Elemental Dice next time they use an '
        'Elemental Skill or equip a Talent card.'
    )
    cost: Cost = Cost(same_dice_number = 3)
    version: Literal['4.0'] = '4.0'
    weapon_type: WeaponType = WeaponType.BOW

    def equip(self, match: Any) -> List[CreateObjectAction]:
        """
        attach status
        """
        return [CreateObjectAction(
            object_position = self.position.set_area(
                ObjectPositionType.CHARACTOR_STATUS),
            object_name = self.name,
            object_arguments = {}
        )]


class AmosBow(RoundEffectWeaponBase):
    name: Literal["Amos' Bow"]
    desc: str = (
        'The character deals +1 DMG. When the character uses a Skill that '
        'costs at least a total of 5 Elemental Dice and Energy, +2 additional '
        'DMG. (Once per Round)'
    )
    cost: Cost = Cost(same_dice_number = 3)
    version: Literal['3.7'] = '3.7'
    weapon_type: WeaponType = WeaponType.BOW
    max_usage_per_round: int = 1

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        condition_satisfied = False
        if (
            value.cost.total_dice_cost + value.cost.charge >= 5
            and self.usage > 0
        ):
            # have usage and costs satisfied
            self.damage_increase = 3
            condition_satisfied = True
        current_damage = value.damage
        super().value_modifier_DAMAGE_INCREASE(value, match, mode)
        if value.damage > current_damage:
            # value modified
            if condition_satisfied:
                # decrease usage
                assert mode == 'REAL'
                self.usage -= 1
        self.damage_increase = 1
        return value


Bows = AmosBow | KingsSquire
