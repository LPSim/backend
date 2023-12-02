"""
Arcane legend cards.
"""

from typing import Any, List, Literal

from ...event import UseCardEventArguments

from ....utils.class_registry import register_class

from ...modifiable_values import DamageValue

from ...action import (
    Actions, ConsumeArcaneLegendAction, CreateDiceAction, CreateObjectAction, 
    DrawCardAction, MakeDamageAction, RemoveCardAction
)

from ...struct import Cost, MultipleObjectPosition, ObjectPosition
from ...consts import (
    ELEMENT_TO_DAMAGE_TYPE, CostLabels, DamageType, ElementType, 
    ObjectPositionType, ObjectType
)
from ...object_base import EventCardBase


class ArcaneLegendBase(EventCardBase):
    type: Literal[ObjectType.ARCANE] = ObjectType.ARCANE
    cost_label: int = (
        CostLabels.CARD.value | CostLabels.ARCANE.value
        | CostLabels.EVENT.value
    )

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

    def event_handler_USE_CARD(
        self, event: UseCardEventArguments, match: Any
    ) -> List[Actions]:
        """
        Mainly copied from CardBase with modifications with use_card_success.

        If this card is used, trigger events. But if not use_card_success,
        instead of do nothing, will consume arcane legend.
        """
        actions: List[Actions] = []
        if event.action.card_position.id != self.id:
            # not this card
            return actions
        if self.remove_when_used:  # pragma: no branch
            actions.append(RemoveCardAction(
                position = ObjectPosition(
                    player_idx = self.position.player_idx,
                    area = ObjectPositionType.HAND,
                    id = self.id,
                ),
                remove_type = 'USED',
            ))
        # target is None, otherwise should match class
        assert (
            event.action.target is None
            or (
                isinstance(event.action.target, MultipleObjectPosition)
                == self.target_position_type_multiple
            )
        )
        if event.use_card_success:
            # use success, add actions of the card
            actions += self.get_actions(
                target = event.action.target,  # type: ignore
                match = match,
            )
        else:
            # use failed, only consume arcane legend
            actions += [ConsumeArcaneLegendAction(
                player_idx = self.position.player_idx
            )]
        return actions


class AncientCourtyard_3_8(ArcaneLegendBase):
    name: Literal['Ancient Courtyard']
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


class CovenantOfRock_3_8(ArcaneLegendBase):
    name: Literal['Covenant of Rock']
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


class JoyousCelebration_4_2(ArcaneLegendBase):
    name: Literal['Joyous Celebration']
    version: Literal['4.2'] = '4.2'
    cost: Cost = Cost(
        same_dice_number = 1,
        arcane_legend = True
    )
    apply_no_element_charactor: bool = False

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
        apply element to corresponding characters.
        """
        assert target is None
        ret: List[ConsumeArcaneLegendAction | MakeDamageAction] = []
        ret += super().get_actions(target, match)
        damage_action = MakeDamageAction(
            damage_value_list = [],
        )
        active_charactor = match.player_tables[
            self.position.player_idx].get_active_charactor()
        element = active_charactor.element
        for c in match.player_tables[self.position.player_idx].charactors:
            if c.is_defeated:
                continue
            if (
                (not self.apply_no_element_charactor) 
                and len(c.element_application) == 0
            ):
                # not apply to no element charactor
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
        if len(damage_action.damage_value_list) > 0:
            ret.append(damage_action)
        return ret


class JoyousCelebration_4_0(JoyousCelebration_4_2):
    version: Literal['4.0'] = '4.0'
    apply_no_element_charactor: bool = True


class FreshWindOfFreedom_4_1(ArcaneLegendBase):
    name: Literal['Fresh Wind of Freedom']
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


class InEveryHouseAStove_4_2(ArcaneLegendBase):
    name: Literal['In Every House a Stove']
    version: Literal['4.2'] = '4.2'
    cost: Cost = Cost(arcane_legend = True)

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[ConsumeArcaneLegendAction | DrawCardAction]:
        """
        Draw cards.
        """
        assert target is None
        return super().get_actions(target, match) + [
            DrawCardAction(
                player_idx = self.position.player_idx,
                number = min(match.round_number, 4),
                draw_if_filtered_not_enough = True
            )
        ]


register_class(
    AncientCourtyard_3_8 | CovenantOfRock_3_8 | JoyousCelebration_4_2
    | FreshWindOfFreedom_4_1 | InEveryHouseAStove_4_2 | JoyousCelebration_4_0
)
