"""
Base classes of objects in the game table. They are all subclasses of
ObjectBase. CardBase are defined here because like ObjectBase, they are used 
in many other places. Other objects are defined in their own files.
"""


import time
import random

from .query import query, query_one

from ..utils.class_registry import register_base_class

from .event import GameStartEventArguments, UseCardEventArguments
from ..utils import BaseModel, accept_same_or_higher_version
from typing import List, Literal, Any, Tuple
from pydantic import validator
from .action import Actions, ActionTypes, CreateObjectAction, RemoveCardAction
from .consts import ObjectType, ObjectPositionType, CostLabels, PlayerActionLabels
from .modifiable_values import ModifiableValueTypes
from .struct import DeckRestriction, MultipleObjectPosition, ObjectPosition, Cost


used_object_ids = set()
ID_MOD_NUM = 86400
ID_MULTI_NUM = 1000000
ID_RAND_NUM = 1024


class ObjectBase(BaseModel):
    """
    Base class of objects in the game table. All objects in the game table
    should inherit from this class.
    Args:
        name (str): Name of the object.
        desc (str): Description of the object. When set, frontend
            will add desc to the name, i.e. `{name}_{desc}`, to find
            descriptions. This is useful for objects that have different
            descriptions with different state (talent effect activated etc.).
            Defaults to empty string, and frontend will do nothing.
    """

    name: str
    desc: Literal[""] = ""
    type: ObjectType = ObjectType.EMPTY
    position: ObjectPosition
    id: int = -1

    # If the object is in trashbin, event handlers except those in this list
    # will not available.
    available_handler_in_trashbin: List[ActionTypes] = []

    # If the object is in deck, event handlers except those in this list
    # will not available.
    available_handler_in_deck: List[ActionTypes] = []

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        # check event handler name valid
        for k in dir(self):
            if k[:14] == "event_handler_":
                k = k[14:]
                try:
                    k = ActionTypes(k)
                except ValueError:
                    raise ValueError(f"Invalid event handler name: {k}")
            if k[:15] == "value_modifier_":
                k = k[15:]
                try:
                    k = ModifiableValueTypes(k)
                except ValueError:
                    raise ValueError(f"Invalid value modifier name: {k}")
        # if id is -1, generate a new id
        if self.id == -1:
            self.renew_id()
        used_object_ids.add(self.id)
        # set id in position
        self.position = self.position.set_id(self.id)

    def renew_id(self):
        """
        Renew the id of the object.
        """
        while True:
            new_id = int(
                time.time() % ID_MOD_NUM * ID_MULTI_NUM
            ) * ID_RAND_NUM + random.randint(0, ID_RAND_NUM - 1)
            if new_id in used_object_ids:  # pragma: no cover
                continue
            self.id = new_id
            used_object_ids.add(self.id)
            self.position = self.position.set_id(self.id)
            break

    def query(self, match: Any, command: str) -> List["ObjectBase"]:
        """
        Receives match, and get objects from match based on command.

        Command contains:
        - `both / our / opponent` to select player_table, or `self` to select this
            character (caller area must be character or character_status). must appear
            first.
        - `[active / prev / next]` or
            `[deck / hand / character / team_status / summon / support]`
            for player_table, `[weapon / artifact / talent]` or `[skill / status]` for
            character, to select an object (first group) or object lists (second group).
            Note with `both`, select one object may also receive two objects.
        - `['key=value']` to filter current objects that `x.key == value`. All types
            will be converted to str to compare. it can be used multiple times. command
            can be surrounded with quotes, and if not space in key and value, quotes can
            be omitted.
        - `and` to make multiple queries, and their results are combined.

        Samples:
        - `self` to get self character when called by a character status
        - `opponent active status 'name=Seed of Skandha'` to get status
        - `opponent character status name=Refraction` to get status from all opponent
            characters
        - `both summon` to get all summons on field
        - `self and our active and our next` to select characters
        """
        return query(self.position, match, command)

    def query_one(
        self, match: Any, command: str, allow_multiple: bool = False
    ) -> "ObjectBase | None":
        """
        Receives match, and get one object from match based on command.
        If no object is found, return None. For command structure, see `query` function.
        If allow_multiple is False, when multiple objects are found, raise error.
        """
        return query_one(self.position, match, command, allow_multiple)


class CardBase(ObjectBase):
    """
    Base class of all real cards.
    """

    name: str
    type: Literal[
        ObjectType.CARD,
        ObjectType.WEAPON,
        ObjectType.ARTIFACT,
        ObjectType.TALENT,
        ObjectType.SUPPORT,
        ObjectType.ARCANE,
    ] = ObjectType.CARD
    strict_version_validation: bool = False  # default accept higher versions
    version: str
    position: ObjectPosition = ObjectPosition(
        player_idx=-1,
        area=ObjectPositionType.INVALID,
        id=-1,
    )
    cost: Cost
    cost_label: int
    remove_when_used: bool = True
    target_position_type_multiple: Literal[False] = False

    @validator("version", pre=True)
    def accept_same_or_higher_version(cls, v: str, values):
        return accept_same_or_higher_version(cls, v, values)

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        # set cost label into cost
        self.cost.label = self.cost_label
        assert self.cost.original_value is None

    def get_deck_restriction(self) -> DeckRestriction:
        """
        Get the deck restriction of the card. It will be checked when deck is
        created.
        """
        return DeckRestriction(type="NONE", name="", number=0)

    def get_action_type(self, match: Any) -> Tuple[int, bool]:
        """
        Get the action type of using the card.

        Returns:
            Tuple[int, bool]: The first element is the action label, the second
                element is whether the action type is a combat action.
        """
        return PlayerActionLabels.CARD.value, False

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        Get the targets of the card.
        """
        raise NotImplementedError()

    def get_actions(self, target: ObjectPosition | None, match: Any) -> List[Actions]:
        """
        Act the card. It will return a list of actions.

        Arguments:
            target (ObjectPosition | None): The target of the action.
                for cards that do not need to specify target, target is None.
                Note: the ID of the target may not be the same as the ID of the
                card, e.g. equipping artifact. Reconstruct correct
                ObjectPosition if needed.
            match (Any): The match object.
        """
        raise NotImplementedError()

    def is_valid(self, match: Any) -> bool:
        """
        Check if the card can be used. Note that this function will not check
        the cost of the card.
        """
        return True

    def event_handler_USE_CARD(
        self, event: UseCardEventArguments, match: Any
    ) -> List[Actions]:
        """
        If this card is used, trigger events
        """
        actions: List[Actions] = []
        if event.action.card_position.id != self.id:
            # not this card
            return actions
        if self.remove_when_used:
            actions.append(
                RemoveCardAction(
                    position=ObjectPosition(
                        player_idx=self.position.player_idx,
                        area=ObjectPositionType.HAND,
                        id=self.id,
                    ),
                    remove_type="USED",
                )
            )
        # target is None, otherwise should match class
        assert event.action.target is None or (
            isinstance(event.action.target, MultipleObjectPosition)
            == self.target_position_type_multiple
        )
        if event.use_card_success:
            # use success, add actions of the card
            actions += self.get_actions(
                target=event.action.target,  # type: ignore
                match=match,
            )
        return actions


class EventCardBase(CardBase):
    type: Literal[ObjectType.CARD] = ObjectType.CARD
    cost_label: int = CostLabels.CARD.value | CostLabels.EVENT.value


class MultiTargetEventCardBase(EventCardBase):
    """
    Base class of cards that can target multiple targets.
    """

    target_position_type_multiple: Literal[True] = True

    def get_targets(self, match: Any) -> List[MultipleObjectPosition]:
        raise NotImplementedError()

    def get_actions(
        self, target: MultipleObjectPosition | None, match: Any
    ) -> List[Actions]:
        """
        Act the card. It will return a list of actions.

        Arguments:
            target (MultipleObjectPosition | None): The target of the action.
                for cards that do not need to specify target, target is None.
                Note: the ID of the target may not be the same as the ID of the
                card, e.g. equipping artifact. Reconstruct correct
                ObjectPosition if needed.
            match (Any): The match object.
        """
        raise NotImplementedError()


class CreateSystemEventHandlerObject(BaseModel):
    """
    objects that will create system event handler at game start
    """

    handler_name: str

    available_handler_in_deck: List[ActionTypes] = [
        ActionTypes.GAME_START,
    ]

    def event_handler_GAME_START(
        self, event: GameStartEventArguments, match: Any
    ) -> List[CreateObjectAction]:
        """
        When game start, create event handler with specified name
        """
        return [
            CreateObjectAction(
                object_name=self.handler_name,
                object_position=ObjectPosition(
                    player_idx=-1,
                    area=ObjectPositionType.SYSTEM,
                    id=-1,
                ),
                object_arguments={},
            )
        ]

    def _get_event_handler(self, match: Any):
        """
        get created event handler object. If not found, raise error.
        """
        target_event_handler: Any = None
        for event_handler in match.event_handlers:
            if event_handler.name == self.handler_name:
                target_event_handler = event_handler
                break
        else:
            raise AssertionError(f"event handler {self.handler_name} not found")
        return target_event_handler


# CardBases = CardBase | MultiTargetEventCardBase
register_base_class(CardBase)
register_base_class(EventCardBase)
register_base_class(MultiTargetEventCardBase)
