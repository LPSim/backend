import logging
from .event import EventArguments
from .action import Actions, ActionTypes
from .modifiable_values import (
    ModifiableValueTypes, 
    ModifiableValues,
    ModifiableValueArguments,
)
from typing import Dict, Any, List


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
        self._registry: Dict[int, Any] = {}
        self._id_counter: int = 0
        self.event_triggers: Dict[ActionTypes, List[Any]] = {}
        self.value_modifiers: Dict[ModifiableValueTypes, List[Any]] = {}
        for i in ActionTypes:
            self.event_triggers[i] = []
        for i in ModifiableValueTypes:
            self.value_modifiers[i] = []

    def register(self, obj):
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

    def trigger_event(self, event_arg: EventArguments) -> List[Actions]:
        """
        Trigger events.
        """
        ret: List[Actions] = []
        for obj_id in self.event_triggers[event_arg.type]:
            logging.debug(f'Trigger event {event_arg.type} for '
                          f'{self._registry[obj_id].name}:{obj_id}.')
            ...
        return ret

    def modify_value(self, value: ModifiableValues, 
                     modify_arg: ModifiableValueArguments) -> None:
        """
        Modify values. It will directly modify the value arguments.
        """
        for obj_id in self.value_modifiers[value.type]:
            logging.debug(f'Modify value {value.type} for '
                          f'{self._registry[obj_id].name}:{obj_id}.')
            ...
