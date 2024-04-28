from typing import Protocol
from Model.InputEvent import InputEventDescription, InputEvent, KeystrokeEvent, MouseMoveEvent, MouseClickEvent, \
    MouseScrollEvent
from Model.InputEventType import InputEventType
from Model.JSONInputEvent import JSONInputEvent
from pynput.mouse import Button as MouseKey


class EventActionParserProtocol(Protocol):
    def parse(self, event) -> InputEvent: pass

class EventActionParser(EventActionParserProtocol):
    
    def parse(self, event) -> InputEvent:
        if isinstance(event, dict):
            event = JSONInputEvent(event)
        
        event_type = InputEventType(event.get_type())
        
        match event_type:
            case InputEventType.KEYBOARD_PRESS:
                result = KeystrokeEvent(True, event.get_keystroke())
            case InputEventType.KEYBOARD_RELEASE:
                result = KeystrokeEvent(False, event.get_keystroke())
            case InputEventType.MOUSE_MOVE:
                result = MouseMoveEvent(event.get_point())
            case InputEventType.MOUSE_PRESS:
                result = MouseClickEvent(True, event.get_keystroke(), event.get_point())
            case InputEventType.MOUSE_RELEASE:
                result = MouseClickEvent(False, event.get_keystroke(), event.get_point())
            case InputEventType.MOUSE_SCROLL:
                result = MouseScrollEvent(event.get_named_point(JSONInputEvent.POINT_NAME_GENERIC), event.get_named_point(JSONInputEvent.POINT_NAME_SCROLL))
            case _:
                assert False
        
        result.set_time(float(event.get_time()))
        return result

class EventActionToStringParserGrouping:
    type: InputEventType
    
    def __init__(self, type):
        self.type = type
    
    def match_event(self, event):
        return event.event_type() == self.type

class EventActionToStringParserProtocol(Protocol):
    def parse(self, event) -> InputEventDescription: pass
    def parse_list(self, events, group_options: EventActionToStringParserGrouping = None) -> [InputEventDescription]: pass

class EventActionToStringParser(EventActionToStringParserProtocol):
    inner_parser: EventActionParserProtocol = EventActionParser()
    
    def parse(self, event) -> InputEventDescription:
        if not isinstance(event, InputEvent):
            event = self.inner_parser.parse(event)
        
        result = InputEventDescription()
        
        input_event: InputEvent = event
        result.time = "{:.1f}".format(input_event.get_time())
        result.type = input_event.event_type().name
        result.value = input_event.value_as_string()
        
        return result
    
    def parse_list(self, events, group_options: EventActionToStringParserGrouping = None) -> [InputEventDescription]:
        result = []
        previous_events = []
        group_enabled = group_options is not None
        
        for event in events:
            new_event = self.inner_parser.parse(event)
            
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


