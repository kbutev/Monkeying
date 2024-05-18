from typing import Protocol
from kink import inject
from Model.InputEvent import InputEvent
from Model.KeyPressType import KeyPressType
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.MouseInputEvent import MouseClickEvent, MouseMoveEvent, MouseScrollEvent
from Model.ScriptActionType import ScriptActionType


class ScriptActionTypeParserProtocol(Protocol):
    def type_for_input_event(self, input_event: InputEvent) -> ScriptActionType: return None


@inject(use_factory=True, alias=ScriptActionTypeParserProtocol)
class ScriptActionTypeParser(Protocol):
    
    def __init__(self):
        pass
    
    def type_for_input_event(self, input_event: InputEvent) -> ScriptActionType:
        if isinstance(input_event, KeystrokeEvent):
            match input_event.press_type():
                case KeyPressType.PRESS:
                    return ScriptActionType.KEYBOARD_PRESS
                case KeyPressType.RELEASE:
                    return ScriptActionType.KEYBOARD_RELEASE
                case KeyPressType.CLICK:
                    return ScriptActionType.KEYBOARD_CLICK
        elif isinstance(input_event, MouseClickEvent):
            match input_event.press_type():
                case KeyPressType.PRESS:
                    return ScriptActionType.MOUSE_PRESS
                case KeyPressType.RELEASE:
                    return ScriptActionType.MOUSE_RELEASE
                case KeyPressType.CLICK:
                    return ScriptActionType.MOUSE_CLICK
        elif isinstance(input_event, MouseMoveEvent):
            return ScriptActionType.MOUSE_MOVE
        elif isinstance(input_event, MouseScrollEvent):
            return ScriptActionType.MOUSE_SCROLL
        else:
            assert False

