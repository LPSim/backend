from typing import Any, List, Literal

from .....utils.class_registry import register_class

from ....action import CreateDiceAction

from ....event import SkillEndEventArguments
from ....consts import (
    ELEMENT_TO_DIE_COLOR,
    ElementType,
    ObjectPositionType,
    SkillType,
    WeaponType,
)
from ....struct import Cost
from .base import RoundEffectWeaponBase


class SacrificialWeapons_3_3(RoundEffectWeaponBase):
    name: Literal[
        "Sacrificial Fragments",
        "Sacrificial Greatsword",
        "Sacrificial Sword",
        "Sacrificial Bow",
    ]
    cost: Cost = Cost(same_dice_number=3)
    version: Literal["3.3"] = "3.3"
    weapon_type: WeaponType = WeaponType.OTHER
    max_usage_per_round: int = 1

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.name == "Sacrificial Fragments":
            self.weapon_type = WeaponType.CATALYST
        elif self.name == "Sacrificial Bow":
            self.weapon_type = WeaponType.BOW
        elif self.name == "Sacrificial Sword":
            self.weapon_type = WeaponType.SWORD
        else:
            assert self.name == "Sacrificial Greatsword"
            self.weapon_type = WeaponType.CLAYMORE

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[CreateDiceAction]:
        """
        If self use elemental skill, create one corresponding dice
        """
        if not (
            self.position.area == ObjectPositionType.CHARACTER
            and event.action.position.player_idx == self.position.player_idx
            and event.action.position.character_idx == self.position.character_idx
            and event.action.skill_type == SkillType.ELEMENTAL_SKILL
            and self.usage > 0
        ):
            # not equipped or not self use elemental skill or no usage
            return []
        self.usage -= 1
        character = match.player_tables[self.position.player_idx].characters[
            self.position.character_idx
        ]
        ele_type: ElementType = character.element
        die_color = ELEMENT_TO_DIE_COLOR[ele_type]
        return [
            CreateDiceAction(
                player_idx=self.position.player_idx,
                number=1,
                color=die_color,
            )
        ]


register_class(SacrificialWeapons_3_3)
