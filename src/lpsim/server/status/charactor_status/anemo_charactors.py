from typing import Any, List, Literal

from ...modifiable_values import DamageElementEnhanceValue, DamageIncreaseValue
from ...action import Actions, RemoveObjectAction
from ...event import MakeDamageEventArguments, SkillEndEventArguments
from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, ElementType, ElementalReactionType, 
    ObjectPositionType, SkillType
)
from .base import ElementalInfusionCharactorStatus


class MidareRanzan(ElementalInfusionCharactorStatus):
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
    desc: str = (
        'When the attached character uses a Plunging Attack: Physical DMG '
        'dealt becomes _ELEMENT_ DMG, and deals +1 DMG. '
        'After the character uses a skill: This effect is removed.'
    )
    element: ElementType = ElementType.NONE
    version: Literal['3.8'] = '3.8'
    usage: int = 1
    max_usage: int = 1
    newly_created: bool = True

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
            self.desc = self.desc.replace('_ELEMENT_', 
                                          self.element.name.capitalize())
        else:
            assert skill_used, 'kazuha elemental skill damage not found'
            if self.element == ElementType.NONE:
                # no swirl, change to anemo
                self.name = 'Midare Ranzan'
                self.element = ElementType.ANEMO
                self.desc = self.desc.replace('_ELEMENT_', 'Anemo')
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


AnemoCharactorStatus = MidareRanzan | MidareRanzan
