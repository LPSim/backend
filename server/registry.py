import logging
from .event import EventArguments
from .action import Actions, ActionTypes
from .modifiable_values import (
    ModifiableValueTypes, 
    ModifiableValues,
    ModifiableValueArguments,
)
from .object_base import ObjectBase, ObjectType
from typing import Dict, Any, List
from utils import BaseModel


class ObjectSortRule(BaseModel):
    """
    Base class of object sort rules. It is used to sort objects when event is
    triggered.

    Args:
        current_player_id (int): The ID of the player who is currently the
            active player.
        max_charactor_number (int): The maximum number of charactors for one
            player.
        front_charactor_ids (List[int]): The IDs of the front charactors.
        max_index_number (int): The maximum number of objects in one 
            region. Default is 100. It should larger than 
            `self.max_charactor_number`.
    """
    current_player_id: int
    max_charactor_number: int
    front_charactor_ids: List[int]
    max_index_number: int = 100

    def sort_key(self, obj: Any) -> int:
        """
        Calculate the key of the object for sorting. The key is used to sort
        objects to fit the following rules. If one rule is not enough to
        distinguish two objects, the next rule will be used to distinguish them
        until the objects are distinguished. We will use an integer to
        represent the key. The rules are:
        1. objects is `self.current_player_id` or not.
        2. object belongs to charactor or not.
            2.1. front charactor first, otherwise the default order.
            2.2. for one charactor, order is weapon, artifact, talent, buff.
            2.3. for buff, order is their index in buff list, i.e. generated
                time.
        3. for other objects, order is: summon, support, hand, dice, deck.
            3.1. all other objects in same region are sorted by their index in
                the list.

        Args:
            obj (Any): The object to be sorted.

        Returns:
            int: The key of the object.
        """
        key: List[int] = []
        if self.max_charactor_number > self.max_index_number:
            raise ValueError(
                'The maximum index number should be larger than the maximum '
                'charactor number.'
            )
        key_multiplier: List[int] = []
        # Rule 1: objects is `self.current_player_id` or not.
        if obj.player_id == self.current_player_id:
            key.append(0)
        else:
            key.append(1)
        key_multiplier.append(2)

        # Rule 2: object belongs to charactor or not. It will use three digits,
        # first for rule 2, second for rule 2.1, third for rule 2.2 and 2.3.
        charactor_object_order = [
            ObjectType.WEAPON, ObjectType.ARTIFACT, ObjectType.TALENT,
            ObjectType.CHARACTOR_BUFF
        ]
        if obj.type in charactor_object_order:
            key.append(0)

            # Rule 2.1: front charactor first, otherwise the default order.
            front_charactor_id = self.front_charactor_ids[obj.charactor_id]
            if obj.charactor_id == front_charactor_id:
                key.append(0)
            else:
                char_id = obj.charactor_id
                if char_id < front_charactor_id:
                    char_id += 1
                key.append(char_id)

            # Rule 2.2: for one charactor, order is weapon, artifact, talent,
            # buff. if is buff, order is their index in buff list.
            if obj.type != ObjectType.CHARACTOR_BUFF:
                key.append(charactor_object_order.index(obj.type))
            else:
                key.append(3 + obj.index)
        else:
            key += [1, 0, 0]
        key_multiplier += [2, self.max_charactor_number, self.max_index_number]

        # Rule 3: for other objects, order is: summon, support, hand, dice,
        # deck. all other objects in same region are sorted by their index in
        # the list. If type is not in the list, it will put into last.
        other_object_order = [
            ObjectType.SUMMON, ObjectType.SUPPORT, ObjectType.HAND_CARD,
            ObjectType.DICE, ObjectType.DECK_CARD
        ]
        if obj.type in other_object_order:
            key.append(other_object_order.index(obj.type))
            key.append(obj.index)
        else:
            # unknown type. or is charactor types, but as they have smaller
            # index before, whether their index is larger or smaller here
            # does not matter.
            key += [len(other_object_order), obj.index]
        key_multiplier += [len(other_object_order), self.max_index_number]

        res = 0
        for k, m in zip(key, key_multiplier):
            res *= m
            res += k
        return res


class Registry:
    """
    Registry for all objects in the game table. It is used to find objects by
    their IDs, collect event triggers, and collect value modifiers.

    Args:
        logger (logging.Logger): The logger for the registry.
        _registry (Dict[int, Any]): The registry of all objects. Key is the
            object ID, and value is the object.
        _id_counter (int): The counter for object ID. When new object is
            registered, it will be assigned with a new ID and the counter will
            increase by 1.
        event_triggers (Dict[ActionTypes, List[Any]]): The event triggers of
            all objects. Key is the action type, and value is the list of
            object IDs that will trigger the event.
        value_modifiers (Dict[ModifiableValueTypes, List[Any]]): The value 
            modifiers of all objects. Key is the value type, and value is the 
            list of object IDs that will modify the value.
    """
    def __init__(self):
        self._registry: Dict[int, ObjectBase] = {}
        self._id_counter: int = 0
        self.event_triggers: Dict[ActionTypes, List[int]] = {}
        self.value_modifiers: Dict[ModifiableValueTypes, List[int]] = {}
        for i in ActionTypes:
            self.event_triggers[i] = []
        for i in ModifiableValueTypes:
            self.value_modifiers[i] = []

    def register(self, obj: ObjectBase):
        """
        Register an object to the registry.
        """
        self._registry[self._id_counter] = obj
        self._id_counter += 1
        for i in obj.event_triggers:
            self.event_triggers[i].append(self._id_counter)

    def find_object(self, object_id: int):
        """
        Find an object by its ID.
        """
        return self._registry[object_id]

    def find_id(self, obj) -> int:
        """
        Find the ID of an object.
        """
        for i in self._registry:
            if self._registry[i] == obj:
                return i
        raise ValueError('Object not found in registry.')

    def unregister(self, obj):
        """
        Unregister an object from the registry.
        """
        obj_id = self.find_id(obj)
        for i in obj.event_triggers:
            self.event_triggers[i].remove(obj_id)
        self._registry.pop(obj_id)

    def trigger_event(self, event_arg: EventArguments, 
                      sort_rule: ObjectSortRule
                      ) -> List[Actions]:
        """
        Trigger events. It will return a list of actions that will be triggered
        by the event. The actions will be sorted by the sort rule.
        """
        ret: List[Actions] = []
        triggers = self.event_triggers[event_arg.type]
        triggers.sort(key = lambda x: sort_rule.sort_key(x))
        for obj_id in triggers:
            logging.debug(f'Trigger event {event_arg.type} for '
                          f'{self._registry[obj_id].type}:{obj_id}.')
            ...
        return ret

    def modify_value(self, value: ModifiableValues, 
                     sort_rule: ObjectSortRule,
                     modify_arg: ModifiableValueArguments) -> None:
        """
        Modify values. It will directly modify the value argument.
        TODO: move arguments of ModifierValueArguments into ModifierValues.
        """
        modifiers = self.value_modifiers[value.type]
        modifiers.sort(key = lambda x: sort_rule.sort_key(x))
        for obj_id in modifiers:
            logging.debug(f'Modify value {value.type} for '
                          f'{self._registry[obj_id].type}:{obj_id}.')
            ...
