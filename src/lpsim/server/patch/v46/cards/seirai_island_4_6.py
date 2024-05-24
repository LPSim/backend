from re import Match
from typing import Literal
from lpsim.server.action import CreateObjectAction, RemoveObjectAction
from lpsim.server.card.support.locations import LocationBase
from lpsim.server.consts import (
    DamageElementalType,
    DamageType,
    IconType,
    ObjectPositionType,
)
from lpsim.server.event import ReceiveDamageEventArguments, RoundPrepareEventArguments
from lpsim.server.status.character_status.base import RoundEndAttackCharacterStatus
from lpsim.server.struct import Cost
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class DistantStorm_4_6(RoundEndAttackCharacterStatus):
    name: Literal["Distant Storm"] = "Distant Storm"
    version: Literal["4.6"] = "4.6"
    usage: int = 1
    max_usage: int = 1
    damage: int = 2
    damage_elemental_type: DamageElementalType = DamageElementalType.PIERCING


class SeiraiIsland_4_6(LocationBase):
    name: Literal["Seirai Island"]
    version: Literal["4.6"] = "4.6"
    usage: int = 2
    cost: Cost = Cost(same_dice_number=1)

    icon_type: IconType = IconType.TIMESTATE

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> list[CreateObjectAction]:
        if self.position.area != ObjectPositionType.SUPPORT:
            return []
        damage = event.final_damage
        if damage.damage_type is not DamageType.HEAL:
            return []
        return [
            CreateObjectAction(
                object_position=damage.target_position.set_area(
                    ObjectPositionType.CHARACTER_STATUS
                ),
                object_name="Distant Storm",
                object_arguments={},
            )
        ]

    def event_handler_ROUND_PREPARE(
        self, event: RoundPrepareEventArguments, match: Match
    ) -> list[RemoveObjectAction]:
        """
        TODO: in game, Seirai Island will disappear *after* end phase but *before*
        next round. currently there's no such event, so we use ROUND_PREPARE.
        """
        if self.position.area != "SUPPORT":
            # not in support area, do nothing
            return []
        self.usage -= 1
        return self.check_should_remove()


desc: dict[str, DescDictType] = {
    "SUPPORT/Seirai Island": {
        "names": {"en-US": "Seirai Island", "zh-CN": "清籁岛"},
        "descs": {
            "4.6": {
                "en-US": "After any character on either side is healed: That character gains Distant Storm. (Takes 2 Piercing DMG at the End Phase. Can be used once)\nDuration (Rounds): 2",  # noqa
                "zh-CN": "任意阵营的角色受到治疗后：使该角色附属悠远雷暴。（结束阶段受到2点穿透伤害，可用1次）\n持续回合：2",  # noqa
            }
        },
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Assist_Location_Qinglaidao.png",  # noqa
        "id": 321019,
    },
    "CHARACTER_STATUS/Distant Storm": {
        "names": {"en-US": "Distant Storm", "zh-CN": "悠远雷暴"},
        "descs": {
            "4.6": {
                "en-US": "Takes 2 Piercing DMG at the End Phase.\nUsage(s): 1",
                "zh-CN": "结束阶段受到2点穿透伤害\n可用次数：1",
            }
        },
    },
}


register_class(SeiraiIsland_4_6 | DistantStorm_4_6, desc)
