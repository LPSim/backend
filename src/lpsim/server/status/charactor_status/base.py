from typing import Any, Literal, List

from ....utils.class_registry import register_base_class

from ...struct import Cost

from ...modifiable_values import (
    DamageDecreaseValue, DamageElementEnhanceValue, DamageValue
)
from ...consts import (
    ELEMENT_TO_ENCHANT_ICON, DamageElementalType, DamageType, ElementType, 
    IconType, ObjectType, PlayerActionLabels
)
from ..base import StatusBase
from ...action import (
    ActionEndAction, MakeDamageAction, RemoveObjectAction, Actions, 
    SkipPlayerActionAction, UseSkillAction
)
from ...event import (
    ChooseCharactorEventArguments, MakeDamageEventArguments, 
    PlayerActionStartEventArguments, RoundEndEventArguments, 
    RoundPrepareEventArguments, SwitchCharactorEventArguments
)


class CharactorStatusBase(StatusBase):
    """
    Base class of charactor status.
    """
    type: Literal[ObjectType.CHARACTOR_STATUS] = ObjectType.CHARACTOR_STATUS
    name: str
    version: str
    usage: int
    max_usage: int


register_base_class(CharactorStatusBase)


class UsageCharactorStatus(CharactorStatusBase):
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


class RoundCharactorStatus(CharactorStatusBase):
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


class DefendCharactorStatus(UsageCharactorStatus):
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
            return value
        new_usage = value.apply_shield(
            self.usage, self.min_damage_to_trigger, 
            self.max_in_one_time, self.decrease_usage_by_damage,
        )
        assert mode == 'REAL'
        self.usage = new_usage
        return value


class ShieldCharactorStatus(DefendCharactorStatus):
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


class ElementalInfusionCharactorStatus(CharactorStatusBase):
    """
    Base class of doing elemental infusion. It will infuse all physical damage
    to corresponding elemental damage for this charactor. If there extra
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


class PrepareCharactorStatus(CharactorStatusBase):
    """
    Prepare status will trigger when self player action start, and try to
    use a specified skill, and skip next player action phase.
    if this charactor is stunned, it will do nothing.

    When this charactor is not active charactor, it will remove itself. 
    """
    name: str
    version: str
    charactor_name: str
    skill_name: str

    usage: int = 1
    max_usage: int = 1
    icon_type: Literal[IconType.SPECIAL] = IconType.SPECIAL

    def event_handler_SWITCH_CHARACTOR(
        self, event: SwitchCharactorEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        If self switch charactor, after switch if this charactor is not active
        charactor, remove this status.
        """
        if event.action.player_idx != self.position.player_idx:
            # not self switch charactor
            return []
        return [RemoveObjectAction(
            object_position = self.position,
        )]

    def event_handler_CHOOSE_CHARACTOR(
        self, event: ChooseCharactorEventArguments, match: Any
    ) -> List[MakeDamageAction]:
        """
        As choose charactor only happens on charactor defeated, it is not
        possible.
        """
        if event.action.player_idx != self.position.player_idx:
            # not self choose charactor
            return []
        raise NotImplementedError('Should not be called')
        return [RemoveObjectAction(
            object_position = self.position,
        )]

    def event_handler_PLAYER_ACTION_START(
        self, event: PlayerActionStartEventArguments, match: Any
    ) -> List[RemoveObjectAction | UseSkillAction 
              | SkipPlayerActionAction | ActionEndAction]:
        """
        If self player action start, and this charactor is at front,
        use skill, remove this status, and skip player action.
        """
        if event.player_idx != self.position.player_idx:
            # not self player action start, do nothing
            return []
        table = match.player_tables[self.position.player_idx]
        active_idx = table.active_charactor_idx
        if active_idx != self.position.charactor_idx:  # pragma: no cover
            # not active charactor, do nothing
            return []
        charactor = table.get_active_charactor()
        if charactor.is_stunned:
            # stunned, do nothing
            return []
        ret: List[
            RemoveObjectAction | UseSkillAction | SkipPlayerActionAction
            | ActionEndAction
        ] = []
        ret.append(RemoveObjectAction(object_position = self.position))
        assert charactor.name == self.charactor_name
        # use skill
        for skill in charactor.skills:
            if skill.name == self.skill_name:
                # clear, should not remove self first
                ret.clear()
                ret.append(UseSkillAction(skill_position = skill.position))
                # skip player action
                ret.append(SkipPlayerActionAction())
                # remove self
                ret.append(RemoveObjectAction(object_position = self.position))
                # action end action to switch player
                ret.append(ActionEndAction(
                    action_label = PlayerActionLabels.SKILL,
                    do_combat_action = True,
                    position = skill.position,
                ))
                # note based on its description, no skill end action will be
                # triggered.
                return ret
        else:
            raise AssertionError('Skill not found')


class ReviveCharactorStatus(UsageCharactorStatus):
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
        when make damage, check whether this charactor's hp is 0. if so,
        heal it by self.heal hp.

        Using make damage action, so it will trigger immediately before
        receiving any other damage, and can be defeated by other damage.
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        if charactor.hp > 0:
            # hp not 0, do nothing
            return []
        if self.usage <= 0:  # pragma: no cover
            # no usage, do nothing
            return []
        # heal this charactor by 1
        self.usage -= 1
        return [MakeDamageAction(
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.HEAL,
                    target_position = charactor.position,
                    damage = - self.heal,
                    damage_elemental_type = DamageElementalType.HEAL,
                    cost = Cost()
                )
            ],
        )] + self.check_should_remove()


class RoundEndAttackCharactorStatus(UsageCharactorStatus):
    """
    Make damage to this charactor at round end. It can also be heal, e.g.
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
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        damage_type = DamageType.DAMAGE
        if self.damage < 0:
            damage_type = DamageType.HEAL
        return [MakeDamageAction(
            damage_value_list = [
                DamageValue(
                    position = self.position,
                    damage_type = damage_type,
                    target_position = charactor.position,
                    damage = self.damage,
                    damage_elemental_type = self.damage_elemental_type,
                    cost = Cost()
                )
            ]
        )]
