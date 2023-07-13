from utils import BaseModel
from typing import Literal, List
from resources.consts import CharactorIcons
from .consts import DieColor, ELEMENT_TO_DIE_COLOR, ELEMENT_DEFAULT_ORDER
from .deck import Deck
from .card import Cards
from .die import Die
from .summon import Summons
from .support import Supports
from .charactor import Charactors
from .status import TeamStatus


class PlayerTable(BaseModel):
    """
    Represents the player's table, which contains information about the 
    player's deck information and current state of the table.

    Attributes:
        name (str): class name.
        player_name (str): The name of the player.
        player_icon (CharactorIcons): The icon of the player's character.
        player_deck_information (Deck): The description of the player's deck.

        active_charactor_id (int): The ID of the active character.
        has_round_ended (bool): Whether the player has declared that the
            round has ended.
        dice (List[Dice]): The list of dice on the table.
        team_status (List[Buffs]): The list of status applied to the team.
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
    active_charactor_id: int = -1
    has_round_ended: bool = False
    dice: List[Die] = []
    team_status: List[TeamStatus] = []
    charactors: List[Charactors] = []
    summons: List[Summons] = []
    supports: List[Supports] = []
    hands: List[Cards] = []
    table_deck: List[Cards] = []

    def dice_color_order(self) -> List[DieColor]:
        """
        Returns the order of dice colors.
        """
        result: List[DieColor] = [DieColor.OMNI]
        if self.active_charactor_id != -1:
            c_element = self.charactors[self.active_charactor_id].element
            color = ELEMENT_TO_DIE_COLOR[c_element]
            result.append(color)
        for charactor in self.charactors:
            c_element = charactor.element
            color = ELEMENT_TO_DIE_COLOR[c_element]
            if color not in result:
                result.append(color)
        for element in ELEMENT_DEFAULT_ORDER:
            color = ELEMENT_TO_DIE_COLOR[element]
            if color not in result:
                result.append(color)
        return result

    def sort_dice(self):
        """
        Sorts the dice on the table.
        """
        order = self.dice_color_order()
        self.dice.sort(key=lambda x: order.index(x.color))

    def dice_colors_to_dice_ids(self):
        """
        Returns a dictionary mapping dice colors to dice IDs.
        """
        result = {}
        for i, die in enumerate(self.dice):
            result[die.color] = i
        return result
