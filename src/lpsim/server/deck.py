import logging

from pydantic import validator

from .object_base import CardBases

from .charactor.charactor_base import CharactorBase

from ..utils import BaseModel, get_instance_from_type_unions
from typing import Literal, List
from . import Cards
from . import Charactors


class Deck(BaseModel):
    name: Literal['Deck'] = 'Deck'
    charactors: List[CharactorBase] = []
    cards: List[CardBases] = []

    @validator('charactors', each_item = True, pre = True)
    def parse_charactors(cls, v):
        return get_instance_from_type_unions(Charactors, v)

    @validator('cards', each_item = True, pre = True)
    def parse_cards(cls, v):
        return get_instance_from_type_unions(Cards, v)

    def check_legal(self, card_number: int | None, 
                    max_same_card_number: int | None, 
                    charactor_number: int | None,
                    check_restriction: bool) -> bool:
        """
        check whether the deck is legal.
        1. the number of charactors
        2. the number of cards
        3. the number of cards with the same name
        4. cards with special carrying rules
        """
        if charactor_number is not None:
            if len(self.charactors) != charactor_number:
                logging.error(f'charactor number should be {charactor_number}')
                return False
        if card_number is not None:
            if len(self.cards) != card_number:
                logging.error(f'card number should be {card_number}')
                return False
        if max_same_card_number is not None:
            card_names = [c.name for c in self.cards]
            for card in card_names:
                if card_names.count(card) > max_same_card_number:
                    logging.error(
                        f'card {card} should not be more than '
                        f'{max_same_card_number} in deck'
                    )
                    return False
        if check_restriction:
            for card in self.cards:
                restriction = card.get_deck_restriction()
                if restriction.type == 'NONE':
                    continue
                elif restriction.type == 'FACTION':
                    counter = 0
                    for charactor in self.charactors:
                        if restriction.name in charactor.faction:
                            counter += 1
                    if counter < restriction.number:
                        logging.error(
                            f'to use card {card.name}, '
                            f'charactor number of faction {restriction.name} '
                            f'should be at least {restriction.number}'
                        )
                        return False
                elif restriction.type == 'CHARACTOR':
                    counter = 0
                    for charactor in self.charactors:
                        if restriction.name == charactor.name:
                            counter += 1
                    if counter < restriction.number:
                        logging.error(
                            f'to use card {card.name}, '
                            f'charactor number of name {restriction.name} '
                            f'should be at least {restriction.number}'
                        )
                        return False
                elif restriction.type == 'ELEMENT':
                    counter = 0
                    for charactor in self.charactors:
                        if restriction.name == charactor.element.value:
                            counter += 1
                    if counter < restriction.number:
                        logging.error(
                            f'to use card {card.name}, '
                            f'charactor number of element {restriction.name} '
                            f'should be at least {restriction.number}'
                        )
                        return False
                else:
                    raise NotImplementedError(
                        f'restriction type {restriction.type} not implemented'
                    )
        return True

    @staticmethod
    def from_str(deck_str: str) -> 'Deck':
        """
        Convert deck string to deck object. One line contains one command, 
        card or charactor. 

        To specify default versions for all cards that don't have version
        specified, use 'default_version:version'. If not set, cards without
        version information will not have version in its argument. This line
        must appear before any other lines.

        If declare a charactor, use 'charactor:'. Otherwise 
        write card name directly. 

        To specify different version of cards, add `@version` after the
        line.

        To declare multiple same cards or charactors, add `*number` after 
        the line. When both marks are used, specify version first.
        You can write comment line start with '#'.

        Examples:

        default_version:4.0
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        # you can write comment line with '#'
        Timmie*15
        Rana*15

        """
        deck_str = deck_str.strip()
        deck = Deck()
        default_version: str | None = None
        for line in deck_str.split('\n'):
            line = line.strip()
            if line == '':
                continue
            if line.startswith('default_version:'):
                default_version = line[16:]
                continue
            if line[0] == '#':
                # comment line
                continue
            # deal with numbers
            if '*' in line:
                line, number = line.split('*')
                number = int(number)
            else:
                number = 1
            # deal with version
            if '@' in line:
                line, version = line.split('@')
                version = version.strip()
            else:
                version = default_version
            if line.startswith('charactor:'):
                args = { 'name': line[10:] }
                if version is not None:
                    args['version'] = version
                for _ in range(number):
                    deck.charactors.append(
                        get_instance_from_type_unions(
                            Charactors, args
                        )
                    )
            else:
                for _ in range(number):
                    args = { 'name': line }
                    if version is not None:
                        args['version'] = version
                    deck.cards.append(
                        get_instance_from_type_unions(
                            Cards, args
                        )
                    )
        return deck

    def to_str(self) -> str:
        """
        Convert deck object to deck string.
        """
        deck_str = ''
        for charactor in self.charactors:
            deck_str += f'charactor:{charactor.name}'
            deck_str += f'@{charactor.version}'
            deck_str += '\n'
        for card in self.cards:
            deck_str += card.name
            deck_str += f'@{card.version}'
            deck_str += '\n'
        return deck_str
