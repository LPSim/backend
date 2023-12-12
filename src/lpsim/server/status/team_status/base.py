from typing import Any, List, Literal

from ....utils.class_registry import register_base_class

from ...struct import Cost

from ...modifiable_values import (
    DamageDecreaseValue, DamageElementEnhanceValue, DamageValue
)
from ..base import StatusBase
from ...consts import (
    ELEMENT_TO_ENCHANT_ICON, DamageElementalType, DamageType, ElementType, 
    IconType, ObjectType, SkillType
)
from ...action import MakeDamageAction, RemoveObjectAction, Actions
from ...event import (
    ChooseCharactorEventArguments, MakeDamageEventArguments, 
    RoundPrepareEventArguments, SkillEndEventArguments, 
    SwitchCharactorEventArguments
)


class TeamStatusBase(StatusBase):
    """
    Base class of team status.
    """
    type: Literal[ObjectType.TEAM_STATUS] = ObjectType.TEAM_STATUS
    name: str
    version: str
    usage: int
    max_usage: int


register_base_class(TeamStatusBase)


class UsageTeamStatus(TeamStatusBase):
    """
    Base class of team status that based on usages.
    It will implement a method to check if run out of usage; when run out
    of usage, it will remove itself.

    By default, it listens to MAKE_DAMAGE event to check if run out of usage,
    as most usage-based status will decrease usage when damage made.
    Not using AFTER_MAKE_DAMAGE because we should remove the status before
    side effects of elemental reaction, which is triggered on RECEVIE_DAMAGE.

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
            return [RemoveObjectAction(
                object_position = self.position,
            )]
        return []

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When damage made, check whether the team status should be removed.
        """
        return self.check_should_remove()


class RoundTeamStatus(TeamStatusBase):
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
            return [RemoveObjectAction(
                object_position = self.position,
            )]
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


class DefendTeamStatus(UsageTeamStatus):
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
            self, value: DamageDecreaseValue, match: Any,
            mode: Literal['TEST', 'REAL']) -> DamageDecreaseValue:
        """
        Decrease damage with its rule, and decrease 1 usage.
        """
        if not value.is_corresponding_charactor_receive_damage(
            self.position, match,
        ):
            # not this charactor receive damage, not modify
            return value
        if self.usage <= 0:
            # no usage, not modify
            return value
        new_usage = value.apply_shield(
            self.usage, self.min_damage_to_trigger, 
            self.max_in_one_time, self.decrease_usage_by_damage,
        )
        assert mode == 'REAL'
        self.usage = new_usage
        return value


class ShieldTeamStatus(DefendTeamStatus):
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


class ExtraAttackTeamStatus(TeamStatusBase):
    name: str
    version: str

    trigger_skill_type: SkillType | None
    damage: int
    damage_elemental_type: DamageElementalType
    decrease_usage: bool

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        if skill used by self player, and is trigger skill type or trigger
        skill type is none, then make damage to opponent player's active 
        charactor.
        If self.decrease_usage is True, when make damage success, 
        decrease usage by 1.
        """
        assert self.usage >= 0
        if self.position.player_idx != event.action.position.player_idx:
            # not self player use skill
            return []
        if (
            self.trigger_skill_type is not None
            and event.action.skill_type != self.trigger_skill_type
        ):
            # not trigger skill type
            return []
        target = match.player_tables[
            1 - self.position.player_idx].get_active_charactor()
        if self.decrease_usage:
            self.usage -= 1
        return [MakeDamageAction(
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.DAMAGE,
                    target_position = target.position,
                    damage = self.damage,
                    damage_elemental_type = self.damage_elemental_type,
                    cost = Cost(),
                )
            ]
        )]


class ElementalInfusionTeamStatus(TeamStatusBase):
    """
    Base class of doing elemental infusion. It will infuse all physical damage
    to corresponding elemental damage for active charactor. If there extra
    conditions, filter the condition and call value modifier in subclasses.
    """

    name: Literal[
        'Pyro Elemental Infusion',
        'Hydro Elemental Infusion',
        'Electro Elemental Infusion',
        'Cryo Elemental Infusion',
        'Anemo Elemental Infusion',
        'Geo Elemental Infusion',
        'Dendro Elemental Infusion',
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
            element = self.name.split(' ')[0].upper()
            assert element in [
                'PYRO', 'HYDRO', 'ELECTRO', 'CRYO', 'ANEMO', 'GEO', 'DENDRO'
            ], ('In ElementalInfusion: element not set right value')
            assert self.name.split(' ')[1:] == ['Elemental', 'Infusion']
            self.infused_elemental_type = DamageElementalType(element)
        if self.icon_type == IconType.ATK_UP:
            self.icon_type = ELEMENT_TO_ENCHANT_ICON[
                ElementType(self.infused_elemental_type.value)]  # type: ignore

    def value_modifier_DAMAGE_ELEMENT_ENHANCE(
        self, value: DamageElementEnhanceValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageElementEnhanceValue:
        """
        When self use skill, change physical to corresponding element.
        NOTE: this function will not change the usage.
        """
        assert mode == 'REAL'
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not corresponding charactor use skill, do nothing
            return value
        if self.usage <= 0:  # pragma: no cover
            # no usage, do nothing
            return value
        # change physical to other element
        if value.damage_elemental_type == DamageElementalType.PHYSICAL:
            value.damage_elemental_type = self.infused_elemental_type
        return value


class SwitchActionTeamStatus(UsageTeamStatus):
    name: str
    version: str
    usage: int
    max_usage: int

    def _action(self, match: Any) -> List[Actions]:
        """
        action to perform when switch charactor
        """
        raise NotImplementedError()

    def _check(self, match: Any, event_player_idx: int) -> List[Actions]:
        if event_player_idx != self.position.player_idx:
            # not self switch charactor
            return []
        if self.usage <= 0:  # pragma: no cover
            # no usage
            return []
        self.usage -= 1
        return self._action(match)

    def event_handler_SWITCH_CHARACTOR(
        self, event: SwitchCharactorEventArguments, match: Any
    ) -> List[Actions]:
        """
        If self switch charactor, perform attack
        """
        return self._check(match, event.action.player_idx)

    def event_handler_CHOOSE_CHARACTOR(
        self, event: ChooseCharactorEventArguments, match: Any
    ) -> List[Actions]:
        """
        If self choose charactor (when ally defeated), perform attack
        """
        return self._check(match, event.action.player_idx)
