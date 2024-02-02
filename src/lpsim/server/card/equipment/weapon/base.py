from typing import Literal, List, Any

from .....utils.class_registry import register_base_class

from ....modifiable_values import DamageIncreaseValue

from ....event import MoveObjectEventArguments, RoundPrepareEventArguments

from ....struct import ObjectPosition, Cost

from ....action import Actions, MoveObjectAction, RemoveObjectAction

from ....consts import (
    CostLabels,
    DamageElementalType,
    ObjectPositionType,
    ObjectType,
    WeaponType,
)
from ....object_base import CardBase


class WeaponBase(CardBase):
    """
    Base class of weapons.
    """

    name: str
    cost: Cost
    version: str
    weapon_type: WeaponType
    type: Literal[ObjectType.WEAPON] = ObjectType.WEAPON
    cost_label: int = (
        CostLabels.CARD.value | CostLabels.WEAPON.value | CostLabels.EQUIPMENT.value
    )

    damage_increase: int = 1  # Almost all weapons increase the damage by 1
    remove_when_used: bool = False

    def equip(self, match: Any) -> List[Actions]:
        """
        The weapon is equipped, i.e. from hand to character. Set the status
        of weapon, and if it has actions when equipped, return the actions.
        """
        return []

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # can quip on self alive characters that have same weapon type
        ret: List[ObjectPosition] = []
        for character in match.player_tables[self.position.player_idx].characters:
            if character.is_alive and character.weapon_type == self.weapon_type:
                ret.append(character.position)
        return ret

    def is_valid(self, match: Any) -> bool:
        # can only be used when in hand
        targets = self.get_targets(match)
        return self.position.area == ObjectPositionType.HAND and len(targets) != 0

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[MoveObjectAction | RemoveObjectAction]:
        """
        Act the weapon. will place it into weapon area.
        When other weapon is equipped, remove the old one.
        """
        assert target is not None
        ret: List[MoveObjectAction | RemoveObjectAction] = []
        position = target.set_id(self.id)
        character_id = target.id
        assert position.area == ObjectPositionType.CHARACTER
        assert position.player_idx == self.position.player_idx
        characters = match.player_tables[position.player_idx].characters
        for character in characters:
            if character.id == character_id:
                # check if need to remove current weapon
                if character.weapon is not None:
                    ret.append(
                        RemoveObjectAction(
                            object_position=character.weapon.position,
                        )
                    )
        ret.append(
            MoveObjectAction(
                object_position=self.position,
                target_position=position,
            )
        )
        return ret

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Any
    ) -> List[Actions]:
        """
        When this weapon is moved from hand to character, it is considered
        as equipped, and will call `self.equip`.
        """
        if (
            event.action.object_position.id == self.id
            and event.action.object_position.area == ObjectPositionType.HAND
            and event.action.target_position.area == ObjectPositionType.CHARACTER
        ):
            # this weapon equipped from hand to character
            return self.equip(match)
        return []

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any, mode: Literal["TEST", "REAL"]
    ) -> DamageIncreaseValue:
        """
        When equipped character is using skill, increase the damage.
        """
        if self.position.area != ObjectPositionType.CHARACTER:
            # not equipped
            return value
        if not value.is_corresponding_character_use_damage_skill(
            self.position, match, None
        ):
            # not current character using skill
            return value
        if value.damage_elemental_type == DamageElementalType.PIERCING:
            # piercing damage
            return value
        # modify damage
        value.damage += self.damage_increase
        return value


register_base_class(WeaponBase)


class RoundEffectWeaponBase(WeaponBase):
    """
    Weapons that has round effects. Refresh their usage when equipped and
    at round preparing stage.
    Instead of setting usage, set max_usage_per_round.
    """

    name: str
    cost: Cost
    version: str
    weapon_type: WeaponType
    max_usage_per_round: int

    usage: int = 0

    def equip(self, match: Any) -> List[Actions]:
        self.usage = self.max_usage_per_round
        return []

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.usage = self.max_usage_per_round
        return []

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Any
    ) -> List[Actions]:
        """
        When this weapon is moved from character to character, and mark as
        reset_usage, reset usage.
        """
        if (
            event.action.object_position.id == self.id
            and event.action.object_position.area == ObjectPositionType.CHARACTER
            and event.action.target_position.area == ObjectPositionType.CHARACTER
            and event.action.reset_usage
        ):
            # this weapon equipped from character to character
            self.usage = self.max_usage_per_round
        return super().event_handler_MOVE_OBJECT(event, match)
