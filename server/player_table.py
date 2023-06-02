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
    """
    name: Literal['PlayerTable'] = 'PlayerTable'

    # player information
    player_name: str = 'Nahida'
    player_icon: CharactorIcons = CharactorIcons.NAHIDA
    deck: Deck = Deck()

    # table information
    front_charactor_id: int = -1
    has_round_ended: bool = False
    team_buffs: List[Buffs] = []
    charactors: List[Charactors] = []
    summons: List[Summons] = []
    supports: List[Supports] = []
    hands: List[Cards] = []

    # TODO how to solve abstract class problem with pydantic
