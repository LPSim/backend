
from typing import Any, List, Literal

from .....utils.class_registry import register_class

from ....event import SkillEndEventArguments

from ....modifiable_values import DamageIncreaseValue

from ....action import CreateObjectAction

from ....consts import ObjectPositionType, SkillType, WeaponType

from ....struct import Cost, ObjectPosition
from .base import RoundEffectWeaponBase, WeaponBase


class AmosBow_3_7(RoundEffectWeaponBase):
    name: Literal["Amos' Bow"]
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


class ElegyForTheEnd_3_7(WeaponBase):
    name: Literal["Elegy for the End"]
    cost: Cost = Cost(same_dice_number = 3)
    version: Literal['3.7'] = '3.7'
    weapon_type: WeaponType = WeaponType.BOW

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If equipped and self use elemental burst, create a status
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, 
            source_area = ObjectPositionType.CHARACTOR
        ):
            # not equipped or not self use skill
            return []
        if event.action.skill_type != SkillType.ELEMENTAL_BURST:
            # not elemental burst
            return []
        return [CreateObjectAction(
            object_name = 'Millennial Movement: Farewell Song',
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = 0
            ),
            object_arguments = {}
        )]


register_class(AmosBow_3_7 | ElegyForTheEnd_3_7)
