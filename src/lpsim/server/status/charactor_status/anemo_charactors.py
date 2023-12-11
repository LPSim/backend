from typing import Any, List, Literal

from ....utils.class_registry import register_class

from ...modifiable_values import (
    CostValue, DamageElementEnhanceValue, DamageIncreaseValue
)
from ...action import Actions, RemoveObjectAction
from ...event import (
    MakeDamageEventArguments, RoundPrepareEventArguments, 
    SkillEndEventArguments
)
from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, ELEMENT_TO_ENCHANT_ICON, CostLabels, 
    DamageElementalType, DieColor, ElementType, ElementalReactionType, 
    IconType, ObjectPositionType, SkillType
)
from .base import (
    CharactorStatusBase, ElementalInfusionCharactorStatus, RoundCharactorStatus
)


class MidareRanzan_3_8(ElementalInfusionCharactorStatus):
    name: Literal[
        # newly created ranzan, and will change its element based on kazuha
        # skill.
        'Midare Ranzan: New',
        # no swirl reaction, anemo element
        'Midare Ranzan',
        # swirl, corresponding element
        'Midare Ranzan: Pyro',
        'Midare Ranzan: Hydro',
        'Midare Ranzan: Cryo',
        'Midare Ranzan: Electro',
    ] = 'Midare Ranzan'
    element: ElementType = ElementType.NONE
    version: Literal['3.8'] = '3.8'
    usage: int = 1
    max_usage: int = 1
    newly_created: bool = True
    icon_type: Literal[
        IconType.ELEMENT_ENCHANT_ELEC,
        IconType.ELEMENT_ENCHANT_FIRE,
        IconType.ELEMENT_ENCHANT_WATER,
        IconType.ELEMENT_ENCHANT_ICE,
        IconType.ELEMENT_ENCHANT_WIND
    ] = IconType.ELEMENT_ENCHANT_WIND

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Do not call ElementalInfusionCharactorStatus.__init__(), because the
        element type is not determined at this time.
        """
        super(ElementalInfusionCharactorStatus, self).__init__(*args, **kwargs)

    def value_modifier_DAMAGE_ELEMENT_ENHANCE(
        self, value: DamageElementEnhanceValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageElementEnhanceValue:
        """
        Assert that self.element is correctly set, and if not plunging attack,
        do not modify.
        """
        assert self.newly_created or self.element != ElementType.NONE, (
            'not newly created, but element not set'
        )
        if not match.player_tables[self.position.player_idx].plunge_satisfied:
            # not plunging attack, do nothing
            return value
        return super().value_modifier_DAMAGE_ELEMENT_ENHANCE(
            value, match, mode
        )

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        """
        if plunging attack, +1 DMG.
        """
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, SkillType.NORMAL_ATTACK
        ):
            # not self normal attack, do nothing
            return value
        if not match.player_tables[self.position.player_idx].plunge_satisfied:
            # not plunging attack, do nothing
            return value
        # plunging attack, +1 DMG
        value.damage += 1
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        when damage made, if kazuha did elemental skill, change element type
        based on damage results. This should be triggered immediately after
        it is created and by kazuha's elemental skill, and the element type
        is determined at that time.
        """
        if self.name != 'Midare Ranzan: New':
            # not newly created, do nothing
            return []
        skill_used: bool = False
        for damage in event.damages:
            if not self.position.check_position_valid(
                damage.final_damage.position, match, 
                player_idx_same = True, charactor_idx_same = True, 
                target_area = ObjectPositionType.SKILL,
            ):  # pragma: no cover
                # not self charactor use skill, do nothing
                continue
            skill = match.get_object(damage.final_damage.position)
            assert skill.skill_type == SkillType.ELEMENTAL_SKILL
            skill_used = True
            if damage.elemental_reaction != ElementalReactionType.SWIRL:
                # not swirl, do nothing
                continue
            # swirl, change element type
            assert self.name == 'Midare Ranzan: New'
            for element in damage.reacted_elements:
                if element != ElementType.ANEMO:
                    self.element = element
            self.name = (
                f'Midare Ranzan: {self.element.name.capitalize()}'
            )  # type: ignore
            self.icon_type = ELEMENT_TO_ENCHANT_ICON[
                self.element]  # type: ignore
        else:
            assert skill_used, 'kazuha elemental skill damage not found'
            if self.element == ElementType.NONE:
                # no swirl, change to anemo
                self.name = 'Midare Ranzan'
                self.element = ElementType.ANEMO
        self.infused_elemental_type = ELEMENT_TO_DAMAGE_TYPE[self.element]
        return []

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[RemoveObjectAction]:
        """
        When skill end by this charactor, if it is newly created, mark False 
        and do nothing. Otherwise, remove itself.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True,
            target_area = ObjectPositionType.SKILL,
        ):
            # not this charactor use skill, do nothing
            return []
        if self.newly_created:
            # this card is newly created, mark False and do nothing.
            self.newly_created = False
            return []
        # remove itself
        return [RemoveObjectAction(
            object_position = self.position
        )]


class YakshasMask_3_7(ElementalInfusionCharactorStatus, RoundCharactorStatus):
    name: Literal["Yaksha's Mask"] = "Yaksha's Mask"
    version: Literal['3.7'] = '3.7'
    usage: int = 2
    max_usage: int = 2
    infused_elemental_type: DamageElementalType = DamageElementalType.ANEMO
    icon_type: Literal[IconType.OTHERS] = IconType.OTHERS
    switch_cost_decrease_usage: int = 1
    switch_cost_decrease_max_usage: int = 1

    skill_cost_decrease_usage: int = 0

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Any
    ) -> List[Actions]:
        self.switch_cost_decrease_usage = self.switch_cost_decrease_max_usage
        return super().event_handler_ROUND_PREPARE(event, match)

    def renew(self, new_status: 'YakshasMask_3_7') -> None:
        self.switch_cost_decrease_usage = new_status.switch_cost_decrease_usage
        self.skill_cost_decrease_usage = new_status.skill_cost_decrease_usage
        super().renew(new_status)

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any, 
        mode: Literal['TEST', 'REAL']
    ) -> DamageIncreaseValue:
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not self use damage skill
            return value
        if (
            value.is_corresponding_charactor_use_damage_skill(
                self.position, match, SkillType.NORMAL_ATTACK
            )
            and match.player_tables[self.position.player_idx].plunge_satisfied
        ):
            # self use plunge attack, increase damage by 2
            value.damage += 2
        if (  # pragma: no branch
            value.damage_elemental_type == DamageElementalType.ANEMO
        ):
            # anemo damage, increase damage by 1
            value.damage += 1
        return value

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL']
    ) -> CostValue:
        if value.cost.label & CostLabels.SWITCH_CHARACTOR.value != 0:
            # switch charactor cost
            if (
                value.position.player_idx != self.position.player_idx
                or value.position.charactor_idx != self.position.charactor_idx
                or self.switch_cost_decrease_usage <= 0
            ):
                # not self switch from this charactor, or no usage
                return value
            # decrease cost
            if value.cost.decrease_cost(None):  # pragma: no branch
                if mode == 'REAL':
                    self.switch_cost_decrease_usage -= 1
        elif value.cost.label & CostLabels.ELEMENTAL_SKILL.value != 0:
            # elemental skill
            if not (
                self.position.check_position_valid(
                    value.position, match, player_idx_same = True, 
                    charactor_idx_same = True, 
                    target_area = ObjectPositionType.SKILL
                )
                and self.skill_cost_decrease_usage > 0
            ):
                # not self use skill, or no usage
                return value
            # decrease cost
            if value.cost.decrease_cost(DieColor.ANEMO):  # pragma: no branch
                if mode == 'REAL':
                    self.skill_cost_decrease_usage -= 1
        return value


class Windfavored_4_1(CharactorStatusBase):
    """
    As attack target will be changed, we do not contain triggers for this
    status; instead, maintenance its usage by normal attack. The only exception
    is remove self, when its usage becomes zero in skill end, we will remove
    self.
    """
    name: Literal['Windfavored'] = 'Windfavored'
    version: Literal['4.1'] = '4.1'
    usage: int = 2
    max_usage: int = 2
    icon_type: Literal[IconType.ATK_UP] = IconType.ATK_UP

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[Actions]:
        """
        If out of usage, remove self. We do not remove it when usage changes
        because talent card should check whether this status exists. As it is
        triggered after talent card, even its usage becomes zero, talent card
        will still be triggered. Usage change should only happen when this
        charactor performs normal attack.
        """
        if self.usage <= 0:
            return [RemoveObjectAction(object_position = self.position)]
        return []


register_class(MidareRanzan_3_8 | YakshasMask_3_7 | Windfavored_4_1)
