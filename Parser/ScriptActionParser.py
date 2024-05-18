from typing import Protocol
from kink import inject
from Model import ScriptAction
from Model.KeyPressType import KeyPressType
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.MouseInputEvent import MouseMoveEvent, MouseClickEvent, MouseScrollEvent
from Model.Point import Point
from Model.ScriptActionJSON import *
from Model.ScriptActionType import ScriptActionType
from Model.ScriptInputEventAction import ScriptInputEventAction
from Model.ScriptMessageAction import ScriptMessageAction
from Model.ScriptRunAction import ScriptRunAction


class ScriptActionParserProtocol(Protocol):
    def parse_to_json(self, action: ScriptAction) -> dict: pass
    def parse_to_action(self, json) -> ScriptAction: pass


@inject(use_factory=True, alias=ScriptActionParserProtocol)
class ScriptActionParser(ScriptActionParserProtocol):
    
    def __init__(self):
        pass
    
    def parse_to_json(self, action: ScriptAction) -> dict:
        assert isinstance(action, ScriptInputEventAction)
        event = action.get_event()
        
        result = dict()
        
        def set_point(point):
            result[KEY_POINT_X] = point.x
            result[KEY_POINT_Y] = point.y
        
        def set_dt_point(point):
            result[KEY_POINT_DT_X] = point.x
            result[KEY_POINT_DT_Y] = point.y
        
        result[KEY_TYPE] = action.action_type().value
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
        elif isinstance(event, ScriptMessageAction):
            result[KEY_MESSAGE] = event.message()
            result[KEY_MESSAGE_NOTIFICATION] = event.notifications_enabled()
        elif isinstance(event, ScriptRunAction):
            result[KEY_PATH] = event.path.absolute
        else:
            assert False
        
        return result
    
    def parse_to_action(self, json) -> ScriptAction:
        action_type = ScriptActionType(json[KEY_TYPE])
        
        def point() -> Point: return Point(json[KEY_POINT_X], json[KEY_POINT_Y])
        def dt_point() -> Point: return Point(json[KEY_POINT_DT_X], json[KEY_POINT_DT_Y])
        
        input_event = None
        
        match action_type:
            case ScriptActionType.KEYBOARD_PRESS:
                input_event = KeystrokeEvent(KeyPressType.PRESS, json[KEY_KEYSTROKE])
            case ScriptActionType.KEYBOARD_RELEASE:
                input_event = KeystrokeEvent(KeyPressType.RELEASE, json[KEY_KEYSTROKE])
            case ScriptActionType.KEYBOARD_CLICK:
                input_event = KeystrokeEvent(KeyPressType.CLICK, json[KEY_KEYSTROKE])
            case ScriptActionType.MOUSE_MOVE:
                input_event = MouseMoveEvent(point())
            case ScriptActionType.MOUSE_PRESS:
                input_event = MouseClickEvent(KeyPressType.PRESS, json[KEY_KEYSTROKE], point())
            case ScriptActionType.MOUSE_RELEASE:
                input_event = MouseClickEvent(KeyPressType.RELEASE, json[KEY_KEYSTROKE], point())
            case ScriptActionType.MOUSE_CLICK:
                input_event = MouseClickEvent(KeyPressType.CLICK, json[KEY_KEYSTROKE], point())
            case ScriptActionType.MOUSE_SCROLL:
                input_event = MouseScrollEvent(point(), dt_point())
        
        if input_event is not None:
            result = ScriptInputEventAction(action_type, input_event)
        else:
            match action_type:
                case ScriptActionType.MESSAGE:
                    result = ScriptMessageAction(json[KEY_MESSAGE], json[KEY_MESSAGE_NOTIFICATION])
                case ScriptActionType.RUN_SCRIPT:
                    result = ScriptRunAction(json[KEY_PATH])
                case _:
                    assert False  # Input event is not implemented or bad type
        
        result.set_time(float(json[KEY_TIME]))
        return result
