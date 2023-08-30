from typing import Literal, Any
from ..object_base import CardBase
from ..consts import (
    ObjectType, DamageElementalType, DamageType
)
from ..event import (
    RoundEndEventArguments,
    ChangeObjectUsageEventArguments,
)
from ..action import (
    MakeDamageAction, RemoveObjectAction
)
from ..modifiable_values import DamageDecreaseValue, DamageValue
from ..struct import Cost


class SummonBase(CardBase):
    type: Literal[ObjectType.SUMMON] = ObjectType.SUMMON
    renew_type: Literal['ADD', 'RESET', 'RESET_WITH_MAX'] = 'RESET_WITH_MAX'
    name: str
    usage: int
    max_usage: int
    cost: Cost = Cost()

    def renew(self, new_status: 'SummonBase') -> None:
        """
        Renew the status. 
        """
        if self.renew_type == 'ADD':
            self.usage += new_status.usage
            if self.max_usage < self.usage:
                self.usage = self.max_usage
        elif self.renew_type == 'RESET':
            raise NotImplementedError('RESET is not supported')
            self.usage = new_status.usage
        else:
            assert self.renew_type == 'RESET_WITH_MAX'
            self.usage = max(self.usage, new_status.usage)

    def is_valid(self, match: Any) -> bool:
        """
        For summons, it is expected to never be used as card.
        """
        raise AssertionError('SummonBase is not expected to be used as card')


class AttackerSummonBase(SummonBase):
    """
    Attacker summons, e.g. Guoba, Oz. They do attack on round end, and 
    disappears when run out of usage.
    """
    damage_elemental_type: DamageElementalType
    damage: int

    def event_handler_ROUND_END(self, event: RoundEndEventArguments) \
            -> list[MakeDamageAction]:
        """
        When round end, make damage to the opponent.
        """
        player_idx = self.position.player_idx
        assert self.usage > 0
        self.usage -= 1
        return [
            MakeDamageAction(
                player_idx = player_idx,
                target_idx = 1 - player_idx,
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
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
            )
        ]

    def event_handler_CHANGE_OBJECT_USAGE(
            self, event: ChangeObjectUsageEventArguments) \
            -> list[RemoveObjectAction]:
        """
        When usage is 0, remove the summon.
        """
        if self.usage <= 0:
            raise AssertionError('Not tested part')
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


class ShieldSummonBase(SummonBase):
    """
    Temporary shield summons, e.g. Ushi, Frog, Baron Bunny. They gives shield 
    which can decrease damage, and will do one-time damage in round end.

    Args:
        damage_elemental_type: The elemental type when attack.
        damage: The damage when attack.
        usage: The usage of the shield, which is shown on top right when it is
            summoned.
        max_usage: The maximum usage of the shield.
        min_damage_to_trigger: The minimum damage to trigger the damage 
            decrease.
        max_in_one_time: the maximum damage decrease in one time.
        decrease_usage_type: The type of decrease usage. 'ONE' means decrease
            one usage when damage decreased, regardless of how many. 
            'DAMAGE' means decrease usage by the damage decreased. Currently
            only 'ONE' is supported.
        attack_until_run_out_of_usage: Whether attack until run out of usage.
            If true, when usage is not zero, it will remain on the summon area
            and do nothing in round end. If false, when usage is not zero, it
            will do damage in round end and disappear.
    """
    damage_elemental_type: DamageElementalType
    damage: int
    usage: int
    max_usage: int
    min_damage_to_trigger: int
    max_in_one_time: int
    decrease_usage_type: Literal['ONE', 'DAMAGE']
    attack_until_run_out_of_usage: bool

    def event_handler_ROUND_END(self, event: RoundEndEventArguments) \
            -> list[MakeDamageAction | RemoveObjectAction]:
        """
        When round end, make damage to the opponent if is needed and remove
        itself.
        """
        player_idx = self.position.player_idx
        if self.usage > 0 and self.attack_until_run_out_of_usage:
            # attack until run out of usage
            raise AssertionError('Not tested part')
            return []
        return [
            MakeDamageAction(
                player_idx = player_idx,
                target_idx = 1 - player_idx,
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
                        damage = self.damage,
                        damage_elemental_type = self.damage_elemental_type,
                        charge_cost = 0,
                        target_player = 'ENEMY',
                        target_charactor = 'ACTIVE'
                    )
                ],
                charactor_change_rule = 'NONE',
            )
        ] + self._remove()

    def _remove(self) -> list[RemoveObjectAction]:
        """
        Remove the summon.
        """
        return [
            RemoveObjectAction(
                object_position = self.position,
            )
        ]

    def value_modifier_DAMAGE_DECREASE(
            self, value: DamageDecreaseValue,
            mode: Literal['TEST', 'REAL']) -> DamageDecreaseValue:
        """
        Decrease damage.
        """
        if value.target_position.player_idx != self.position.player_idx:
            # attack enemy, not activate
            return value
        if self.usage > 0:
            if value.damage < self.min_damage_to_trigger:
                raise NotImplementedError('Not tested part')
                # damage too small to trigger
                return value
            if self.decrease_usage_type != 'ONE':
                raise NotImplementedError('Only ONE is supported')
            decrease = min(self.max_in_one_time, value.damage)
            value.damage -= decrease
            assert mode == 'REAL'
            self.usage -= 1
        return value
