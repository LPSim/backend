from typing import Any, List, Literal

from .....utils.class_registry import register_class

from ....consts import ObjectPositionType, SkillType

from ....action import ChargeAction

from ....event import SkillEndEventArguments

from ....struct import Cost
from .base import RoundEffectArtifactBase


class ExilesCirclet_3_3(RoundEffectArtifactBase):
    name: Literal["Exile's Circlet"]
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(any_dice_number = 2)
    max_usage_per_round: int = 1

    def event_handler_SKILL_END(
        self, event: SkillEndEventArguments, match: Any
    ) -> List[ChargeAction]:
        """
        If self use elemental burst, charge standby charactors.
        """
        if not self.position.check_position_valid(
            event.action.position, match, player_idx_same = True,
            charactor_idx_same = True, 
            source_area = ObjectPositionType.CHARACTOR,
            target_area = ObjectPositionType.SKILL,
        ):
            # not equipped, or not this charactor use skill
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
        for cid, charactor in enumerate(match.player_tables[
                self.position.player_idx].charactors):
            if (
                cid == self.position.charactor_idx
                or charactor.is_defeated
            ):
                # skip self and defeated charactors
                continue
            ret.append(ChargeAction(
                player_idx = self.position.player_idx,
                charactor_idx = cid,
                charge = 1,
            ))
        return ret


register_class(ExilesCirclet_3_3)
