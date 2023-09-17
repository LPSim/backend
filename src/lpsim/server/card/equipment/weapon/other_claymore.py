

from typing import Any, List, Literal

from ....modifiable_values import DamageIncreaseValue

from ....action import CreateObjectAction

from ....event import SkillEndEventArguments

from .base import RoundEffectWeaponBase, WeaponBase

from ....struct import Cost, ObjectPosition

from ....consts import CostLabels, ObjectPositionType, ObjectType, WeaponType


class WolfsGravestone(WeaponBase):
    name: Literal["Wolf's Gravestone"] = "Wolf's Gravestone"
    desc: str = (
        "The character deals +1 DMG. Deal +2 additional DMG if the target's "
        'remaining HP is equal or less than 6.'
    )
    cost: Cost = Cost(same_dice_number = 3)
    version: Literal['3.3'] = '3.3'
    weapon_type: WeaponType = WeaponType.CLAYMORE

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        assert value.target_position.area == ObjectPositionType.CHARACTOR
        charactor = match.get_object(value.target_position)
        if charactor.hp <= 6:
            self.damage_increase = 3
        super().value_modifier_DAMAGE_INCREASE(value, match, mode)
        self.damage_increase = 1
        return value


class TheBell(RoundEffectWeaponBase):
    name: Literal['The Bell']
    desc: str = (
        'The character deals +1 DMG. '
        'After the character uses a skill: Gives 1 Shield point to your '
        'active character. (Once per Round, stacks up to 2 points)'
    )
    type: Literal[ObjectType.WEAPON] = ObjectType.WEAPON
    version: Literal['3.7'] = '3.7'
    cost_label: int = CostLabels.CARD.value | CostLabels.WEAPON.value
    weapon_type: WeaponType = WeaponType.CLAYMORE

    cost: Cost = Cost(same_dice_number = 3)
    max_usage_per_round: int = 1

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If self charactor use any skill, and have usage, create Rebellious
        Shield.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, target_area = ObjectPositionType.SKILL
        ):
            # not self charactor use skill
            return []
        if self.usage == 0:
            # no usage
            return []
        self.usage -= 1
        return [CreateObjectAction(
            object_name = 'Rebellious Shield',
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1
            ),
            object_arguments = {}
        )]


Claymores = WolfsGravestone | TheBell
