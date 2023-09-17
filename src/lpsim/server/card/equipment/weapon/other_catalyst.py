from typing import Any, List, Literal
from ....action import DrawCardAction

from ....modifiable_values import DamageIncreaseValue

from ....struct import Cost

from ....consts import (
    CostLabels, ElementalReactionType, ObjectPositionType, ObjectType, 
    WeaponType
)
from .base import RoundEffectWeaponBase, WeaponBase


class AThousandFloatingDreams(RoundEffectWeaponBase):
    name: Literal['A Thousand Floating Dreams']
    desc: str = (
        'The character deals +1 DMG. '
        'When your character triggers an Elemental Reaction: Deal +1 DMG. '
        '(Twice per Round)'
    )
    type: Literal[ObjectType.WEAPON] = ObjectType.WEAPON
    version: Literal['3.7'] = '3.7'
    cost_label: int = CostLabels.CARD.value | CostLabels.WEAPON.value
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


class FruitOfFulfillment(WeaponBase):
    name: Literal['Fruit of Fulfillment']
    desc: str = '''The character deals +1 DMG. When played: Draw 2 cards.'''
    cost: Cost = Cost(any_dice_number = 3)
    version: Literal['3.8'] = '3.8'
    weapon_type: WeaponType = WeaponType.CATALYST

    def equip(self, match: Any) -> List[DrawCardAction]:
        """
        draw 2 cards
        """
        return [DrawCardAction(
            player_idx = self.position.player_idx,
            number = 2,
            draw_if_filtered_not_enough = True
        )]


Catalysts = AThousandFloatingDreams | FruitOfFulfillment
