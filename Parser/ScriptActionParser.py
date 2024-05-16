from typing import Protocol
from kink import inject
from Model import InputEvent
from Model.InputEventType import InputEventType
from Model.JSONInputEvent import JSONInputEvent
from Model.KeyPressType import KeyPressType
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.MessageInputEvent import MessageInputEvent
from Model.MouseInputEvent import MouseMoveEvent, MouseClickEvent, MouseScrollEvent
from Model.ScriptInputEvent import ScriptInputEvent
from Model.JSONInputEvent import POINT_NAME_GENERIC, POINT_NAME_SCROLL


class ScriptActionParserProtocol(Protocol):
    def parse_to_json(self, event: InputEvent) -> JSONInputEvent: pass
    def parse_to_event(self, json) -> InputEvent: pass


@inject(use_factory=True, alias=ScriptActionParserProtocol)
class ScriptActionParser(ScriptActionParserProtocol):
    
    def __init__(self):
        pass
    
    def parse_to_json(self, event: InputEvent) -> JSONInputEvent:
        result = JSONInputEvent()
        result.set_time(event.time())
        result.set_type(event.event_type())
        
        if isinstance(event, KeystrokeEvent):
            result.set_keystroke(event.key_as_string())
        elif isinstance(event, MouseClickEvent):
            result.set_keystroke(event.key_as_string())
            result.set_point(event.point)
        elif isinstance(event, MouseMoveEvent):
            result.set_point(event.point)
        elif isinstance(event, MouseScrollEvent):
            result.set_named_point(POINT_NAME_GENERIC, event.point)
            result.set_named_point(POINT_NAME_SCROLL, event.scroll_dt)
        elif isinstance(event, MessageInputEvent):
            result.set_message(event.message())
            result.set_message_notification(event.notifications_enabled())
        elif isinstance(event, ScriptInputEvent):
            result.set_path(event.path)
        else:
            assert False
        
        return result
    
    def parse_to_event(self, json) -> InputEvent:
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
                assert False  # Input event is not implemented or bad type
        
        result.set_time(float(event.time()))
        return result
