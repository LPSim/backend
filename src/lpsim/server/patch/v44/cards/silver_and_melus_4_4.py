"""
TODO: same as jeht
"""
from typing import Dict, List, Literal

from pydantic import PrivateAttr

from .....utils.class_registry import register_class
from ....struct import Cost
from ....action import Actions, DrawCardAction, RemoveObjectAction
from ....match import Match
from ....event import (
    ReceiveDamageEventArguments, RoundEndEventArguments
)
from ....consts import (
    DamageElementalType, DamageType, IconType, ObjectPositionType
)
from ....card.support.companions import CompanionBase
from .....utils.desc_registry import DescDictType


class SilverAndMelus_4_4(CompanionBase):
    name: Literal['Silver and Melus']
    version: Literal['4.4'] = '4.4'
    usage: int = 0
    _max_usage: int = PrivateAttr(4)
    recorded_damage_type: List[DamageElementalType] = []
    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE
    cost: Cost = Cost(same_dice_number = 1)

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[Actions]:
        if not self.position.check_position_valid(
            event.final_damage.target_position, match, player_idx_same = False,
            source_area = ObjectPositionType.SUPPORT
        ):
            # self not in support or damage receive not in enemy
            return []
        if (
            event.final_damage.damage_type != DamageType.DAMAGE
            or (
                event.final_damage.damage_elemental_type 
                in [
                    DamageElementalType.PIERCING,
                    DamageElementalType.PHYSICAL,
                    DamageElementalType.HEAL,
                ]
            )
        ):
            # not damage or damage type not elemental
            return []
        # record damage type
        damage_element = event.final_damage.damage_elemental_type
        if damage_element not in self.recorded_damage_type:
            self.recorded_damage_type.append(damage_element)
        self.usage = min(len(self.recorded_damage_type), self._max_usage)
        return []

    def event_handler_ROUND_END(
        self, event: RoundEndEventArguments, match: Match,
    ) -> List[DrawCardAction | RemoveObjectAction]:
        """
        If usage above 3, remove self and draw cards.
        """
        if self.usage < 3:
            return []
        return [
            DrawCardAction(
                player_idx = self.position.player_idx,
                number = self.usage,
                draw_if_filtered_not_enough = True
            ),
            RemoveObjectAction(
                object_position = self.position
            ),
        ]


desc: Dict[str, DescDictType] = {
    "SUPPORT/Silver and Melus": {
        "names": {
            "en-US": "Silver and Melus",
            "zh-CN": "西尔弗和迈勒斯"
        },
        "descs": {
            "4.4": {
                "en-US": "This card will record the number of types of Elemental DMG opposing characters have taken during this match as points of Attendant's Attentiveness. (Max 4 points)\nEnd Phase: If you have at least 3 Attendant's Attentiveness points, discard this card and draw cards equal to the amount of Attendant's Attentiveness points.",  # noqa: E501
                "zh-CN": "此牌会记录本场对局中敌方角色受到过的元素伤害种类数，称为「侍从的周到」。（最多4点）\n结束阶段：如果「侍从的周到」至少为3，则弃置此牌，然后抓「侍从的周到」点数的牌。"  # noqa: E501
            }
        },
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Assist_NPC_Silver.png",  # noqa: E501
        "id": 322023
    },
}


register_class(SilverAndMelus_4_4, desc)
