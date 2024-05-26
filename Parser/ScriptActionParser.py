from typing import Protocol
from kink import inject
from Model import ScriptAction
from Model.KeyPressType import KeyPressType
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.MouseInputEvent import MouseMoveEvent, MouseClickEvent, MouseScrollEvent
from Model.ScriptSnapshotAction import ScriptSnapshotAction
from Utilities.Point import Point
from Model.ScriptActionJSON import *
from Model.ScriptActionType import ScriptActionType
from Model.ScriptInputEventAction import ScriptInputEventAction
from Model.ScriptMessageAction import ScriptMessageAction
from Model.ScriptRunAction import ScriptRunAction, NOOPScriptRunAction, NOOP_SCRIPT


class ScriptActionParserProtocol(Protocol):
    def parse_to_json(self, action: ScriptAction) -> dict: pass
    def parse_to_action(self, json) -> ScriptAction: pass


@inject(use_factory=True, alias=ScriptActionParserProtocol)
class ScriptActionParser(ScriptActionParserProtocol):
    
    def __init__(self):
        pass
    
    def parse_to_json(self, action: ScriptAction) -> dict:
        result = dict()
        
        def set_point(point):
            result[KEY_POINT_X] = point.x
            result[KEY_POINT_Y] = point.y
        
        def set_dt_point(point):
            result[KEY_POINT_DT_X] = point.x
            result[KEY_POINT_DT_Y] = point.y
        
        result[KEY_TYPE] = action.action_type().value
        result[KEY_TIME] = action.time()
        
        if isinstance(action, ScriptInputEventAction):
            event = action.get_event()
            
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
            else:
                assert False
        elif isinstance(action, ScriptMessageAction):
            result[KEY_MESSAGE] = action.message()
            result[KEY_MESSAGE_NOTIFICATION] = action.notifications_enabled()
        elif isinstance(action, ScriptRunAction):
            result[KEY_PATH] = action.path.absolute
        elif isinstance(action, NOOPScriptRunAction):
            result[KEY_PATH] = ''
        elif isinstance(action, ScriptSnapshotAction):
            result[KEY_PATH] = action.file_name()
        else:
            assert False # ScriptAction implement: not implemented
        
        return result
    
    def parse_to_action(self, json) -> ScriptAction:
        def get_value(key):
            if key not in json:
                raise ValueError(f"Bad script action json, key '{key}' not found")
            return json[key]
        
        action_type = ScriptActionType(get_value(KEY_TYPE))
        
        def point() -> Point: return Point(get_value(KEY_POINT_X), get_value(KEY_POINT_Y))
        def dt_point() -> Point: return Point(get_value(KEY_POINT_DT_X), get_value(KEY_POINT_DT_Y))
        
        input_event = None
        
        match action_type:
            case ScriptActionType.KEYBOARD_PRESS:
                input_event = KeystrokeEvent(KeyPressType.PRESS, get_value(KEY_KEYSTROKE))
            case ScriptActionType.KEYBOARD_RELEASE:
                input_event = KeystrokeEvent(KeyPressType.RELEASE, get_value(KEY_KEYSTROKE))
            case ScriptActionType.KEYBOARD_CLICK:
                input_event = KeystrokeEvent(KeyPressType.CLICK, get_value(KEY_KEYSTROKE))
            case ScriptActionType.MOUSE_MOVE:
                input_event = MouseMoveEvent(point())
            case ScriptActionType.MOUSE_PRESS:
                input_event = MouseClickEvent(KeyPressType.PRESS, get_value(KEY_KEYSTROKE), point())
            case ScriptActionType.MOUSE_RELEASE:
                input_event = MouseClickEvent(KeyPressType.RELEASE, get_value(KEY_KEYSTROKE), point())
            case ScriptActionType.MOUSE_CLICK:
                input_event = MouseClickEvent(KeyPressType.CLICK, get_value(KEY_KEYSTROKE), point())
            case ScriptActionType.MOUSE_SCROLL:
                input_event = MouseScrollEvent(point(), dt_point())
        
        if input_event is not None:
            result = ScriptInputEventAction(action_type, input_event, 0)
        else:
            match action_type:
                case ScriptActionType.MESSAGE:
                    result = ScriptMessageAction(get_value(KEY_MESSAGE), get_value(KEY_MESSAGE_NOTIFICATION), 0)
                case ScriptActionType.RUN_SCRIPT:
                    path = json[KEY_PATH]
                    
                    if path != NOOP_SCRIPT:
                        result = ScriptRunAction(get_value(KEY_PATH), 0)
                    else:
                        result = NOOPScriptRunAction(0)
                case ScriptActionType.SNAPSHOT:
                    result = ScriptSnapshotAction(get_value(KEY_PATH), 0)
                case _:
                    assert False # Input event is not implemented or bad type
        
        result.set_time(float(get_value(KEY_TIME)))
        return result
