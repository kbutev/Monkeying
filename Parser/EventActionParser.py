from dataclasses import dataclass
from typing import Protocol
from kink import inject
from Model.InputEvent import InputEventDescription, InputEvent
from Model.KeyPressType import KeyPressType
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.MessageInputEvent import MessageInputEvent
from Model.MouseInputEvent import MouseMoveEvent, MouseClickEvent, MouseScrollEvent
from Model.InputEventType import InputEventType
from Model.JSONInputEvent import JSONInputEvent, POINT_NAME_GENERIC, POINT_NAME_SCROLL
from Model.ScriptInputEvent import ScriptInputEvent


class EventActionParserProtocol(Protocol):
    def parse_json(self, json) -> InputEvent: pass
    def parse_input_event(self, input_event: InputEvent) -> JSONInputEvent: pass


@inject(use_factory=True, alias=EventActionParserProtocol)
class EventActionParser(EventActionParserProtocol):
    
    def parse_json(self, json) -> InputEvent:
        if isinstance(json, dict):
            event = JSONInputEvent(json)
        else:
            event = json
        
        event_type = InputEventType(event.type())
        
        match event_type:
            case InputEventType.KEYBOARD_PRESS:
                result = KeystrokeEvent(KeyPressType.PRESS, event.keystroke())
            case InputEventType.KEYBOARD_RELEASE:
                result = KeystrokeEvent(KeyPressType.RELEASE, event.keystroke())
            case InputEventType.KEYBOARD_CLICK:
                result = KeystrokeEvent(KeyPressType.CLICK, event.keystroke())
            case InputEventType.MOUSE_MOVE:
                result = MouseMoveEvent(event.point())
            case InputEventType.MOUSE_PRESS:
                result = MouseClickEvent(KeyPressType.PRESS, event.keystroke(), event.point())
            case InputEventType.MOUSE_RELEASE:
                result = MouseClickEvent(KeyPressType.RELEASE, event.keystroke(), event.point())
            case InputEventType.MOUSE_CLICK:
                result = MouseClickEvent(KeyPressType.CLICK, event.keystroke(), event.point())
            case InputEventType.MOUSE_SCROLL:
                result = MouseScrollEvent(event.named_point(POINT_NAME_GENERIC), event.named_point(POINT_NAME_SCROLL))
            case InputEventType.MESSAGE:
                result = MessageInputEvent(event.message(), event.message_notification())
            case InputEventType.RUN_SCRIPT:
                result = ScriptInputEvent(event.path())
            case _:
                assert False # Input event is not implemented or bad type
        
        result.set_time(float(event.time()))
        return result
    
    def parse_input_event(self, input_event: InputEvent) -> JSONInputEvent:
        result = JSONInputEvent()
        result.set_time(input_event.time())
        result.set_type(input_event.event_type())
        
        if isinstance(input_event, KeystrokeEvent):
            result.set_keystroke(input_event.key_as_string())
        elif isinstance(input_event, MouseClickEvent):
            result.set_keystroke(input_event.key_as_string())
            result.set_point(input_event.point)
        elif isinstance(input_event, MouseMoveEvent):
            result.set_point(input_event.point)
        elif isinstance(input_event, MouseScrollEvent):
            result.set_named_point(POINT_NAME_GENERIC, input_event.point)
            result.set_named_point(POINT_NAME_SCROLL, input_event.scroll_dt)
        elif isinstance(input_event, MessageInputEvent):
            result.set_message(input_event.message())
            result.set_message_notification(input_event.notifications_enabled())
        elif isinstance(input_event, ScriptInputEvent):
            result.set_path(input_event.path)
        else:
            assert False
        
        return result


@dataclass
class EventActionToStringParserGrouping:
    type: InputEventType
    
    def match_event(self, event):
        return event.event_type() == self.type


class EventActionToStringParserProtocol(Protocol):
    def parse(self, event) -> InputEventDescription: pass
    def parse_list(self, events, group_options: EventActionToStringParserGrouping = None) -> [InputEventDescription]: pass


@inject(use_factory=True, alias=EventActionToStringParserProtocol)
class EventActionToStringParser(EventActionToStringParserProtocol):
    
    def __init__(self):
        self.inner_parser: EventActionParserProtocol = EventActionParser()
    
    def parse(self, event) -> InputEventDescription:
        if not isinstance(event, InputEvent):
            event = self.inner_parser.parse_json(event)

        input_event: InputEvent = event
        timestamp = "{:.3f}".format(input_event.time())
        type = input_event.event_type().name
        value = input_event.value_as_string()
        result = InputEventDescription(timestamp, type, value)
        return result
    
    def parse_list(self, events, group_options: EventActionToStringParserGrouping = None) -> [InputEventDescription]:
        result = []
        previous_events = []
        group_enabled = group_options is not None
        
        for event in events:
            new_event = self.inner_parser.parse_json(event)
            
            # Group logic
            if group_enabled:
                if group_options.match_event(new_event) and len(previous_events) >= 2:
                    if group_options.match_event(previous_events[0]) and group_options.match_event(previous_events[1]):
                        result.pop()
            
            if len(previous_events) >= 2:
                previous_events.pop(0)
            
            result.append(self.parse(new_event))
            previous_events.append(new_event)
        
        return result

