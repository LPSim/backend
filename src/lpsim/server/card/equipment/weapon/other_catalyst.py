from typing import Any, Literal

from .....utils.class_registry import register_class

from ....modifiable_values import DamageIncreaseValue

from ....struct import Cost

from ....consts import (
    ElementalReactionType, ObjectPositionType, ObjectType, 
    WeaponType
)
from .base import RoundEffectWeaponBase


class AThousandFloatingDreams_3_7(RoundEffectWeaponBase):
    name: Literal['A Thousand Floating Dreams']
    type: Literal[ObjectType.WEAPON] = ObjectType.WEAPON
    version: Literal['3.7'] = '3.7'
    weapon_type: WeaponType = WeaponType.CATALYST

    cost: Cost = Cost(same_dice_number = 3)
    max_usage_per_round: int = 2

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, 
        match: Any, mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        """
        First +1 DMG if self charactor use skill. Then if this damage is
        our charactor use skill, and trigger element reaction, +1 DMG.
        """
        # first +1 DMG
        super().value_modifier_DAMAGE_INCREASE(value, match, mode)

        # second element reaction +1 DMG
        if self.usage == 0:
            # no usage left
            return value
        if self.position.area != ObjectPositionType.CHARACTOR:
            # not equipped
            return value
        if value.element_reaction == ElementalReactionType.NONE:
            # no elemental reaction
            return value
        if value.damage_from_element_reaction:
            # from elemental reaction
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
            target_area = ObjectPositionType.SKILL
        ):
            # not self player use skill
            return value
        # modify damage
        assert mode == 'REAL'
        value.damage += 1
        self.usage -= 1
        return value


register_class(AThousandFloatingDreams_3_7)
