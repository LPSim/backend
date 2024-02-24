from typing import Any, List, Literal

from .....utils.class_registry import register_class

from ....consts import SkillType, WeaponType

from ....action import ChargeAction
from ....event import SkillEndEventArguments
from ....struct import Cost
from .base import RoundEffectWeaponBase


class FavoniusBase(RoundEffectWeaponBase):
    name: str
    cost: Cost = Cost(same_dice_number=3)
    version: str
    weapon_type: WeaponType
    max_usage_per_round: int = 1

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[ChargeAction]:
        """
        if self character use elemental skill, charge one more
        """
        if self.position.not_satisfy(
            "both pidx=same cidx=same and source area=character and target area=skill",
            event.action.position,
        ):
            # not self character or not equipped
            return []
        if event.action.skill_type != SkillType.ELEMENTAL_SKILL:
            # not elemental skill
            return []
        if self.usage <= 0:
            # no usage
            return []
        self.usage -= 1
        return [
            ChargeAction(
                player_idx=self.position.player_idx,
                character_idx=self.position.character_idx,
                charge=1,
            )
        ]


class FavoniusSword_3_7(FavoniusBase):
    name: Literal["Favonius Sword"]
    version: Literal["3.7"] = "3.7"
    weapon_type: Literal[WeaponType.SWORD] = WeaponType.SWORD


register_class(FavoniusSword_3_7)
