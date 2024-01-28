import logging

from pydantic import validator

from ..utils.deck_code import deck_code_to_deck_str, deck_str_to_deck_code

from .object_base import CardBase

from .character.character_base import CharacterBase

from ..utils import BaseModel, get_instance
from typing import Any, Literal, List, Tuple


class Deck(BaseModel):
    name: Literal["Deck"] = "Deck"
    characters: List[CharacterBase] = []
    cards: List[CardBase] = []
    default_version: str | None = None

    @validator("characters", each_item=True, pre=True)
    def parse_characters(cls, v):
        return get_instance(CharacterBase, v)

    @validator("cards", each_item=True, pre=True)
    def parse_cards(cls, v):
        return get_instance(CardBase, v)

    def check_legal(
        self,
        card_number: int | None,
        max_same_card_number: int | None,
        character_number: int | None,
        check_restriction: bool,
    ) -> Tuple[bool, Any]:
        """
        check whether the deck is legal.
        1. the number of characters
        2. the number of cards
        3. the number of cards with the same name
        4. cards with special carrying rules

        Returns:
            bool: whether the deck is legal
            Any: error message if not legal
        """
        if character_number is not None:
            if len(self.characters) != character_number:
                error_msg = f"character number should be {character_number}"
                logging.error(error_msg)
                return False, error_msg
        if card_number is not None:
            if len(self.cards) != card_number:
                error_msg = f"card number should be {card_number}"
                logging.error(error_msg)
                return False, error_msg
        if max_same_card_number is not None:
            card_names = [c.name for c in self.cards]
            for card in card_names:
                if card_names.count(card) > max_same_card_number:
                    error_msg = (
                        f"card {card} should not be more than "
                        f"{max_same_card_number} in deck"
                    )
                    logging.error(error_msg)
                    return False, error_msg
        if check_restriction:
            for card in self.cards:
                restriction = card.get_deck_restriction()
                if restriction.type == "NONE":
                    continue
                elif restriction.type == "FACTION":
                    counter = 0
                    for character in self.characters:
                        if restriction.name in character.faction:
                            counter += 1
                    if counter < restriction.number:
                        error_msg = (
                            f"to use card {card.name}, "
                            f"character number of faction {restriction.name} "
                            f"should be at least {restriction.number}"
                        )
                        logging.error(error_msg)
                        return False, error_msg
                elif restriction.type == "CHARACTER":
                    counter = 0
                    for character in self.characters:
                        if restriction.name == character.name:
                            counter += 1
                    if counter < restriction.number:
                        error_msg = (
                            f"to use card {card.name}, "
                            f"character number of name {restriction.name} "
                            f"should be at least {restriction.number}"
                        )
                        logging.error(error_msg)
                        return False, error_msg
                elif restriction.type == "ELEMENT":
                    counter = 0
                    for character in self.characters:
                        if restriction.name == character.element.value:
                            counter += 1
                    if counter < restriction.number:
                        error_msg = (
                            f"to use card {card.name}, "
                            f"character number of element {restriction.name} "
                            f"should be at least {restriction.number}"
                        )
                        logging.error(error_msg)
                        return False, error_msg
                else:
                    raise NotImplementedError(
                        f"restriction type {restriction.type} not implemented"
                    )
        return True, None

    @staticmethod
    def from_str(deck_str: str) -> "Deck":
        """
        Convert deck string to deck object. One line contains one command,
        card or character.

        To specify default versions for all cards that don't have version
        specified, use 'default_version:version'. If not set, cards without
        version information will not have version in its argument. This line
        must appear before any other lines.

        If declare a character, use 'character:'. Otherwise
        write card name directly.

        To specify different version of cards, add `@version` after the
        line.

        To declare multiple same cards or characters, add `*number` after
        the line. When both marks are used, specify version first.
        You can write comment line start with '#'.

        Examples:

        default_version:4.0
        character:Fischl
        character:Mona
        character:Nahida
        # you can write comment line with '#'
        Timmie*15
        Rana*15

        """
        deck_str = deck_str.strip()
        deck = Deck()
        for line in deck_str.split("\n"):
            line = line.strip()
            if line == "":
                continue
            if line.startswith("default_version:"):
                deck.default_version = line[16:]
                continue
            if line[0] == "#":
                # comment line
                continue
            # deal with numbers
            if "*" in line:
                line, number = line.split("*")
                number = int(number)
            else:
                number = 1
            # deal with version
            if "@" in line:
                line, version = line.split("@")
                version = version.strip()
            else:
                version = deck.default_version
            if line.startswith("character:"):
                args = {"name": line[10:]}
                if version is not None:
                    args["version"] = version
                for _ in range(number):
                    deck.characters.append(get_instance(CharacterBase, args))
            else:
                for _ in range(number):
                    args = {"name": line}
                    if version is not None:
                        args["version"] = version
                    deck.cards.append(get_instance(CardBase, args))
        return deck

    def to_str(self) -> str:
        """
        Convert deck object to deck string.
        """
        deck_str = ""
        if self.default_version is not None:
            deck_str += f"default_version:{self.default_version}\n"
        for character in self.characters:
            deck_str += f"character:{character.name}"
            deck_str += f"@{character.version}"
            deck_str += "\n"
        for card in self.cards:
            deck_str += card.name
            deck_str += f"@{card.version}"
            deck_str += "\n"
        return deck_str

    @staticmethod
    def from_deck_code(deck_code: str, version: str | None = None) -> "Deck":
        """
        Convert deck code to deck object. If version is specified,
        default_version will be set in deck_str.
        """
        return Deck.from_str(deck_code_to_deck_str(deck_code, version))

    def to_deck_code(self) -> str:
        """
        Convert deck object to deck code.
        """
        return deck_str_to_deck_code(self.to_str())
