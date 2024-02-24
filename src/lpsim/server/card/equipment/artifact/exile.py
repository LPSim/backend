from typing import Any, List, Literal

from .....utils.class_registry import register_class
from ....consts import SkillType
from ....action import ChargeAction
from ....event import SkillEndEventArguments
from ....struct import Cost
from .base import RoundEffectArtifactBase


class ExilesCirclet_3_3(RoundEffectArtifactBase):
    name: Literal["Exile's Circlet"]
    version: Literal["3.3"] = "3.3"
    cost: Cost = Cost(any_dice_number=2)
    max_usage_per_round: int = 1

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[ChargeAction]:
        """
        If self use elemental burst, charge standby characters.
        """
        if self.position.not_satisfy(
            "both pidx=same cidx=same and source area=character and target area=skill",
            event.action.position,
        ):
            # not equipped, or not this character use skill
            return []
        if self.usage <= 0:
            # no usage left
            return []
        if event.action.skill_type != SkillType.ELEMENTAL_BURST:
            # not elemental burst
            return []
        # charge
        self.usage -= 1
        ret: List[ChargeAction] = []
        for cid, character in enumerate(
            match.player_tables[self.position.player_idx].characters
        ):
            if cid == self.position.character_idx or character.is_defeated:
                # skip self and defeated characters
                continue
            ret.append(
                ChargeAction(
                    player_idx=self.position.player_idx,
                    character_idx=cid,
                    charge=1,
                )
            )
        return ret


register_class(ExilesCirclet_3_3)
