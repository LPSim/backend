from typing import Any, List, Literal

from .....utils.class_registry import register_class

from ....event import ChooseCharacterEventArguments, SwitchCharacterEventArguments

from ....action import CreateObjectAction
from ....modifiable_values import CostValue, DamageIncreaseValue
from ....consts import CostLabels, ObjectPositionType, SkillType
from ....struct import Cost
from .base import RoundEffectArtifactBase


class SkillCostDecreaseArtifact(RoundEffectArtifactBase):
    name: str
    version: str
    cost: Cost
    skill_label: int  # CostLabels

    max_usage_per_round: int = 1

    def value_modifier_COST(
        self,
        value: CostValue,
        match: Any,
        mode: Literal["TEST", "REAL"],
    ) -> CostValue:
        if self.usage > 0:
            # has usage
            if not self._check_value_self_skill_or_talent(
                value, match, self.skill_label
            ):
                return value
            # can decrease cost
            if (  # pragma: no branch
                value.cost.decrease_cost(value.cost.elemental_dice_color)
            ):
                # decrease cost success
                if mode == "REAL":
                    self.usage -= 1
        return value


class ThunderingPoise_4_0(SkillCostDecreaseArtifact):
    name: Literal["Thundering Poise"]
    version: Literal["4.0"] = "4.0"
    cost: Cost = Cost(any_dice_number=2)
    skill_label: int = CostLabels.NORMAL_ATTACK.value


class VermillionHereafter_4_0(ThunderingPoise_4_0):
    name: Literal["Vermillion Hereafter"]
    cost: Cost = Cost(any_dice_number=3)

    def _attach_status(
        self, player_idx: int, character_idx: int
    ) -> List[CreateObjectAction]:
        """
        attach status
        """
        if (
            player_idx == self.position.player_idx
            and character_idx == self.position.character_idx
            and self.position.area == ObjectPositionType.CHARACTER
        ):
            # equipped and switch to this character
            return [
                CreateObjectAction(
                    object_position=self.position.set_area(
                        ObjectPositionType.CHARACTER_STATUS
                    ),
                    object_name=self.name,
                    object_arguments={},
                )
            ]
        return []

    def event_handler_SWITCH_CHARACTER(
        self, event: SwitchCharacterEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If switch to this character, attach status.
        """
        return self._attach_status(event.action.player_idx, event.action.character_idx)

    def event_handler_CHOOSE_CHARACTER(
        self, event: ChooseCharacterEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        If choose this character, attach status.
        """
        return self._attach_status(event.action.player_idx, event.action.character_idx)


class CapriciousVisage_4_0(SkillCostDecreaseArtifact):
    name: Literal["Capricious Visage"]
    version: Literal["4.0"] = "4.0"
    cost: Cost = Cost(any_dice_number=2)
    skill_label: int = CostLabels.ELEMENTAL_SKILL.value


class ShimenawasReminiscence_4_0(CapriciousVisage_4_0):
    name: Literal["Shimenawa's Reminiscence"]
    cost: Cost = Cost(any_dice_number=3)

    def value_modifier_DAMAGE_INCREASE(
        self,
        value: DamageIncreaseValue,
        match: Any,
        mode: Literal["TEST", "REAL"],
    ) -> DamageIncreaseValue:
        """
        if this character has at least 2 energy and use normal attack or
        elemental skill, +1 damage.
        """
        if not value.is_corresponding_character_use_damage_skill(
            self.position, match, None
        ):
            # not current character using skill
            return value
        skill = match.get_object(value.position)
        if skill.skill_type not in [SkillType.NORMAL_ATTACK, SkillType.ELEMENTAL_SKILL]:
            # skill type not match
            return value
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        if character.charge < 2:
            # not enough energy
            return value
        # increase damage
        assert mode == "REAL"
        value.damage += 1
        return value


class ThunderingPoise_3_7(ThunderingPoise_4_0):
    version: Literal["3.7"]
    cost: Cost = Cost(same_dice_number=2)


class VermillionHereafter_3_7(VermillionHereafter_4_0):
    version: Literal["3.7"]
    cost: Cost = Cost(same_dice_number=3)


class CapriciousVisage_3_7(CapriciousVisage_4_0):
    version: Literal["3.7"]
    cost: Cost = Cost(same_dice_number=2)


class ShimenawasReminiscence_3_7(ShimenawasReminiscence_4_0):
    version: Literal["3.7"]
    cost: Cost = Cost(same_dice_number=3)


register_class(
    ThunderingPoise_4_0
    | VermillionHereafter_4_0
    | CapriciousVisage_4_0
    | ShimenawasReminiscence_4_0
    | ThunderingPoise_3_7
    | VermillionHereafter_3_7
    | CapriciousVisage_3_7
    | ShimenawasReminiscence_3_7
)
