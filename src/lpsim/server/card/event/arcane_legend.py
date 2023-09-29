"""
Arcane legend cards.
"""

from typing import Any, List, Literal

from ...modifiable_values import DamageValue

from ...action import (
    ConsumeArcaneLegendAction, CreateDiceAction, CreateObjectAction, 
    MakeDamageAction
)

from ...struct import Cost, ObjectPosition
from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, CostLabels, DamageType, ElementType, 
    ObjectPositionType, ObjectType
)
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


class AncientCourtyard(ArcaneLegendBase):
    name: Literal['Ancient Courtyard']
    desc: str = (
        'You must have a character who has already equipped a Weapon or '
        'Artifact: The next time you play a Weapon or Artifact card in this '
        'Round: Spend 2 less Elemental Dice.'
    )
    version: Literal['3.8'] = '3.8'
    cost: Cost = Cost(arcane_legend = True)

    def is_valid(self, match: Any) -> bool:
        """
        You must have a character who has already equipped a Weapon or Artifact
        """
        for charactor in match.player_tables[
                self.position.player_idx].charactors:
            if charactor.weapon is not None or charactor.artifact is not None:
                return True
        return False

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        No targets.
        """
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ConsumeArcaneLegendAction | CreateObjectAction]:
        """
        create team status
        """
        assert target is None
        ret: List[ConsumeArcaneLegendAction | CreateObjectAction] = []
        ret += super().get_actions(target, match)
        ret.append(CreateObjectAction(
            object_name = self.name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectType.TEAM_STATUS,
                id = 0,
            ),
            object_arguments = {}
        ))
        return ret


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


class JoyousCelebration(ArcaneLegendBase):
    name: Literal['Joyous Celebration']
    desc: str = (
        'Your active character must be one of the following elemental types '
        'to play this card: Cryo/Hydro/Pyro/Electro/Dendro: The element '
        'corresponding to your active character\'s Elemental Type will be '
        'applied to all your characters.'
    )
    version: Literal['3.8'] = '3.8'
    cost: Cost = Cost(arcane_legend = True)

    def is_valid(self, match: Any) -> bool:
        """
        Your active character must be one of the following elemental types to
        play this card: Cryo/Hydro/Pyro/Electro/Dendro
        """
        charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        return charactor.element in [
            ElementType.CRYO, ElementType.HYDRO, ElementType.PYRO,
            ElementType.ELECTRO, ElementType.DENDRO
        ]

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        No targets.
        """
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ConsumeArcaneLegendAction | MakeDamageAction]:
        """
        apply element to all your characters.
        """
        assert target is None
        ret: List[ConsumeArcaneLegendAction | MakeDamageAction] = []
        ret += super().get_actions(target, match)
        damage_action = MakeDamageAction(
            source_player_idx = self.position.player_idx,
            target_player_idx = self.position.player_idx,
            damage_value_list = [
            ],
        )
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        element = active_charactor.element
        for c in match.player_tables[self.position.player_idx].charactors:
            if c.is_defeated:
                continue
            damage_action.damage_value_list.append(
                DamageValue(
                    position = self.position,
                    damage_type = DamageType.ELEMENT_APPLICATION,
                    target_position = c.position,
                    damage = 0,
                    damage_elemental_type = ELEMENT_TO_DAMAGE_TYPE[element],
                    cost = self.cost.copy(),
                )
            )
        return ret + [damage_action]


class FreshWindOfFreedom(ArcaneLegendBase):
    name: Literal['Fresh Wind of Freedom']
    desc: str = (
        'In this Round, when an opposing character is defeated during your '
        'Action, you can continue to act again when that Action ends.'
    )
    version: Literal['4.1'] = '4.1'
    cost: Cost = Cost(arcane_legend = True)

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ConsumeArcaneLegendAction | CreateObjectAction]:
        """
        Create Wind and Freedom team status.
        """
        assert target is None
        return super().get_actions(target, match) + [
            CreateObjectAction(
                object_name = self.name,
                object_position = ObjectPosition(
                    player_idx = self.position.player_idx,
                    area = ObjectPositionType.TEAM_STATUS,
                    id = -1,
                ),
                object_arguments = {},
            )
        ]


ArcaneLegendCards = (
    AncientCourtyard | CovenantOfRock | JoyousCelebration
    | FreshWindOfFreedom
)
