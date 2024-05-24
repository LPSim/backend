from typing import Literal
from lpsim.server.action import CreateObjectAction, MakeDamageAction
from lpsim.server.card.event.foods import FoodCardBase
from lpsim.server.consts import DamageType, IconType, ObjectPositionType
from lpsim.server.event import ReceiveDamageEventArguments
from lpsim.server.match import Match
from lpsim.server.modifiable_values import DamageValue
from lpsim.server.status.character_status.base import UsageCharacterStatus
from lpsim.server.struct import Cost, ObjectPosition
from lpsim.utils.class_registry import register_class
from lpsim.utils.desc_registry import DescDictType


class RainbowMacaronsStatus_4_6(UsageCharacterStatus):
    name: Literal["Rainbow Macarons"] = "Rainbow Macarons"
    version: Literal["4.6"] = "4.6"
    usage: int = 3
    max_usage: int = 3

    icon_type: IconType = IconType.HEAL

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ):
        # if this character is damaged, heal 1 HP
        if self.usage == 0:  # pragma: no cover
            # no usage
            return []
        damage = event.final_damage
        if self.position.not_satisfy(
            "both pidx=same cidx=same and target area=character",
            damage.target_position,
            match,
        ):
            # target not self character
            return []
        if damage.damage_type != DamageType.DAMAGE:
            # not damage
            return []
        self.usage -= 1
        return [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue.create_heal(
                        self.position, damage.target_position, -1, Cost()
                    )
                ]
            )
        ]


class RainbowMacarons_4_6(FoodCardBase):
    name: Literal["Rainbow Macarons"] = "Rainbow Macarons"
    version: Literal["4.6"] = "4.6"
    cost: Cost = Cost(any_dice_number=2)
    can_eat_only_if_damaged: bool = True

    def get_actions(
        self, target: ObjectPosition | None, match: Match
    ) -> list[CreateObjectAction | MakeDamageAction]:
        assert target is not None
        ret: list[CreateObjectAction | MakeDamageAction] = [
            MakeDamageAction(
                damage_value_list=[
                    DamageValue.create_heal(self.position, target, -1, Cost())
                ]
            )
        ]
        ret += super().get_actions(target, match)
        ret += [
            CreateObjectAction(
                object_name=self.name,
                object_position=target.set_area(ObjectPositionType.CHARACTER_STATUS),
                object_arguments={},
            )
        ]
        return ret


desc: dict[str, DescDictType] = {
    "CARD/Rainbow Macarons": {
        "names": {"en-US": "Rainbow Macarons", "zh-CN": "缤纷马卡龙"},
        "descs": {
            "4.6": {
                "en-US": "Heal the target character for 1 HP. The next 3 times this character takes DMG, they will also heal 1 HP afterward.\n(A character can consume at most 1 Food per Round)",  # noqa
                "zh-CN": "治疗目标角色1点，该角色接下来3次受到伤害后再治疗其1点。\n（每回合每个角色最多食用1次「料理」）",  # noqa
            }
        },
        "image_path": "https://api.ambr.top/assets/UI/gcg/UI_Gcg_CardFace_Event_Food_Macarons.png",  # noqa
        "id": 333015,
    },
    "CHARACTER_STATUS/Rainbow Macarons": {
        "names": {"en-US": "Rainbow Macarons", "zh-CN": "缤纷马卡龙"},
        "descs": {
            "4.6": {
                "en-US": "The next 3 times this character takes DMG will heal 1 HP afterward.",  # noqa
                "zh-CN": "该角色接下来3次受到伤害后治疗其1点。",  # noqa
            }
        },
    },
}


register_class(RainbowMacaronsStatus_4_6 | RainbowMacarons_4_6, desc)
