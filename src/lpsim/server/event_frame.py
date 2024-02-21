from typing import Optional, Union

from .consts import ObjectPositionType
from .event import *


class EventFrameController(BaseModel):
    frame_list: List[EventFrame] = []

    def has_event(self):
        return len(self.frame_list) != 0

    def append(self, event_frame):
        self.frame_list.append(event_frame)

    def pop(self):
        return self.frame_list.pop()

    def run_event_frame(self, match):
        while len(self.frame_list):
            event_frame = self.frame_list[-1]
            if len(event_frame.triggered_actions):
                self.act_action(event_frame, match)
                return
            elif len(event_frame.triggered_objects):
                self.get_action(event_frame, match)
            elif len(event_frame.events):
                self.trigger_event(event_frame, match)
            else:
                self.frame_list.pop()
        # event frame cleared, clear trashbin
        match.trashbin.clear()

    def act_action(self, frame, match):
        activated_action = frame.triggered_actions.pop(0)
        event_args = match._act(activated_action)
        new_frame = EventFrame(
            events=event_args,
        )
        self.frame_list.append(new_frame)

    def get_action(self, frame, match):
        event_arg = frame.processing_event
        assert event_arg is not None
        object_position = frame.triggered_objects.pop(0)
        obj = match.get_object(object_position, event_arg.type)
        handler_name = f"event_handler_{event_arg.type.name}"
        func = getattr(obj, handler_name, None)
        if func is not None:
            frame.triggered_actions = func(event_arg, match)
        self.frame_list[-1] = frame

    def trigger_event(self, event_frame: EventFrame, match) -> None:
        """
        trigger new event to update triggered object lists of a EventFrame.
        it will take first event from events, put it into processing_event,
        and update triggered object lists.
        """
        event_arg = event_frame.events.pop(0)
        event_frame.processing_event = event_arg
        object_list = match.get_object_list()
        # add object in trashbin to list
        for obj in match.trashbin:
            if event_arg.type in obj.available_handler_in_trashbin:
                object_list.append(obj)
        handler_name = f"event_handler_{event_arg.type.name}"
        for obj in object_list:
            # for deck objects, check availability
            if obj.position.area == ObjectPositionType.DECK:
                if event_arg.type not in obj.available_handler_in_deck:
                    continue
            func = getattr(obj, handler_name, None)
            if func is not None:
                event_frame.triggered_objects.append(obj.position)