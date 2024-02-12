from typing import Dict, List, Literal
from pydantic import PrivateAttr

from ....event_handler import SystemEventHandlerBase
from ....object_base import CreateSystemEventHandlerObject
from .....utils.class_registry import register_class
from ....struct import Cost
from ....action import ChangeObjectUsageAction, DrawCardAction, RemoveObjectAction
from ....match import Match
from ....event import (
    MoveObjectEventArguments,
    ReceiveDamageEventArguments,
    RoundEndEventArguments,
)
from ....consts import DamageElementalType, DamageType, IconType
from ....card.support.companions import CompanionBase
from .....utils.desc_registry import DescDictType


class SilverAndMelusEventHandler_4_4(SystemEventHandlerBase):
    """
    It will be generated when Silver and Melus in deck, and record elemental damage
    types for both player, and when Silver and Melus is played into area or elemental
    damage is made, it will update its counter and also update all existing Silver and
    Melus usage.
    """

    name: Literal["Silver and Melus"] = "Silver and Melus"
    version: Literal["4.4"] = "4.4"
    etypes: List[List[DamageElementalType]] = [[], []]
    _max_usage: int = PrivateAttr(4)

    def _update_usage(self, match: Match) -> List[ChangeObjectUsageAction]:
        """
        check all, if their usage not same as self, update it.
        """
        actions: List[ChangeObjectUsageAction] = []
        for etypes, table in zip(self.etypes, match.player_tables):
            counter = min(len(etypes), self._max_usage)
            for support in table.supports:
                if support.name == self.name and support.usage != counter:
                    actions.append(
                        ChangeObjectUsageAction(
                            object_position=support.position,
                            change_usage=counter - support.usage,
                        )
                    )
        return actions

    def event_handler_MOVE_OBJECT(
        self, event: MoveObjectEventArguments, match: Match
    ) -> List[ChangeObjectUsageAction]:
        if event.object_name != self.name:
            # not Silver and Melus
            return []
        return self._update_usage(match)

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[ChangeObjectUsageAction]:
        pidx = event.final_damage.target_position.player_idx
        if event.final_damage.damage_type != DamageType.DAMAGE or (
            event.final_damage.damage_elemental_type
            in [
                DamageElementalType.PIERCING,
                DamageElementalType.PHYSICAL,
                DamageElementalType.HEAL,
            ]
        ):
            # not damage or damage type not elemental
            return []
        # record damage type
        damage_element = event.final_damage.damage_elemental_type
        # damage is too frequent. If not new damage type, do not check usage.
        changed = False
        if damage_element not in self.etypes[1 - pidx]:
            self.etypes[1 - pidx].append(damage_element)
            changed = True
        if not changed:
            return []
        return self._update_usage(match)


class SilverAndMelus_4_4(CreateSystemEventHandlerObject, CompanionBase):
    name: Literal["Silver and Melus"]
    version: Literal["4.4"] = "4.4"
    usage: int = 0
    _max_usage: int = PrivateAttr(4)
    recorded_damage_type: List[DamageElementalType] = []
    icon_type: Literal[IconType.TIMESTATE] = IconType.TIMESTATE
    cost: Cost = Cost(same_dice_number=1)

    handler_name: Literal["Silver and Melus"] = "Silver and Melus"

    def event_handler_ROUND_END(
        self,
        event: RoundEndEventArguments,
        match: Match,
    ) -> List[DrawCardAction | RemoveObjectAction]:
        """
        If usage above 3, remove self and draw cards.
        """
        if self.usage < 3:
            return []
        return [
            DrawCardAction(
                player_idx=self.position.player_idx,
                number=self.usage,
                draw_if_filtered_not_enough=True,
            ),
            RemoveObjectAction(object_position=self.position),
        ]


desc: Dict[str, DescDictType] = {
    "SUPPORT/Silver and Melus": {
        "names": {"en-US": "Silver and Melus", "zh-CN": "西尔弗和迈勒斯"},
        "descs": {
            "4.4": {
                "en-US": "This card will record the number of types of Elemental DMG opposing characters have taken during this match as points of Attendant's Attentiveness. (Max 4 points)\nEnd Phase: If you have at least 3 Attendant's Attentiveness points, discard this card and draw cards equal to the amount of Attendant's Attentiveness points.",  # noqa: E501
                "zh-CN": "此牌会记录本场对局中敌方角色受到过的元素伤害种类数，称为「侍从的周到」。（最多4点）\n结束阶段：如果「侍从的周到」至少为3，则弃置此牌，然后抓「侍从的周到」点数的牌。",  # noqa: E501
            }
        },
        "image_path": "cardface/Assist_NPC_Silver.png",  # noqa: E501
        "id": 322023,
    },
    "SYSTEM/Silver and Melus": {
        "names": {"en-US": "Silver and Melus", "zh-CN": "西尔弗和迈勒斯"},
        "descs": {"4.4": {}},
    },
}


register_class(SilverAndMelus_4_4 | SilverAndMelusEventHandler_4_4, desc)
