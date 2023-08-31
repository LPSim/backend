from typing import Any, List, Literal

from ...action import CreateObjectAction
from ...struct import Cost, ObjectPosition
from ...consts import CostLabels, ObjectPositionType
from ...object_base import CardBase


class FoodCardBase(CardBase):
    """
    Base class for food cards.
    """
    cost_label: int = CostLabels.CARD | CostLabels.FOOD
    can_eat_only_if_damaged: bool

    def eat_target(self, match: Any) -> List[int]:
        """
        Get target charactor idxs that can eat.
        """
        ret: List[int] = []
        table = match.player_tables[self.position.player_idx]
        for idx, charactor in enumerate(table.charactors):
            if charactor.is_defeated:
                continue
            is_full = False
            for status in charactor.status:
                if status.name == 'Satiated':
                    is_full = True
                    break
            if is_full:
                continue
            if self.can_eat_only_if_damaged and charactor.damage_taken <= 0:
                continue
            ret.append(idx)
        return ret

    def is_valid(self, match: Any) -> bool:
        """
        If there is at least one target that can eat.
        """
        return len(self.eat_target(match)) > 0

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        Get targets of this card.
        """
        ret: List[ObjectPosition] = []
        for idx in self.eat_target(match):
            ret.append(ObjectPosition(
                player_idx = self.position.player_idx,
                charactor_idx = idx,
                area = ObjectPositionType.CHARACTOR,
                id = -1,
            ))
        return ret

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Add Satiated status to target charactor.
        """
        assert target is not None
        pos = target.copy()
        pos.area = ObjectPositionType.CHARACTOR_STATUS
        return [CreateObjectAction(
            object_name = 'Satiated',
            object_position = pos,
            object_arguments = {}
        )]


class AdeptusTemptation(FoodCardBase):
    name: Literal["Adeptus' Temptation"]
    desc: str = (
        "During this Round, the target character's next Elemental Burst "
        "deals +3 DMG."
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(any_dice_number = 2)

    can_eat_only_if_damaged: bool = False

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        ret = super().get_actions(target, match)
        assert len(ret) == 1
        action_2 = ret[0].copy(deep = True)
        action_2.object_name = self.name
        ret.append(action_2)
        return ret


FoodCards = AdeptusTemptation | AdeptusTemptation
