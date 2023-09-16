from typing import Any, List, Literal

from ....modifiable_values import DamageValue

from ....action import MakeDamageAction

from ....event import SkillEndEventArguments

from ....consts import (
    DamageElementalType, DamageType, ObjectPositionType, WeaponType
)

from ....struct import Cost
from .base import RoundEffectWeaponBase


class AquilaFavonia(RoundEffectWeaponBase):
    name: Literal['Aquila Favonia']
    desc: str = (
        'The character deals +1 DMG. After the opposing character uses a '
        'Skill: If the character with this attached is the active character, '
        'heal this character for 1 HP. (Max twice per Round) '
    )
    cost: Cost = Cost(same_dice_number = 3)
    version: Literal['3.3'] = '3.3'
    weapon_type: WeaponType = WeaponType.SWORD
    max_usage_per_round: int = 2

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        If self use elemental skill, create one corresponding dice
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = False,
            source_area = ObjectPositionType.CHARACTOR,
            target_area = ObjectPositionType.SKILL
        ):
            # not equipped or not opponent use skill
            return []
        if self.usage == 0:
            # no usage
            return []
        self.usage -= 1
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        return [MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
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


Swords = AquilaFavonia | AquilaFavonia
