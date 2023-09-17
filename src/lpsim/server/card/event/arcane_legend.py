"""
Arcane legend cards.
"""

from typing import Any, List, Literal

from ...action import ConsumeArcaneLegendAction, CreateDiceAction

from ...struct import Cost, ObjectPosition
from ...consts import CostLabels, ObjectType
from ...object_base import CardBase


class ArcaneLegendBase(CardBase):
    type: Literal[ObjectType.ARCANE] = ObjectType.ARCANE
    cost_label: int = CostLabels.CARD.value | CostLabels.ARCANE.value

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ConsumeArcaneLegendAction]:
        """
        Consume arcane legend.
        """
        assert target is None
        return [ConsumeArcaneLegendAction(
            player_idx = self.position.player_idx
        )]


class CovenantOfRock(ArcaneLegendBase):
    name: Literal['Covenant of Rock']
    desc: str = (
        'Can only be played when you have 0 Elemental Dice left: '
        'Generate 2 different Elemental Dice.'
    )
    version: Literal['3.8'] = '3.8'
    cost: Cost = Cost(arcane_legend = True)

    def is_valid(self, match: Any) -> bool:
        """
        Can only be played when you have 0 Elemental Dice left.
        """
        return len(match.player_tables[
            self.position.player_idx].dice.colors) == 0

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        No targets.
        """
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ConsumeArcaneLegendAction | CreateDiceAction]:
        """
        Generate 2 different Elemental Dice.
        """
        assert target is None
        ret: List[ConsumeArcaneLegendAction | CreateDiceAction] = []
        ret += super().get_actions(target, match)
        ret.append(CreateDiceAction(
            player_idx = self.position.player_idx,
            number = 2,
            different = True
        ))
        return ret


ArcaneLegendCards = CovenantOfRock | CovenantOfRock
