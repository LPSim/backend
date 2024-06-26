from typing import List, Literal, Any
from pydantic import validator

from ...utils import accept_same_or_higher_version
from ...utils.class_registry import register_base_class
from ..object_base import ObjectBase
from ..consts import (
    ELEMENT_TO_DAMAGE_TYPE,
    ElementType,
    ElementalReactionType,
    IconType,
    ObjectPositionType,
    ObjectType,
    DamageElementalType,
    DamageType,
)
from ..event import (
    CreateObjectEventArguments,
    DeclareRoundEndEventArguments,
    MakeDamageEventArguments,
    ReceiveDamageEventArguments,
    RoundEndEventArguments,
    ChangeObjectUsageEventArguments,
    RoundPrepareEventArguments,
)
from ..action import (
    ActionTypes,
    Actions,
    ChangeObjectUsageAction,
    CreateObjectAction,
    MakeDamageAction,
    RemoveObjectAction,
)
from ..modifiable_values import DamageDecreaseValue, DamageValue
from ..struct import Cost, ObjectPosition


class SummonBase(ObjectBase):
    type: Literal[ObjectType.SUMMON] = ObjectType.SUMMON
    renew_type: Literal["ADD", "RESET", "RESET_WITH_MAX"] = "RESET_WITH_MAX"
    name: str
    strict_version_validation: bool = False  # default accept higher versions
    version: str
    usage: int
    max_usage: int
    damage_elemental_type: DamageElementalType
    damage: int

    # icon type is used to show the icon on the summon top right.
    icon_type: Literal[
        IconType.SHIELD, IconType.BARRIER, IconType.TIMESTATE, IconType.COUNTER
    ]
    # when status icon type is not none, it will show in team status area
    status_icon_type: Literal[IconType.NONE] = IconType.NONE

    @validator("version", pre=True)
    def accept_same_or_higher_version(cls, v: str, values):
        return accept_same_or_higher_version(cls, v, values)

    def renew(self, new_status: "SummonBase") -> None:
        """
        Renew the status.
        """
        if self.renew_type == "ADD":
            self.usage += new_status.usage
            if self.max_usage < self.usage:
                self.usage = self.max_usage
        elif self.renew_type == "RESET":
            raise NotImplementedError("RESET is not supported")
            self.usage = new_status.usage
        else:
            assert self.renew_type == "RESET_WITH_MAX"
            self.usage = max(self.usage, new_status.usage)
        self.desc = new_status.desc

    def is_valid(self, match: Any) -> bool:
        """
        For summons, it is expected to never be used as card.
        """
        raise AssertionError("SummonBase is not expected to be used as card")


register_base_class(SummonBase)


class AttackerSummonBase(SummonBase):
    """
    Attacker summons, e.g. Guoba, Oz. They do attack on round end, and
    disappears when run out of usage. Specially, Melody Loop can also be a
    Attacker Summon, as it also makes damage with type HEAL.
    """

    name: str
    version: str
    usage: int
    max_usage: int
    damage_elemental_type: DamageElementalType
    damage: int

    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        """
        When round end, make damage to the opponent, and decrease self usage.
        """
        player_idx = self.position.player_idx
        assert self.usage > 0
        damage_type = DamageType.DAMAGE
        target_table = match.player_tables[1 - player_idx]
        if self.damage_elemental_type == DamageElementalType.HEAL:
            damage_type = DamageType.HEAL
            target_table = match.player_tables[player_idx]
        target_character = target_table.get_active_character()
        return [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        damage_type=damage_type,
                        target_position=target_character.position,
                        damage=self.damage,
                        damage_elemental_type=self.damage_elemental_type,
                        cost=Cost(),
                    )
                ],
            ),
            ChangeObjectUsageAction(object_position=self.position, change_usage=-1),
        ]

    def _remove(self, match: Any) -> List[RemoveObjectAction]:
        """
        Remove the summon.
        """
        return [
            RemoveObjectAction(
                object_position=self.position,
            )
        ]

    def event_handler_CHANGE_OBJECT_USAGE(
        self, event: ChangeObjectUsageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When usage is 0, remove the summon.
        """
        if self.usage <= 0:
            return self._remove(match)
        return []

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When usage is 0, remove the summon.
        """
        if self.usage <= 0:
            return self._remove(match)
        return []


class AOESummonBase(AttackerSummonBase):
    """
    Base class that deals AOE damage. It will attack active character
    damage+element, back character back_damage_piercing.
    """

    back_damage: int

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        ret = super().event_handler_ROUND_END(event, match)
        damage_action = ret[0]
        assert damage_action.type == ActionTypes.MAKE_DAMAGE
        target_table = match.player_tables[1 - self.position.player_idx]
        characters = target_table.characters
        for cid, character in enumerate(characters):
            if cid == target_table.active_character_idx:
                continue
            if character.is_defeated:
                continue
            damage_action.damage_value_list.append(
                DamageValue(
                    position=self.position,
                    damage_type=DamageType.DAMAGE,
                    target_position=character.position,
                    damage=self.back_damage,
                    damage_elemental_type=DamageElementalType.PIERCING,
                    cost=Cost(),
                )
            )
        return ret


class DeclareRoundEndAttackSummonBase(AttackerSummonBase):
    """
    Summons that will attack when declare round end, e.g. Sesshou Sakura.
    """

    extra_attack_usage: int

    def event_handler_DECLARE_ROUND_END(
        self, event: DeclareRoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction | ChangeObjectUsageAction]:
        """
        if usage larger than expected, return event_handler_ROUND_END
        """
        if event.action.player_idx != self.position.player_idx:
            # not our player, do nothing
            return []
        if self.usage < self.extra_attack_usage:
            # not enough usage, do nothing
            return []
        # as attack not use event, use fake event instead.
        fake_event: Any = None
        # make damage
        return self.event_handler_ROUND_END(fake_event, match)


class DefendSummonBase(SummonBase):
    """
    Defend summons, e.g. Ushi, Frog, Baron Bunny. decrease damage with its rule
    when receive damage, and decrease usage by 1, and will do one-time damage
    in round end.

    Args:
        name: The name of the summon.
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

    icon_type: Literal[IconType.BARRIER] = IconType.BARRIER

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
        target_character = target_table.get_active_character()
        return [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        damage_type=DamageType.DAMAGE,
                        target_position=target_character.position,
                        damage=self.damage,
                        damage_elemental_type=self.damage_elemental_type,
                        cost=Cost(),
                    )
                ],
            )
        ] + self._remove(match)

    def _remove(self, match: Any) -> List[RemoveObjectAction]:
        """
        Remove the summon.
        """
        return [
            RemoveObjectAction(
                object_position=self.position,
            )
        ]

    def value_modifier_DAMAGE_DECREASE(
        self, value: DamageDecreaseValue, match: Any, mode: Literal["TEST", "REAL"]
    ) -> DamageDecreaseValue:
        """
        Decrease damage with its rule, and decrease usage.
        """
        if not value.is_corresponding_character_receive_damage(
            self.position,
            match,
        ):
            # not this character receive damage, not modify
            return value
        new_usage = value.apply_shield(
            self.usage,
            self.min_damage_to_trigger,
            self.max_in_one_time,
            self.decrease_usage_by_damage,
        )
        assert mode == "REAL"
        self.usage = new_usage
        return value


class ShieldSummonBase(DefendSummonBase):
    """
    Shield summons, which decrease damage like yellow shield, decrease damage
    by its usage and decrease corresponding usage. Currently no such summon.

    Args:
        name: The name of the summon.
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
    version: str
    usage: int
    max_usage: int
    damage_elemental_type: DamageElementalType
    damage: int
    attack_until_run_out_of_usage: bool

    icon_type: Literal[IconType.SHIELD] = IconType.SHIELD

    # papams passing to apply_shield is fixed
    min_damage_to_trigger: int = 0
    max_in_one_time: int = 0
    decrease_usage_by_damage: bool = True


class SwirlChangeSummonBase(AttackerSummonBase):
    """
    Base class for summons that can change damage elemental type when swirl
    reaction made by our character or summon.
    Note: create summon before attack, so it can change element immediately.
    """

    name: str
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
        our character or summon, and current damage type is anemo,
        change stormeye damage element.
        """
        if self.damage_elemental_type != DamageElementalType.ANEMO:
            # already changed, do nothing
            return []
        if event.final_damage.position.area not in [
            ObjectPositionType.SKILL,
            ObjectPositionType.SUMMON,
        ]:  # pragma: no cover
            # not character or summon made damage, do nothing
            return []
        if event.final_damage.position.player_idx != self.position.player_idx:
            # not our player made damage, do nothing
            return []
        if event.final_damage.element_reaction != ElementalReactionType.SWIRL:
            # not swirl reaction, do nothing
            return []
        elements = event.final_damage.reacted_elements
        assert elements[0] == ElementType.ANEMO, "First element must be anemo"
        # do type change
        self.damage_elemental_type = ELEMENT_TO_DAMAGE_TYPE[elements[1]]
        return []


class AttackAndGenerateStatusSummonBase(AttackerSummonBase):
    """
    Summons that will attack opposite, and generate status to self periodly,
    usually defend status. e.g. Dehya, Lynette. When the summon is removed,
    it will also try to remove the status.
    """

    name: str
    version: str
    usage: int
    max_usage: int
    damage_elemental_type: DamageElementalType
    damage: int
    status_name: str | None = None

    def _create_status(self, match: Any) -> List[CreateObjectAction]:
        """
        Create status
        """
        if self.status_name is not None:  # pragma: no cover
            name = self.status_name
        else:
            name = self.name
        return [
            CreateObjectAction(
                object_name=name,
                object_position=ObjectPosition(
                    player_idx=self.position.player_idx,
                    area=ObjectPositionType.TEAM_STATUS,
                    id=0,
                ),
                object_arguments={},
            )
        ]

    def event_handler_CREATE_OBJECT(
        self, event: CreateObjectEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When created object is self, and not renew, also create teams status
        """
        if event.create_result != "NEW":
            # not new, do nothing
            return []
        if event.action.object_name == self.name and self.position.check_position_valid(
            event.action.object_position, match, player_idx_same=True, area_same=True
        ):
            # name same, and position same, is self created
            return self._create_status(match)
        return []

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        # re-generate status
        return self._create_status(match)

    def _remove(self, match: Any) -> List[RemoveObjectAction]:
        """
        If self should remove, and has generated status, remove together.
        """
        status = match.player_tables[self.position.player_idx].team_status
        target_status = None
        for s in status:
            if s.name == self.name:
                target_status = s
                break
        ret: List[RemoveObjectAction] = [
            RemoveObjectAction(
                object_position=self.position,
            )
        ]
        if target_status is not None:
            ret.append(RemoveObjectAction(object_position=target_status.position))
        return ret
