from typing import Literal
from ..object_base import CardBase
from ..consts import (
    ObjectType, DamageElementalType, DamageSourceType, DamageType
)
from ..event import (
    RoundEndEventArguments,
    ChangeObjectUsageEventArguments,
)
from ..action import (
    MakeDamageAction, RemoveObjectAction
)
from ..modifiable_values import DamageValue
from ..struct import DiceCost


class SummonBase(CardBase):
    type: Literal[ObjectType.SUMMON] = ObjectType.SUMMON
    renew_type: Literal['ADD', 'RESET', 'RESET_WITH_MAX'] = 'RESET_WITH_MAX'
    name: str
    usage: int
    max_usage: int
    cost: DiceCost = DiceCost()

    def renew(self, new_status: 'SummonBase') -> None:
        """
        Renew the status. 
        """
        if self.renew_type == 'ADD':
            self.usage += new_status.usage
            if self.max_usage < self.usage:
                self.usage = self.max_usage
        elif self.renew_type == 'RESET':
            self.usage = new_status.usage
        elif self.renew_type == 'RESET_WITH_MAX':
            self.usage = max(self.usage, new_status.usage)


class AttackerSummonBase(SummonBase):

    damage_elemental_type: DamageElementalType
    damage: int

    def event_handler_ROUND_END(self, event: RoundEndEventArguments) \
            -> list[MakeDamageAction]:
        """
        When round end, make damage to the opponent.
        """
        player_id = self.position.player_id
        source_type = DamageSourceType.CURRENT_PLAYER_SUMMON
        assert self.usage > 0
        self.usage -= 1
        return [
            MakeDamageAction(
                player_id = player_id,
                target_id = 1 - player_id,
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        id = self.id,
                        damage_type = DamageType.DAMAGE,
                        damage_source_type = source_type,
                        damage = self.damage,
                        damage_elemental_type = self.damage_elemental_type,
                        charge_cost = 0,
                        target_player = 'ENEMY',
                        target_charactor = 'ACTIVE'
                    )
                ],
                charactor_change_rule = 'NONE',
            )
        ]

    def _remove(self) -> list[RemoveObjectAction]:
        """
        Remove the summon.
        """
        return [
            RemoveObjectAction(
                object_position = self.position,
                object_id = self.id,
            )
        ]

    def event_handler_CHANGE_OBJECT_USAGE(
            self, event: ChangeObjectUsageEventArguments) \
            -> list[RemoveObjectAction]:
        """
        When usage is 0, remove the summon.
        """
        if self.usage <= 0:
            return self._remove()
        return []

    def event_handler_MAKE_DAMAGE(self, event: MakeDamageAction) \
            -> list[RemoveObjectAction]:
        """
        When usage is 0, remove the summon.
        """
        if self.usage <= 0:
            return self._remove()
        return []
