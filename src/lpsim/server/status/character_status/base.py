from typing import Any, Literal, List

from ....utils.class_registry import register_base_class

from ...struct import Cost

from ...modifiable_values import (
    DamageDecreaseValue,
    DamageElementEnhanceValue,
    DamageValue,
)
from ...consts import (
    ELEMENT_TO_ENCHANT_ICON,
    DamageElementalType,
    DamageType,
    ElementType,
    IconType,
    ObjectType,
    PlayerActionLabels,
)
from ..base import StatusBase
from ...action import (
    MakeDamageAction,
    RemoveObjectAction,
    Actions,
    SkipPlayerActionAction,
    UseSkillAction,
)
from ...event import (
    ChooseCharacterEventArguments,
    MakeDamageEventArguments,
    PlayerActionStartEventArguments,
    RoundEndEventArguments,
    RoundPrepareEventArguments,
    SwitchCharacterEventArguments,
    UseSkillEventArguments,
)


class CharacterStatusBase(StatusBase):
    """
    Base class of character status.
    """

    type: Literal[ObjectType.CHARACTER_STATUS] = ObjectType.CHARACTER_STATUS
    name: str
    version: str
    usage: int
    max_usage: int


register_base_class(CharacterStatusBase)


class UsageCharacterStatus(CharacterStatusBase):
    """
    Base class of team status that based on usages.
    It will implement a method to check if run out of usage; when run out
    of usage, it will remove itself.

    By default, it listens to MAKE_DAMAGE event to check if run out of usage,
    as most usage-based status will decrease usage when damage made.
    Not using AFTER_MAKE_DAMAGE because we should remove the status before
    side effects of elemental reaction, which is triggered on RECEIVE_DAMAGE.

    If it is not a damage related status, check_should_remove should be
    called manually.
    """

    name: str
    version: str
    usage: int
    max_usage: int

    def check_should_remove(self) -> List[RemoveObjectAction]:
        """
        Check if the status should be removed.
        when usage has changed, call this function to check if the status
        should be removed.
        """
        if self.usage <= 0:
            return [
                RemoveObjectAction(
                    object_position=self.position,
                )
            ]
        return []

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When damage made, check whether the team status should be removed.
        """
        return self.check_should_remove()


class RoundCharacterStatus(CharacterStatusBase):
    """
    Base class of team status that based on rounds.  It will implement the
    event trigger on ROUND_PREPARE to check if run out of usages; when run out
    of usages, it will remove itself.
    """

    name: str
    version: str
    usage: int
    max_usage: int

    def check_should_remove(self) -> List[RemoveObjectAction]:
        """
        Check if the status should be removed.
        when round has changed, call this function to check if the status
        should be removed.
        """
        if self.usage <= 0:
            return [
                RemoveObjectAction(
                    object_position=self.position,
                )
            ]
        return []

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        """
        When reaching prepare, decrease usage and check whether the team
        status should be removed.
        """
        self.usage -= 1
        return list(self.check_should_remove())


class DefendCharacterStatus(UsageCharacterStatus):
    """
    Base class of defend status (purple shield), decrease damage with its rule
    when receive damage, and decrease usage by 1.
    """

    name: str
    version: str
    usage: int
    max_usage: int
    min_damage_to_trigger: int
    max_in_one_time: int
    decrease_usage_by_damage: bool = False

    icon_type: Literal[IconType.BARRIER] = IconType.BARRIER

    def value_modifier_DAMAGE_DECREASE(
        self, value: DamageDecreaseValue, match: Any, mode: Literal["TEST", "REAL"]
    ) -> DamageDecreaseValue:
        """
        Decrease damage with its rule, and decrease 1 usage.
        """
        if not value.is_corresponding_character_receive_damage(
            self.position,
            match,
        ):
            # not this character receive damage, not modify
            return value
        if self.usage <= 0:
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


class ShieldCharacterStatus(DefendCharacterStatus):
    """
    Base class of shield status (yellow shield), decrease damage by its usage
    and decrease corresponding usage.
    """

    name: str
    version: str
    usage: int
    max_usage: int

    icon_type: Literal[IconType.SHIELD] = IconType.SHIELD

    # papams passing to apply_shield is fixed
    min_damage_to_trigger: int = 0
    max_in_one_time: int = 0
    decrease_usage_by_damage: bool = True


class ElementalInfusionCharacterStatus(CharacterStatusBase):
    """
    Base class of doing elemental infusion. It will infuse all physical damage
    to corresponding elemental damage for this character. If there extra
    conditions, filter the condition and call value modifier in subclasses.
    """

    name: Literal[
        "Pyro Elemental Infusion",
        "Hydro Elemental Infusion",
        "Electro Elemental Infusion",
        "Cryo Elemental Infusion",
        "Anemo Elemental Infusion",
        "Geo Elemental Infusion",
        "Dendro Elemental Infusion",
    ]
    infused_elemental_type: DamageElementalType = DamageElementalType.PHYSICAL

    icon_type: Literal[
        IconType.ELEMENT_ENCHANT_ELEC,
        IconType.ELEMENT_ENCHANT_FIRE,
        IconType.ELEMENT_ENCHANT_WATER,
        IconType.ELEMENT_ENCHANT_ICE,
        IconType.ELEMENT_ENCHANT_WIND,
        IconType.ELEMENT_ENCHANT_ROCK,
        IconType.ELEMENT_ENCHANT_GRASS,
        IconType.ATK_UP,
    ] = IconType.ATK_UP

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.infused_elemental_type == DamageElementalType.PHYSICAL:
            # not set elemental type manually, get it from name
            element = self.name.split(" ")[0].upper()
            assert element in [
                "PYRO",
                "HYDRO",
                "ELECTRO",
                "CRYO",
                "ANEMO",
                "GEO",
                "DENDRO",
            ], "In ElementalInfusion: element not set right value"
            assert self.name.split(" ")[1:] == ["Elemental", "Infusion"]
            self.infused_elemental_type = DamageElementalType(element)
        if self.icon_type == IconType.ATK_UP:
            self.icon_type = ELEMENT_TO_ENCHANT_ICON[
                ElementType(self.infused_elemental_type.value)
            ]  # type: ignore

    def value_modifier_DAMAGE_ELEMENT_ENHANCE(
        self,
        value: DamageElementEnhanceValue,
        match: Any,
        mode: Literal["TEST", "REAL"],
    ) -> DamageElementEnhanceValue:
        """
        When self use skill, change physical to corresponding element.
        NOTE: this function will not change the usage.
        """
        assert mode == "REAL"
        if not value.is_corresponding_character_use_damage_skill(
            self.position, match, None
        ):
            # not corresponding character use skill, do nothing
            return value
        if self.usage <= 0:  # pragma: no cover
            # no usage, do nothing
            return value
        # change physical to other element
        if value.damage_elemental_type == DamageElementalType.PHYSICAL:
            value.damage_elemental_type = self.infused_elemental_type
        return value


class PrepareCharacterStatus(CharacterStatusBase):
    """
    Prepare status will trigger when self player action start, and try to
    use a specified skill, and skip next player action phase.
    if this character is stunned, it will do nothing.

    When this character is not active character, it will remove itself.
    """

    name: str
    version: str
    character_name: str
    skill_name: str

    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.SPECIAL] = IconType.SPECIAL

    done: bool = False

    def event_handler_SWITCH_CHARACTER(
        self, event: SwitchCharacterEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        If self switch character, after switch if this character is not active
        character, remove this status.
        """
        if event.action.player_idx != self.position.player_idx:
            # not self switch character
            return []
        return [
            RemoveObjectAction(
                object_position=self.position,
            )
        ]

    def event_handler_CHOOSE_CHARACTER(
        self, event: ChooseCharacterEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        As choose character only happens on character defeated, it is not
        possible.
        """
        if event.action.player_idx != self.position.player_idx:
            # not self choose character
            return []
        raise NotImplementedError("Should not be called")
        return [
            RemoveObjectAction(
                object_position=self.position,
            )
        ]

    def event_handler_PLAYER_ACTION_START(
        self, event: PlayerActionStartEventArguments, match: Any
    ) -> List[UseSkillAction]:
        """
        If self player action start, and this character is at front,
        use skill. it will also listen to Use Skill event to remove self, and skip
        player action.
        remove this status, and skip player action.
        """
        if event.player_idx != self.position.player_idx:
            # not self player action start, do nothing
            return []
        table = match.player_tables[self.position.player_idx]
        active_idx = table.active_character_idx
        if active_idx != self.position.character_idx:  # pragma: no cover
            # not active character, do nothing
            return []
        character = table.get_active_character()
        if character.is_stunned:
            # stunned, do nothing
            return []
        assert character.name == self.character_name
        for skill in character.skills:
            if skill.name == self.skill_name:
                self.done = True
                return [UseSkillAction(skill_position=skill.position)]
        else:
            raise AssertionError("Skill not found")

    def event_handler_USE_SKILL(
        self, event: UseSkillEventArguments, match: Any
    ) -> List[RemoveObjectAction | SkipPlayerActionAction]:
        """
        When use skill, and this status is marked as done, remove self and trigger
        skip player action.
        As it is a character status, it will always trigger after skill of character.
        """
        if self.done:
            return [
                # remove self
                RemoveObjectAction(object_position=self.position),
                # skip player action
                SkipPlayerActionAction(
                    action_label=PlayerActionLabels.SKILL,
                    do_combat_action=True,
                    position=event.action.skill_position,
                ),
            ]
        return []


class ReviveCharacterStatus(UsageCharacterStatus):
    name: str
    version: str
    heal: int

    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.REVIVE] = IconType.REVIVE

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[MakeDamageAction | RemoveObjectAction]:
        """
        when make damage, check whether this character's hp is 0. if so,
        heal it by self.heal hp.

        Using make damage action, so it will trigger immediately before
        receiving any other damage, and can be defeated by other damage.
        """
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        if character.hp > 0:
            # hp not 0, do nothing
            return []
        if self.usage <= 0:  # pragma: no cover
            # no usage, do nothing
            return []
        # heal this character by 1
        self.usage -= 1
        return [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        damage_type=DamageType.HEAL,
                        target_position=character.position,
                        damage=-self.heal,
                        damage_elemental_type=DamageElementalType.HEAL,
                        cost=Cost(),
                    )
                ],
            )
        ] + self.check_should_remove()


class RoundEndAttackCharacterStatus(UsageCharacterStatus):
    """
    Make damage to this character at round end. It can also be heal, e.g.
    Pizza.
    """

    name: str
    version: str
    usage: int
    max_usage: int
    icon_type: Literal[IconType.DOT] = IconType.DOT
    damage: int
    damage_elemental_type: DamageElementalType

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        assert self.usage > 0
        self.usage -= 1
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        damage_type = DamageType.DAMAGE
        if self.damage < 0:
            damage_type = DamageType.HEAL
        return [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        damage_type=damage_type,
                        target_position=character.position,
                        damage=self.damage,
                        damage_elemental_type=self.damage_elemental_type,
                        cost=Cost(),
                    )
                ]
            )
        ]
