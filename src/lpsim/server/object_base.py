"""
Base classes of objects in the game table. They are all subclasses of
ObjectBase. CardBase are defined here because like ObjectBase, they are used 
in many other places. Other objects are defined in their own files.
"""


import time
import random
from .event import UseCardEventArguments
from ..utils import BaseModel
from typing import List, Literal, Any, Tuple, get_origin, get_type_hints
from pydantic import validator
from .action import Actions, ActionTypes, RemoveCardAction
from .consts import (
    ObjectType, ObjectPositionType, CostLabels, PlayerActionLabels
)
from .modifiable_values import ModifiableValueTypes
from .struct import (
    DeckRestriction, ObjectPosition, Cost
)


used_object_ids = set()
ID_MOD_NUM = 86400
ID_MULTI_NUM = 1000000
ID_RAND_NUM = 1024


class ObjectBase(BaseModel):
    """
    Base class of objects in the game table. All objects in the game table 
    should inherit from this class.
    """
    type: ObjectType = ObjectType.EMPTY
    position: ObjectPosition
    id: int = -1

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        # check event handler name valid
        for k in dir(self):
            if k[:14] == 'event_handler_':
                k = k[14:]
                try:
                    k = ActionTypes(k)
                except ValueError:
                    raise ValueError(f'Invalid event handler name: {k}')
            if k[:15] == 'value_modifier_':
                k = k[15:]
                try:
                    k = ModifiableValueTypes(k)
                except ValueError:
                    raise ValueError(f'Invalid value modifier name: {k}')
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
            new_id = (
                int(time.time() % ID_MOD_NUM * ID_MULTI_NUM) 
                * ID_RAND_NUM + random.randint(0, ID_RAND_NUM - 1)
            )
            if new_id in used_object_ids:  # pragma: no cover
                continue
            self.id = new_id
            used_object_ids.add(self.id)
            self.position = self.position.set_id(self.id)
            break


class CardBase(ObjectBase):
    """
    Base class of all real cards. 
    """
    name: str
    desc: str
    type: Literal[ObjectType.CARD, ObjectType.WEAPON, ObjectType.ARTIFACT,
                  ObjectType.TALENT, ObjectType.SUPPORT] = ObjectType.CARD
    strict_version_validation: bool = False  # default accept higher versions
    version: str
    position: ObjectPosition = ObjectPosition(
        player_idx = -1,
        area = ObjectPositionType.INVALID,
        id = -1,
    )
    cost: Cost
    cost_label: int = CostLabels.CARD.value
    remove_when_used: bool = True

    @validator('version', pre = True)
    def accept_same_or_higher_version(cls, v: str, values):  # pragma: no cover
        msg = 'version annotation must be Literal with one str'
        if not isinstance(v, str):
            raise NotImplementedError(msg)
        version_hints = get_type_hints(cls)['version']
        if get_origin(version_hints) != Literal:
            raise NotImplementedError(msg)
        version_hints = version_hints.__args__
        if len(version_hints) > 1:
            raise NotImplementedError(msg)
        version_hint = version_hints[0]
        if values['strict_version_validation'] and v != version_hint:
            raise ValueError(
                f'version {v} is not equal to {version_hint}'
            )
        if v < version_hint:
            raise ValueError(
                f'version {v} is lower than {version_hint}'
            )
        return version_hint

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
        return DeckRestriction(type = 'NONE', name = '', number = 0)

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
        raise NotImplementedError

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[Actions]:
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
            actions.append(RemoveCardAction(
                position = ObjectPosition(
                    player_idx = self.position.player_idx,
                    area = ObjectPositionType.HAND,
                    id = self.id,
                ),
                remove_type = 'USED',
            ))
        actions += self.get_actions(
            target = event.action.target,
            match = match,
        )
        return actions
