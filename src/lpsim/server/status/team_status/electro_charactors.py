
from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...struct import Cost

from ...consts import DamageElementalType, DamageType, IconType, SkillType

from ...modifiable_values import DamageDecreaseValue, DamageValue

from ...action import MakeDamageAction

from ...event import PlayerActionStartEventArguments
from .base import ExtraAttackTeamStatus, RoundTeamStatus, UsageTeamStatus


class TenkoThunderbolts_3_7(UsageTeamStatus):
    name: Literal['Tenko Thunderbolts'] = 'Tenko Thunderbolts'
    version: Literal['3.7'] = '3.7'
    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    def event_handler_PLAYER_ACTION_START(
        self, event: PlayerActionStartEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        Attack opponent active charactor
        """
        if self.position.player_idx != event.player_idx:
            # not our turn
            return []
        target_table = match.player_tables[1 - self.position.player_idx]
        target_charactor_idx = target_table.active_charactor_idx
        target_charactor = target_table.charactors[target_charactor_idx]
        self.usage -= 1
        return [MakeDamageAction(
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = target_charactor.position,
                    damage = 3,
                    damage_elemental_type = DamageElementalType.ELECTRO,
                    cost = Cost()
                )
            ],
        )]


class ThunderbeastsTarge_3_4(RoundTeamStatus, ExtraAttackTeamStatus):
    name: Literal["Thunderbeast's Targe"] = "Thunderbeast's Targe"
    version: Literal['3.4'] = '3.4'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS

    trigger_skill_type: SkillType | None = SkillType.NORMAL_ATTACK
    damage: int = 1
    damage_elemental_type: DamageElementalType = DamageElementalType.ELECTRO
    decrease_usage: bool = False

    def value_modifier_DAMAGE_DECREASE(
        self, value: DamageDecreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageDecreaseValue:
        """
        If this charactor receives damage, and not piercing, and greater than
        3, decrease damage by 1
        """
        if (
            value.is_corresponding_charactor_receive_damage(
                self.position, match,
            ) 
            and value.damage >= 3
        ):
            value.damage -= 1
        return value


register_class(TenkoThunderbolts_3_7 | ThunderbeastsTarge_3_4)
