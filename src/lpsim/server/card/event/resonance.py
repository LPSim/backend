

from typing import Any, List, Literal

from ...action import CreateDiceAction, CreateObjectAction
from ...consts import (
    ELEMENT_TO_DIE_COLOR, DieColor, ElementType, FactionType, 
    ObjectPositionType
)

from ...object_base import CardBase
from ...struct import Cost, DeckRestriction, ObjectPosition


class ElementalResonanceCardBase(CardBase):
    element: ElementType

    def get_deck_restriction(self) -> DeckRestriction:
        """
        For element resonance cards, should contain at least 2 charactors of
        the corresponding element.
        """
        return DeckRestriction(
            type = 'ELEMENT',
            name = self.element.value,
            number = 2
        )


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
    element: ElementType = ElementType.NONE  # will update element in __init__

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


class EnduringRock(ElementalResonanceCardBase):
    name: Literal[
        'Elemental Resonance: Enduring Rock'
    ] = 'Elemental Resonance: Enduring Rock'
    desc: str = (
        'During this round, after your character deals Geo DMG next time: '
        'Should there be any Combat Status on your side that provides Shield, '
        'grant one such Status with 3 Shield points.'
    )
    version: Literal['3.3'] = '3.3'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.GEO,
        elemental_dice_number = 1
    )
    element: ElementType = ElementType.GEO

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        # no targets
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[CreateObjectAction]:
        """
        Create status
        """
        return [CreateObjectAction(
            object_name = self.name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1,
            ),
            object_arguments = {}
        )]


class NationResonanceCardBase(CardBase):
    faction: FactionType

    def get_deck_restriction(self) -> DeckRestriction:
        """
        For nation resonance cards, should contain at least 2 charactors of
        the corresponding faction.
        """
        return DeckRestriction(
            type = 'FACTION',
            name = self.faction.value,
            number = 2
        )


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
    faction: FactionType = FactionType.MONDSTADT

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
            object_name = self.name,
            object_position = ObjectPosition(
                player_idx = self.position.player_idx,
                area = ObjectPositionType.TEAM_STATUS,
                id = -1,
            ),
            object_arguments = {},
        )]


ElementResonanceCards = WovenCards | EnduringRock
NationResonanceCards = WindAndFreedom | WindAndFreedom
