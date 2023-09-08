from typing import List, Literal, Any
from ..object_base import CardBase
from ..consts import (
    ELEMENT_TO_DAMAGE_TYPE, ElementType, ElementalReactionType, 
    ObjectPositionType, ObjectType, DamageElementalType, DamageType
)
from ..event import (
    MakeDamageEventArguments,
    ReceiveDamageEventArguments,
    RoundEndEventArguments,
    ChangeObjectUsageEventArguments,
)
from ..action import (
    Actions, MakeDamageAction, RemoveObjectAction
)
from ..modifiable_values import DamageDecreaseValue, DamageValue
from ..struct import Cost


class SummonBase(CardBase):
    type: Literal[ObjectType.SUMMON] = ObjectType.SUMMON
    renew_type: Literal['ADD', 'RESET', 'RESET_WITH_MAX'] = 'RESET_WITH_MAX'
    name: str
    desc: str
    version: str
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
    disappears when run out of usage. Specially, Melody Loop can also be a
    Attacker Summon, as it also makes damage with type HEAL.
    """
    name: str
    desc: str = '''End Phase: Deal _DAMAGE_ _ELEMENT_ DMG.'''
    version: str
    usage: int
    max_usage: int
    damage_elemental_type: DamageElementalType
    damage: int

    def __init__(self, *argv, **kwargs) -> None:
        super().__init__(*argv, **kwargs)
        self.desc = self.desc.replace(
            '_DAMAGE_', str(self.damage)
        ).replace(
            '_ELEMENT_', self.damage_elemental_type.name.capitalize()
        )

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        When round end, make damage to the opponent.
        """
        player_idx = self.position.player_idx
        assert self.usage > 0
        self.usage -= 1
        target_table = match.player_tables[1 - player_idx]
        target_charactor = target_table.get_active_charactor()
        return [
            MakeDamageAction(
                source_player_idx = player_idx,
                target_player_idx = 1 - player_idx,
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
                        target_position = target_charactor.position,
                        damage = self.damage,
                        damage_elemental_type = self.damage_elemental_type,
                        cost = self.cost.copy(),
                    )
                ],
            )
        ]

    def _remove(self) -> List[RemoveObjectAction]:
        """
        Remove the summon.
        """
        return [
            RemoveObjectAction(
                object_position = self.position,
            )
        ]

    def event_handler_CHANGE_OBJECT_USAGE(
            self, event: ChangeObjectUsageEventArguments, match: Any) \
            -> List[RemoveObjectAction]:
        """
        When usage is 0, remove the summon.
        """
        if self.usage <= 0:
            return self._remove()
        return []

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When usage is 0, remove the summon.
        """
        if self.usage <= 0:
            return self._remove()
        return []


class DefendSummonBase(SummonBase):
    """
    Defend summons, e.g. Ushi, Frog, Baron Bunny. decrease damage with its rule
    when receive damage, and decrease usage by 1, and will do one-time damage 
    in round end.

    Args:
        name: The name of the summon.
        desc: The description of the summon.
        usage: The usage of the summon, which is shown on top right when it is
            summoned, represents the number of times it can decrease damage.
        max_usage: The maximum usage of the summon.
        damage_elemental_type: The elemental type when attack.
        damage: The damage when attack.
        attack_until_run_out_of_usage: Whether attack until run out of usage.
            If true, when usage is not zero, it will remain on the summon area
            and do nothing in round end. If false, when usage is not zero, it
            will do damage in round end and disappear.
        min_damage_to_trigger: The minimum damage to trigger the damage 
            decrease.
        max_in_one_time: the maximum damage decrease in one time.
        decrease_usage_by_damage: Always be false for defend summons.
    """
    name: str
    desc: str
    version: str
    usage: int
    max_usage: int

    # attack params
    damage_elemental_type: DamageElementalType
    damage: int

    # defend params
    attack_until_run_out_of_usage: bool
    min_damage_to_trigger: int
    max_in_one_time: int
    decrease_usage_by_damage: bool = False

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        When round end, make damage to the opponent if is needed and remove
        itself.
        """
        player_idx = self.position.player_idx
        if self.usage > 0 and self.attack_until_run_out_of_usage:
            # attack until run out of usage
            return []
        target_table = match.player_tables[1 - player_idx]
        target_charactor = target_table.get_active_charactor()
        return [
            MakeDamageAction(
                source_player_idx = player_idx,
                target_player_idx = 1 - player_idx,
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
                        target_position = target_charactor.position,
                        damage = self.damage,
                        damage_elemental_type = self.damage_elemental_type,
                        cost = self.cost.copy(),
                    )
                ],
            )
        ] + self._remove()

    def _remove(self) -> List[RemoveObjectAction]:
        """
        Remove the summon.
        """
        return [
            RemoveObjectAction(
                object_position = self.position,
            )
        ]

    def value_modifier_DAMAGE_DECREASE(
            self, value: DamageDecreaseValue, match: Any,
            mode: Literal['TEST', 'REAL']) -> DamageDecreaseValue:
        """
        Decrease damage with its rule, and decrease usage.
        """
        if not value.is_corresponding_charactor_receive_damage(
            self.position, match,
        ):
            # not this charactor receive damage, not modify
            return value
        new_usage = value.apply_shield(
            self.usage, self.min_damage_to_trigger, self.max_in_one_time,
            self.decrease_usage_by_damage
        )
        assert mode == 'REAL'
        self.usage = new_usage
        return value


class ShieldSummonBase(DefendSummonBase):
    """
    Shield summons, which decrease damage like yellow shield, decrease damage 
    by its usage and decrease corresponding usage. Currently no such summon.

    Args:
        name: The name of the summon.
        desc: The description of the summon.
        usage: The usage of the summon, which is shown on top right when it is
            summoned, represents the number of times it can decrease damage.
        max_usage: The maximum usage of the summon.
        damage_elemental_type: The elemental type when attack.
        damage: The damage when attack.
        attack_until_run_out_of_usage: Whether attack until run out of usage.
            If true, when usage is not zero, it will remain on the summon area
            and do nothing in round end. If false, when usage is not zero, it
            will do damage in round end and disappear.

        decrease_usage_by_damage: Always be true for shield summons.
        min_damage_to_trigger: Not used, always be 0 for shield summons.
        max_in_one_time: Not used, always be 0 for shield summons.
    """
    name: str
    desc: str
    version: str
    usage: int
    max_usage: int
    damage_elemental_type: DamageElementalType
    damage: int
    attack_until_run_out_of_usage: bool

    # papams passing to apply_shield is fixed
    min_damage_to_trigger: int = 0
    max_in_one_time: int = 0
    decrease_usage_by_damage: bool = True


class SwirlChangeSummonBase(AttackerSummonBase):
    """
    Base class for summons that can change damage elemental type when swirl
    reaction made by our charactor or summon. 
    Note: create summon before attack, so it can change element immediately.
    """
    name: str
    desc: str = (
        'After your character or Summon triggers a Swirl reaction: Convert '
        'the Elemental Type of this card and change its DMG dealt to the '
        'element Swirled. (Can only be converted once before leaving the '
        'field)'
    )
    version: str
    usage: int
    max_usage: int

    damage_elemental_type: DamageElementalType = DamageElementalType.ANEMO

    def renew(self, new_status: SummonBase) -> None:
        """
        When renew, also renew damage elemental type.
        """
        super().renew(new_status)
        self.damage_elemental_type = DamageElementalType.ANEMO

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        When anyone receives damage, and has swirl reaction, and made by
        our charactor or summon, and current damage type is anemo, 
        change stormeye damage element.
        """
        if self.damage_elemental_type != DamageElementalType.ANEMO:
            # already changed, do nothing
            return []
        if event.final_damage.position.area not in [
            ObjectPositionType.SKILL, ObjectPositionType.SUMMON
        ]:  # pragma: no cover
            # not charactor or summon made damage, do nothing
            return []
        if event.final_damage.position.player_idx != self.position.player_idx:
            # not our player made damage, do nothing
            return []
        if event.final_damage.element_reaction != ElementalReactionType.SWIRL:
            # not swirl reaction, do nothing
            return []
        elements = event.final_damage.reacted_elements
        assert elements[0] == ElementType.ANEMO, 'First element must be anemo'
        # do type change
        self.damage_elemental_type = ELEMENT_TO_DAMAGE_TYPE[elements[1]]
        return []
