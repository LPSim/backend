from typing import Any, List, Literal

from ....event import (
    ChooseCharactorEventArguments, SwitchCharactorEventArguments
)

from ....action import CreateObjectAction
from ....modifiable_values import CostValue, DamageIncreaseValue
from ....consts import CostLabels, ObjectPositionType, SkillType
from ....struct import Cost
from .base import RoundEffectArtifactBase


class SkillCostDecreaseArtifact(RoundEffectArtifactBase):
    name: str
    desc: str
    version: str
    cost: Cost
    skill_label: int  # CostLabels

    max_usage_per_round: int = 1

    def value_modifier_COST(
        self, value: CostValue, match: Any, mode: Literal['TEST', 'REAL'],
    ) -> CostValue:
        if self.usage > 0:  
            # has usage
            if not self.position.check_position_valid(
                value.position, match,
                player_idx_same = True, 
                source_area = ObjectPositionType.CHARACTOR,
            ):
                # not from self position or not equipped
                return value
            label = value.cost.label
            target = CostLabels.TALENT.value | self.skill_label
            if label & target == 0:
                # no label match
                return value
            position = value.position
            assert self.position.charactor_idx != -1
            if position.area == ObjectPositionType.SKILL:
                # cost from charactor
                if position.charactor_idx != self.position.charactor_idx:
                    # not same charactor
                    return value
            else:
                assert position.area == ObjectPositionType.HAND
                # cost from hand card, is a talent card
                equipped_charactor = match.player_tables[
                    self.position.player_idx
                ].charactors[self.position.charactor_idx]
                for card in match.player_tables[
                        self.position.player_idx].hands:
                    if card.id == value.position.id:
                        if card.charactor_name != equipped_charactor.name:
                            # talent card not for this charactor
                            return value
            # can decrease cost
            if (  # pragma: no branch
                value.cost.decrease_cost(value.cost.elemental_dice_color)
            ):
                # decrease cost success
                if mode == 'REAL':
                    self.usage -= 1
        return value


class ThunderingPoise(SkillCostDecreaseArtifact):
    name: Literal['Thundering Poise']
    desc: str = (
        'When the character uses a Normal Attack or equips a Talent: Spend 1 '
        'less Elemental Die. (Once per Round)'
    )
    version: Literal['4.0'] = '4.0'
    cost: Cost = Cost(any_dice_number = 2)
    skill_label: int = CostLabels.NORMAL_ATTACK.value


class VermillionHereafter(ThunderingPoise):
    name: Literal['Vermillion Hereafter']
    desc: str = (
        'When the character uses a Normal Attack or equips a Talent: Spend 1 '
        'less Elemental Die. (Once per Round) '
        'After a character is switched to the active character: During this '
        'Round, character deals +1 Normal Attack DMG.'
    )
    cost: Cost = Cost(any_dice_number = 3)

    def _attach_status(
        self, player_idx: int, charactor_idx: int
    ) -> List[CreateObjectAction]:
        """
        attach status
        """
        if (
            player_idx == self.position.player_idx
            and charactor_idx == self.position.charactor_idx
            and self.position.area == ObjectPositionType.CHARACTOR
        ):
            # equipped and switch to this charactor
            return [CreateObjectAction(
                object_position = self.position.set_area(
                    ObjectPositionType.CHARACTOR_STATUS),
                object_name = self.name,
                object_arguments = {}
            )]
        return []

    def event_handler_SWITCH_CHARACTOR(
        self, event: SwitchCharactorEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If switch to this charactor, attach status.
        """
        return self._attach_status(event.action.player_idx, 
                                   event.action.charactor_idx)

    def event_handler_CHOOSE_CHARACTOR(
        self, event: ChooseCharactorEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If choose this charactor, attach status.
        """
        return self._attach_status(event.action.player_idx, 
                                   event.action.charactor_idx)


class CapriciousVisage(SkillCostDecreaseArtifact):
    name: Literal['Capricious Visage']
    desc: str = (
        'When the character uses an Elemental Skill or equips a Talent: Spend '
        '1 less Elemental Die. (Once per Round)'
    )
    version: Literal['4.0'] = '4.0'
    cost: Cost = Cost(any_dice_number = 2)
    skill_label: int = CostLabels.ELEMENTAL_SKILL.value


class ShimenawasReminiscence(CapriciousVisage):
    name: Literal["Shimenawa's Reminiscence"]
    desc: str = (
        'When the character uses an Elemental Skill or equips a Talent: Spend '
        '1 less Elemental Die. (Once per Round) '
        "If the character has at least 2 Energy, this character's Normal "
        "Attacks and Elemental Skills will deal +1 DMG."
    )
    cost: Cost = Cost(any_dice_number = 3)

    def value_modifier_DAMAGE_INCREASE(
        self, value: DamageIncreaseValue, match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> DamageIncreaseValue:
        """
        if this charactor has at least 2 energy and use normal attack or
        elemental skill, +1 damage.
        """
        if not value.is_corresponding_charactor_use_damage_skill(
            self.position, match, None
        ):
            # not current charactor using skill
            return value
        skill = match.get_object(value.position)
        if skill.skill_type not in [SkillType.NORMAL_ATTACK, 
                                    SkillType.ELEMENTAL_SKILL]:
            # skill type not match
            return value
        charactor = match.player_tables[
            self.position.player_idx].charactors[self.position.charactor_idx]
        if charactor.charge < 2:
            # not enough energy
            return value
        # increase damage
        assert mode == 'REAL'
        value.damage += 1
        return value


VermillionShimenawas = (
    ThunderingPoise | VermillionHereafter
    | CapriciousVisage | ShimenawasReminiscence 
)
