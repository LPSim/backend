"""
Arcane legend cards.
"""

from typing import Any, List, Literal

from server.action import ConsumeArcaneLegendAction, CreateDiceAction
from server.struct import CardActionTarget

from ...struct import Cost
from ...consts import CostLabels, ObjectType
from ...object_base import CardBase


class ArcaneLegendBase(CardBase):
    type: Literal[ObjectType.ARCANE] = ObjectType.ARCANE
    cost_label: int = CostLabels.CARD.value | CostLabels.ARCANE.value

    def get_actions(
        self, target: CardActionTarget | None, match: Any
    ) -> List[ConsumeArcaneLegendAction]:
        """
        Consume arcane legend.
        """
        assert target is None
        return [ConsumeArcaneLegendAction(
            player_id = self.position.player_id
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
            self.position.player_id].dice.colors) == 0

    def get_targets(self, match: Any) -> List[CardActionTarget]:
        """
        No targets.
        """
        return []

    def get_actions(
        self, target: CardActionTarget | None, match: Any
    ) -> List[ConsumeArcaneLegendAction | CreateDiceAction]:
        """
        Generate 2 different Elemental Dice.
        """
        assert target is None
        ret: List[ConsumeArcaneLegendAction | CreateDiceAction] = []
        ret += super().get_actions(target, match)
        ret.append(CreateDiceAction(
            player_id = self.position.player_id,
            number = 2,
            different = True
        ))
        return ret


ArcaneLegendCards = CovenantOfRock | CovenantOfRock
