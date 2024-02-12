from typing import Dict, List, Literal

from .....utils.class_registry import register_class
from ....modifiable_values import DamageValue
from ....action import ActionTypes, CreateObjectAction, MakeDamageAction
from ....consts import DamageElementalType, DamageType, IconType
from ....status.character_status.base import RoundEndAttackCharacterStatus
from ....match import Match
from ....struct import Cost, ObjectPosition
from ....card.event.foods import FoodCardBase
from .....utils.desc_registry import DescDictType


class MatsutakeMeatRollsStatus_4_4(RoundEndAttackCharacterStatus):
    name: Literal["Matsutake Meat Rolls"] = "Matsutake Meat Rolls"
    version: Literal["4.4"] = "4.4"
    usage: int = 3
    max_usage: int = 3
    icon_type: Literal[IconType.HEAL] = IconType.HEAL
    damage: int = -1
    damage_elemental_type: DamageElementalType = DamageElementalType.HEAL


class MatsutakeMeatRolls_4_4(FoodCardBase):
    name: Literal["Matsutake Meat Rolls"]
    version: Literal["4.4"] = "4.4"
    cost: Cost = Cost(same_dice_number=2)

    can_eat_only_if_damaged: bool = True

    def get_actions(
        self, target: ObjectPosition | None, match: Match
    ) -> List[CreateObjectAction | MakeDamageAction]:
        ret: List[CreateObjectAction | MakeDamageAction] = []
        ret = list(super().get_actions(target, match))
        assert len(ret) == 1
        assert target is not None
        ret.append(
            MakeDamageAction(
                damage_value_list=[
                    DamageValue(
                        position=self.position,
                        damage_type=DamageType.HEAL,
                        target_position=target,
                        damage=-2,
                        damage_elemental_type=DamageElementalType.HEAL,
                        cost=self.cost.copy(),
                    )
                ],
            )
        )
        create_1 = ret[0]
        assert create_1.type == ActionTypes.CREATE_OBJECT
        ret.append(
            CreateObjectAction(
                object_name=self.name,
                object_position=create_1.object_position,
                object_arguments={},
            )
        )
        return ret


desc: Dict[str, DescDictType] = {
    "CHARACTER_STATUS/Matsutake Meat Rolls": {
        "names": {"en-US": "Matsutake Meat Rolls", "zh-CN": "松茸酿肉卷"},
        "descs": {
            "4.4": {
                "en-US": "For the next 3 Rounds, heal this character for 1 HP again during the End Phase. (Usages: 3)",  # noqa: E501
                "zh-CN": "结束阶段治疗此角色1点。（可用次数：3）",  # noqa: E501
            }
        },
    },
    "CARD/Matsutake Meat Rolls": {
        "names": {"en-US": "Matsutake Meat Rolls", "zh-CN": "松茸酿肉卷"},
        "descs": {
            "4.4": {
                "en-US": "Heal the target character for 2 HP. For the next 3 Rounds, heal this character for 1 HP again during the End Phase.\n(A character can consume at most 1 Food per Round)",  # noqa: E501
                "zh-CN": "治疗目标角色2点，3回合内的结束阶段再治疗此角色1点。\n（每回合每个角色最多食用1次「料理」）",  # noqa: E501
            }
        },
        "image_path": "cardface/Event_Food_Matsutake.png",  # noqa: E501
        "id": 333014,
    },
}


register_class(MatsutakeMeatRolls_4_4 | MatsutakeMeatRollsStatus_4_4, desc)
