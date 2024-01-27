from pydantic import validator

from .card.support.base import SupportBase

from .summon.base import SummonBase

from .character.character_base import CharacterBase

from .status.team_status.base import TeamStatusBase
from .struct import ObjectPosition
from ..utils import BaseModel, get_instance
from typing import Literal, List, Tuple
from ..resources.consts import CharacterIcons
from .consts import (
    DieColor,
    ELEMENT_TO_DIE_COLOR,
    ELEMENT_DEFAULT_ORDER,
    ObjectPositionType,
)
from .object_base import CardBase, ObjectBase
from .deck import Deck
from .dice import Dice


class PlayerTable(BaseModel):
    """
    Represents the player's table, which contains information about the
    player's deck information and current state of the table.

    Attributes:
        name (str): class name.
        player_name (str): The name of the player.
        player_icon (CharacterIcons): The icon of the player's character.
        player_deck_information (Deck): The description of the player's deck.

        active_character_idx (int): The index of the active character.
        has_round_ended (bool): Whether the player has declared that the
            round has ended.
        dice (List[Dice]): The list of dice on the table.
        team_status (List[Buffs]): The list of status applied to the team.
        characters (List[Characters]): The list of characters on the table.
        summons (List[Summons]): The list of summons on the table.
        supports (List[Supports]): The list of supports on the table.
        hands (List[Cards]): The list of cards in the player's hand.
        table_deck (List[Cards]): The list of cards in the table deck.
    """

    name: Literal["PlayerTable"] = "PlayerTable"
    version: Literal["0.0.1", "0.0.2", "0.0.3", "0.0.4"]

    # player information
    player_name: str = "Nahida"
    player_icon: CharacterIcons = CharacterIcons.NAHIDA
    player_deck_information: Deck = Deck()

    # table information
    player_idx: int
    active_character_idx: int = -1
    has_round_ended: bool = False
    dice: Dice = Dice()
    team_status: List[TeamStatusBase] = []
    characters: List[CharacterBase] = []
    summons: List[SummonBase] = []
    supports: List[SupportBase] = []
    hands: List[CardBase] = []
    table_deck: List[CardBase] = []
    arcane_legend: bool = True

    charge_satisfied: bool = False
    plunge_satisfied: bool = False

    # when a card is used, it will firstly be moved to using_hand, then it will
    # be moved or removed.
    using_hand: CardBase | None = None

    @validator("team_status", each_item=True, pre=True)
    def parse_team_status(cls, v):
        return get_instance(TeamStatusBase, v)

    @validator("characters", each_item=True, pre=True)
    def parse_characters(cls, v):
        return get_instance(CharacterBase, v)

    @validator("summons", each_item=True, pre=True)
    def parse_summons(cls, v):
        return get_instance(SummonBase, v)

    @validator("supports", each_item=True, pre=True)
    def parse_supports(cls, v):
        return get_instance(SupportBase, v)

    @validator("hands", "table_deck", each_item=True, pre=True)
    def parse_cards(cls, v):
        return get_instance(CardBase, v)

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.dice.position.area == ObjectPositionType.INVALID:
            # not initialized, do initialize.
            self.dice = Dice(
                position=ObjectPosition(
                    player_idx=kwargs["player_idx"],
                    area=ObjectPositionType.DICE,
                    id=-1,
                )
            )

    def dice_color_order_0_0_1(self) -> List[DieColor]:
        """
        Returns the order of dice colors.
        """
        result: List[DieColor] = [DieColor.OMNI]
        assert (
            self.active_character_idx != -1
        ), "Cannot get order when active character index not set."
        c_element = self.characters[self.active_character_idx].element
        color = ELEMENT_TO_DIE_COLOR[c_element]
        result.append(color)
        for character in self.characters:
            c_element = character.element
            color = ELEMENT_TO_DIE_COLOR[c_element]
            if color not in result:
                result.append(color)
        for element in ELEMENT_DEFAULT_ORDER:
            color = ELEMENT_TO_DIE_COLOR[element]
            if color not in result:
                result.append(color)
        return result

    def dice_color_order_0_0_2(self) -> List[DieColor]:
        """
        Returns the order of dice colors.
        Dice colors are always ELEMENT_DEFAULT_ORDER.
        """
        return [DieColor.OMNI] + [
            ELEMENT_TO_DIE_COLOR[x] for x in ELEMENT_DEFAULT_ORDER
        ]

    def dice_color_order(self) -> List[DieColor]:
        """
        Returns the order of dice colors.
        """
        if self.version == "0.0.1":
            return self.dice_color_order_0_0_1()
        return self.dice_color_order_0_0_2()

    def sort_dice(self):
        """
        Sort the dice on the table.
        """
        order = self.dice_color_order()
        self.dice.colors.sort(key=lambda x: order.index(x))

    def get_object(self, position: ObjectPosition) -> ObjectBase | None:
        """
        Get object by its position. If object not exist, return None.
        """
        if position.area == ObjectPositionType.TEAM_STATUS:
            for status in self.team_status:
                if status.id == position.id:
                    return status
            return None
        elif position.area in [
            ObjectPositionType.CHARACTER,
            ObjectPositionType.SKILL,
            ObjectPositionType.CHARACTER_STATUS,
        ]:
            character = self.characters[position.character_idx]
            return character.get_object(position)
        elif position.area == ObjectPositionType.SUMMON:
            for summon in self.summons:
                if summon.id == position.id:
                    return summon
            return None
        elif position.area == ObjectPositionType.SUPPORT:
            for support in self.supports:
                if support.id == position.id:
                    return support
            return None
        elif position.area == ObjectPositionType.HAND:
            if self.using_hand is not None and self.using_hand.id == position.id:
                return self.using_hand
            for card in self.hands:
                if card.id == position.id:
                    return card
            return None
        elif position.area == ObjectPositionType.DECK:
            for card in self.table_deck:
                if card.id == position.id:
                    return card
            return None
        else:
            raise AssertionError(f"Unknown area {position.area}.")

    def get_object_lists(self) -> List[ObjectBase]:
        """
        Get all objects in the table.
        The order of objects should follow the game rule. The rules are:
        1. objects of `self.current_player` goes first
        2. objects belongs to character goes first
            2.1. active character first, then next, next ... until all alive
                characters are included.
            2.2. for one character, order is weapon, artifact, talent, status.
            2.3. for status, order is their index in status list, i.e.
                generated time.
        3. for other objects, order is: summon, support, hand, dice, deck.
            3.1. all other objects in same region are sorted by their index in
                the list.
        """
        result: List[ObjectBase] = []
        start_character_idx = self.active_character_idx
        if start_character_idx == -1:
            start_character_idx = 0
        for i in range(len(self.characters)):
            target = (start_character_idx + i) % len(self.characters)
            if self.characters[target].is_alive:
                result += self.characters[target].get_object_lists()
        result += self.team_status
        result += self.summons
        result += self.supports
        if self.using_hand is not None:
            result.append(self.using_hand)
        result += self.hands
        result += self.table_deck

        # disable them because currently no dice and deck cards will trigger
        # events or modify values.
        # result += self.dice
        # result += self.table_deck

        return result

    def get_active_character(self) -> CharacterBase:
        """
        Returns the active character.
        """
        assert self.active_character_idx >= 0 and self.active_character_idx < len(
            self.characters
        )
        return self.characters[self.active_character_idx]

    def next_character_idx(self, current_idx: int | None = None) -> int | None:
        """
        Returns the next character index. If `current_id` is not provided, the
        active character index will be used.

        Returns:
            int: the next character ID. If there is no next character, returns
                None.
        """
        if current_idx is None:
            current_idx = self.active_character_idx
        assert self.characters[
            current_idx
        ].is_alive, "Cannot get next character when current character is not alive."
        cnum = len(self.characters)
        for i in range(1, cnum):
            target = (current_idx + i) % cnum
            if self.characters[target].is_alive:
                return target
        return None

    def previous_character_idx(self, current_idx: int | None = None) -> int | None:
        """
        Returns the previous character ID. If `current_id` is not provided, the
        active character index will be used.

        Returns:
            int: the previous character ID. If there is no previous character,
                returns None.
        """
        if current_idx is None:
            current_idx = self.active_character_idx
        assert self.characters[current_idx].is_alive, (
            "Cannot get previous character when current character is not " "alive."
        )
        cnum = len(self.characters)
        for i in range(1, cnum):
            target = (cnum + current_idx - i) % cnum
            if self.characters[target].is_alive:
                return target
        return None

    def get_charge_and_arcane_legend(self) -> Tuple[int, bool]:
        """
        Get charge of active character and arcane legend mark together.
        """
        charge = self.get_active_character().charge
        return charge, self.arcane_legend
