from typing import Any, List, Literal

from .....utils.class_registry import register_class

from ....modifiable_values import DamageValue

from ....action import MakeDamageAction

from ....event import SkillEndEventArguments

from ....consts import (
    DamageElementalType, DamageType, ObjectPositionType, WeaponType
)

from ....struct import Cost
from .base import RoundEffectWeaponBase


class AquilaFavonia_3_3(RoundEffectWeaponBase):
    name: Literal['Aquila Favonia']
    cost: Cost = Cost(same_dice_number = 3)
    version: Literal['3.3'] = '3.3'
    weapon_type: WeaponType = WeaponType.SWORD
    max_usage_per_round: int = 2

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If self is active and opposite use skill and has usage, heal 1 HP
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = False,
            source_area = ObjectPositionType.CHARACTOR,
            target_area = ObjectPositionType.SKILL
        ):
            # not equipped or not opponent use skill
            return []
        if (
            self.position.charactor_idx != match.player_tables[
                self.position.player_idx].active_charactor_idx
        ):
            # not active
            return []
        if self.usage == 0:
            # no usage
            return []
        self.usage -= 1
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        return [MakeDamageAction(
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = charactor.position,
                    damage = -1,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = self.cost.copy()
                )
            ],
        )]


register_class(AquilaFavonia_3_3)
