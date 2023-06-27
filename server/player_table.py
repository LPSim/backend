from utils import BaseModel
from typing import Literal, List
from resources.consts import CharactorIcons
from server.deck import Deck
from server.charactor import Charactors
from server.card import Cards
from server.summon import Summons
from server.support import Supports
from server.buff import Buffs


class PlayerTable(BaseModel):
    """
    Represents the player's table, which contains information about the 
    player's deck information and current state of the table.

    Attributes:
        name (str): class name.
        player_name (str): The name of the player.
        player_icon (CharactorIcons): The icon of the player's character.
        player_deck_information (Deck): The description of the player's deck.

        front_charactor_id (int): The ID of the front character.
        has_round_ended (bool): Whether the player has declared that the
            round has ended.
        team_buffs (List[Buffs]): The list of buffs applied to the team.
        charactors (List[Charactors]): The list of characters on the table.
        summons (List[Summons]): The list of summons on the table.
        supports (List[Supports]): The list of supports on the table.
        hands (List[Cards]): The list of cards in the player's hand.
        table_deck (List[Cards]): The list of cards in the table deck.
    """
    name: Literal['PlayerTable'] = 'PlayerTable'

    # player information
    player_name: str = 'Nahida'
    player_icon: CharactorIcons = CharactorIcons.NAHIDA
    player_deck_information: Deck = Deck()

    # table information
    front_charactor_id: int = -1
    has_round_ended: bool = False
    team_buffs: List[Buffs] = []
    charactors: List[Charactors] = []
    summons: List[Summons] = []
    supports: List[Supports] = []
    hands: List[Cards] = []
    table_deck: List[Cards] = []
