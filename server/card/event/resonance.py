

from typing import Any, List, Literal
from server.action import CreateDiceAction, CreateObjectAction
from ...consts import ELEMENT_TO_DIE_COLOR, ElementType, ObjectPositionType

from server.struct import ObjectPosition
from ...object_base import CardBase
from ...struct import Cost


class ElementalResonanceCardBase(CardBase):
    pass


name_to_element_type = {
    'Elemental Resonance: Woven Flames': ElementType.PYRO,
    'Elemental Resonance: Woven Ice': ElementType.CRYO,
    'Elemental Resonance: Woven Stone': ElementType.GEO,
    'Elemental Resonance: Woven Thunder': ElementType.ELECTRO,
    'Elemental Resonance: Woven Waters': ElementType.HYDRO,
    'Elemental Resonance: Woven Weeds': ElementType.DENDRO,
    'Elemental Resonance: Woven Winds': ElementType.ANEMO,
}


class WovenCards(ElementalResonanceCardBase):
    name: Literal[
        'Elemental Resonance: Woven Flames', 
        'Elemental Resonance: Woven Ice',
        'Elemental Resonance: Woven Stone', 
        'Elemental Resonance: Woven Thunder',
        'Elemental Resonance: Woven Waters',
        'Elemental Resonance: Woven Weeds',
        'Elemental Resonance: Woven Winds'
    ]
    desc: str = '''Create 1 XXX Die.'''
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost()
    element: ElementType = ElementType.NONE

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.element = name_to_element_type[self.name]
        self.desc = self.desc.replace('XXX', self.element.name.capitalize())

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateDiceAction]:
        """
        Create one corresponding element dice
        """
        return [CreateDiceAction(
            player_idx = self.position.player_idx,
            color = ELEMENT_TO_DIE_COLOR[self.element],
            number = 1,
        )]


class NationResonanceCardBase(CardBase):
    pass


class WindAndFreedom(NationResonanceCardBase):
    name: Literal['Wind and Freedom']
    desc: str = (
        'In this Round, when an opposing character is defeated during your '
        'Action, you can continue to act again when that Action ends. '
        'Usage(s): 1 '
        '(You must have at least 2 Mondstadt characters in your deck to add '
        'this card to your deck.)'
    )
    version: Literal['3.7'] = '3.7'
    cost: Cost = Cost(same_dice_number = 1)

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Create Wind and Freedom team status.
        """
        assert target is None
        return [CreateObjectAction(
            object_name = 'Wind and Freedom',
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1,
            ),
            object_arguments = {},
        )]


ElementResonanceCards = WovenCards | WovenCards
NationResonanceCards = WindAndFreedom | WindAndFreedom
