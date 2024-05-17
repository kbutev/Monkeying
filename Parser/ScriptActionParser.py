from typing import Protocol
from kink import inject
from Model import InputEvent
from Model.KeyPressType import KeyPressType
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.MessageInputEvent import MessageInputEvent
from Model.MouseInputEvent import MouseMoveEvent, MouseClickEvent, MouseScrollEvent
from Model.Point import Point
from Model.ScriptActionJSON import *
from Model.ScriptInputEvent import ScriptInputEvent


class ScriptActionParserProtocol(Protocol):
    def parse_to_json(self, event: InputEvent) -> dict: pass
    def parse_to_event(self, json) -> InputEvent: pass


@inject(use_factory=True, alias=ScriptActionParserProtocol)
class ScriptActionParser(ScriptActionParserProtocol):
    
    def __init__(self):
        pass
    
    def parse_to_json(self, event: InputEvent) -> dict:
        result = dict()
        
        def set_point(point):
            result[KEY_POINT_X] = point.x
            result[KEY_POINT_Y] = point.y
        
        def set_dt_point(point):
            result[KEY_POINT_DT_X] = point.x
            result[KEY_POINT_DT_Y] = point.y
        
        result[KEY_TYPE] = event.event_type().value
        result[KEY_TIME] = event.time()
        
        if isinstance(event, KeystrokeEvent):
            result[KEY_KEYSTROKE] = event.key_as_string()
        elif isinstance(event, MouseClickEvent):
            result[KEY_KEYSTROKE] = event.key_as_string()
            set_point(event.point)
        elif isinstance(event, MouseMoveEvent):
            set_point(event.point)
        elif isinstance(event, MouseScrollEvent):
            set_point(event.point)
            set_dt_point(event.scroll_dt)
        elif isinstance(event, MessageInputEvent):
            result[KEY_MESSAGE] = event.message()
            result[KEY_MESSAGE_NOTIFICATION] = event.notifications_enabled()
        elif isinstance(event, ScriptInputEvent):
            result[KEY_PATH] = event.path.absolute
        else:
            assert False
        
        return result
    
    def parse_to_event(self, json) -> InputEvent:
        event_type = InputEventType(json[KEY_TYPE])
        
        def point() -> Point: return Point(json[KEY_POINT_X], json[KEY_POINT_Y])
        def dt_point() -> Point: return Point(json[KEY_POINT_DT_X], json[KEY_POINT_DT_Y])
        
        match event_type:
            case InputEventType.KEYBOARD_PRESS:
                result = KeystrokeEvent(KeyPressType.PRESS, json[KEY_KEYSTROKE])
            case InputEventType.KEYBOARD_RELEASE:
                result = KeystrokeEvent(KeyPressType.RELEASE, json[KEY_KEYSTROKE])
            case InputEventType.KEYBOARD_CLICK:
                result = KeystrokeEvent(KeyPressType.CLICK, json[KEY_KEYSTROKE])
            case InputEventType.MOUSE_MOVE:
                result = MouseMoveEvent(point())
            case InputEventType.MOUSE_PRESS:
                result = MouseClickEvent(KeyPressType.PRESS, json[KEY_KEYSTROKE], point())
            case InputEventType.MOUSE_RELEASE:
                result = MouseClickEvent(KeyPressType.RELEASE, json[KEY_KEYSTROKE], point())
            case InputEventType.MOUSE_CLICK:
                result = MouseClickEvent(KeyPressType.CLICK, json[KEY_KEYSTROKE], point())
            case InputEventType.MOUSE_SCROLL:
                result = MouseScrollEvent(point(), dt_point())
            case InputEventType.MESSAGE:
                result = MessageInputEvent(json[KEY_MESSAGE], json[KEY_MESSAGE_NOTIFICATION])
            case InputEventType.RUN_SCRIPT:
                result = ScriptInputEvent(json[KEY_PATH])
            case _:
                assert False  # Input event is not implemented or bad type
        
        result.set_time(float(json[KEY_TIME]))
        return result
