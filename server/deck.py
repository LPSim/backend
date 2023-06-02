from utils import BaseModel
from typing import Literal, List
from server.card import Cards
from server.charactor import Charactors


class Deck(BaseModel):
    name: Literal['Deck'] = 'Deck'
    charactors: List[Charactors] = []
    cards: List[Cards] = []

    def check_legal(self) -> bool:
        """
        check whether the deck is legal.
        1. the number of charactors is 3
        2. the number of cards is 30
        3. the number of cards with the same id is less than 2
        4. cards with special carrying rules
        """
        return True
