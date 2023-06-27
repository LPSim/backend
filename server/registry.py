import logging
from server.event import EventArguments
from server.action import Actions, ActionTypes
from typing import Dict, Any, List


class Registry:

    def __init__(self):
        self._registry: Dict[int, Any] = {}
        self._id_counter: int = 0
        self.event_triggers: Dict[ActionTypes, List[Any]] = {}
        for i in ActionTypes:
            self.event_triggers[i] = []

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

    def destroy(self, obj):
        """
        Destroy an object from the registry.
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
