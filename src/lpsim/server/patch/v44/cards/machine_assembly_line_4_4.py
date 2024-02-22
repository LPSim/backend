from typing import Dict, List, Literal
from pydantic import PrivateAttr

from ....action import Actions, CreateObjectAction
from ....modifiable_values import CostValue
from ....event import ReceiveDamageEventArguments
from ....status.character_status.base import CharacterStatusBase
from ....consts import CostLabels, DamageType, IconType, ObjectPositionType
from ....match import Match
from ....struct import Cost, ObjectPosition
from ....object_base import EventCardBase
from .....utils.class_registry import register_class
from .....utils.desc_registry import DescDictType


class MachineAssemblyLineStatus_4_4(CharacterStatusBase):
    name: Literal["Machine Assembly Line"] = "Machine Assembly Line"
    version: Literal["4.4"] = "4.4"
    usage: int = 0
    max_usage: int = 2
    _card_cost_label: int = PrivateAttr(
        CostLabels.ARTIFACT.value | CostLabels.WEAPON.value
    )
    icon_type: Literal[IconType.SPECIAL] = IconType.SPECIAL

    def event_handler_RECEIVE_DAMAGE(
        self, event: ReceiveDamageEventArguments, match: Match
    ) -> List[Actions]:
        if not event.final_damage.is_corresponding_character_receive_damage(
            self.position, match, ignore_piercing=False
        ):
            # not self receive damage
            if not (
                event.final_damage.damage_type == DamageType.HEAL
                and self.position.check_position_valid(
                    event.final_damage.target_position,
                    match,
                    player_idx_same=True,
                    character_idx_same=True,
                )
            ):
                # and not heal self
                return []
        # add usage
        self.usage = min(self.usage + 1, self.max_usage)
        return []

    def value_modifier_COST(
        self, value: CostValue, match: Match, mode: Literal["TEST", "REAL"]
    ) -> CostValue:
        """
        When self equip weapon or artifact with cost fewer than usage
        """
        if not (
            value.position.player_idx == self.position.player_idx
            and value.cost.original_value is not None
            and value.cost.original_value.total_dice_cost <= self.usage
            and value.cost.label & self._card_cost_label != 0
        ):
            # not self, or original usage larger than self usage, or not weapon
            # or artifact
            return value
        total_cost = value.cost.total_dice_cost
        if total_cost == 0:
            # cost is 0, do nothing
            return value
        for _ in range(total_cost):
            value.cost.decrease_cost(None)
        if mode == "REAL":
            self.usage = 0
        return value


class MachineAssemblyLine_4_4(EventCardBase):
    name: Literal["Machine Assembly Line"]
    version: Literal["4.4"] = "4.4"
    cost: Cost = Cost()

    def get_targets(self, match: Match) -> List[ObjectPosition]:
        # can quip on all self alive characters
        ret: List[ObjectPosition] = []
        for character in match.player_tables[self.position.player_idx].characters:
            if character.is_alive:
                ret.append(character.position)
        return ret

    def get_actions(
        self, target: ObjectPosition | None, match: Match
    ) -> List[CreateObjectAction]:
        assert target is not None
        return [
            CreateObjectAction(
                object_name=self.name,
                object_position=target.set_area(ObjectPositionType.CHARACTER_STATUS),
                object_arguments={},
            )
        ]


desc: Dict[str, DescDictType] = {
    "CHARACTER_STATUS/Machine Assembly Line": {
        "names": {"en-US": "Machine Assembly Line", "zh-CN": "机关铸成之链"},
        "descs": {
            "4.4": {
                "en-US": "Each time after this character is targeted by and takes DMG or is healed: Accumulate 1 point of Battle-Readiness (Max 2 points).\nWhen you play a Weapon or Artifact with an original cost of fewer Dice than you have Battle-Readiness points: Clear all Battle-Readiness points and play that card for free.",  # noqa: E501
                "zh-CN": "该角色每次受到伤害或治疗后：累积1点「备战度」（最多累积2点）。\n我方打出原本费用不多于「备战度」的「武器」或「圣遗物」时：移除所有「备战度」，以免费打出该牌。",  # noqa: E501
            }
        },
    },
    "CARD/Machine Assembly Line": {
        "names": {"en-US": "Machine Assembly Line", "zh-CN": "机关铸成之链"},
        "descs": {
            "4.4": {
                "en-US": "Each time after your character is targeted by and takes DMG or is healed: Accumulate 1 point of Battle-Readiness (Max 2 points).\nWhen you play a Weapon or Artifact with an original cost of fewer Dice than you have Battle-Readiness points: Clear all Battle-Readiness points and play that card for free.",  # noqa: E501
                "zh-CN": "目标我方角色每次受到伤害或治疗后：累积1点「备战度」（最多累积2点）。\n我方打出原本费用不多于「备战度」的「武器」或「圣遗物」时：移除所有「备战度」，以免费打出该牌。",  # noqa: E501
            }
        },
        "image_path": "cardface/Event_Event_Fatiaoji.png",  # noqa: E501
        "id": 332028,
    },
}


register_class(MachineAssemblyLineStatus_4_4 | MachineAssemblyLine_4_4, desc)
