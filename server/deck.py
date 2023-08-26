import logging

from utils import BaseModel
from typing import Literal, List
from . import Cards
from . import Charactors


class Deck(BaseModel):
    name: Literal['Deck'] = 'Deck'
    charactors: List[Charactors] = []
    cards: List[Cards] = []

    def check_legal(self, card_number: int | None, 
                    max_same_card_number: int | None, 
                    charactor_number: int | None) -> bool:
        """
        check whether the deck is legal.
        1. the number of charactors
        2. the number of cards
        3. the number of cards with the same id
        4. cards with special carrying rules  # TODO
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
        return True
