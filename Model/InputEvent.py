from typing import Protocol, runtime_checkable
from pynput.keyboard import Key as KeyboardKey
from pynput.keyboard import KeyCode as KeyboardKeyCode
from pynput.mouse import Button as MouseKey
from Model.InputEventType import InputEventType
from Model.Point import Point


@runtime_checkable
class InputEvent(Protocol):
    def get_time(self): assert False
    def set_time(self, value): assert False
    def event_type(self) -> InputEventType: assert False
    def value_as_string(self) -> str: assert False

class InputEventDescription:
    time = ""
    type = ""
    value = ""
    
    def value_as_string(self) -> str:
        return self.value

class KeystrokeEvent(InputEvent):
    time = 0
    is_pressed = False # Press or release event
    key = None # Key or KeyCode
    
    def __init__(self, is_pressed, key):
        super(KeystrokeEvent, self).__init__()
        self.is_pressed = is_pressed
        
        if isinstance(key, KeyboardKey) or isinstance(key, KeyboardKeyCode):
            self.key = key
        elif isinstance(key, str):
            self.key = KeyboardKeyCode.from_char(key)
        else:
            assert False
    
    def get_time(self): return self.time
    def set_time(self, value): self.time = value
    
    def key_as_string(self) -> str:
        return self.key.char
    
    def event_type(self) -> InputEventType:
        return InputEventType.KEYBOARD_PRESS if self.is_pressed else InputEventType.KEYBOARD_RELEASE
    
    def value_as_string(self) -> str:
        return f'{self.key}'

class MouseClickEvent(InputEvent):
    time = 0
    is_pressed = False  # Press or release event
    key: MouseKey = None
    point = Point(0, 0)
    
    def __init__(self, is_pressed, key, point):
        super(MouseClickEvent, self).__init__()
        self.is_pressed = is_pressed
        self.key = key
        self.point = point
        
        if isinstance(key, MouseKey):
            self.key = key
        elif isinstance(key, str):
            self.key = MouseKey[key]
        else:
            assert False
    
    def get_time(self): return self.time
    def set_time(self, value): self.time = value
    
    def key_as_string(self) -> str:
        return self.key.name
    
    def event_type(self) -> InputEventType:
        return InputEventType.MOUSE_PRESS if self.is_pressed else InputEventType.MOUSE_RELEASE
    
    def value_as_string(self) -> str:
        return f'{self.key} @ ({self.point.x}, {self.point.y})'

class MouseMoveEvent(InputEvent):
    time = 0
    point = Point(0, 0)
    
    def __init__(self, point):
        super(MouseMoveEvent, self).__init__()
        self.point = point
    
    def get_time(self): return self.time
    def set_time(self, value): self.time = value
    
    def event_type(self) -> InputEventType:
        return InputEventType.MOUSE_MOVE
    
    def value_as_string(self) -> str:
        return f'({self.point.x}, {self.point.y})'

class MouseScrollEvent(InputEvent):
    time = 0
    point = Point(0, 0)
    scroll_dt = Point(0, 0)
    
    def __init__(self, point, scroll_dt):
        super(MouseScrollEvent, self).__init__()
        self.point = point
        self.scroll_dt = scroll_dt
    
    def get_time(self): return self.time
    def set_time(self, value): self.time = value
    
    def event_type(self) -> InputEventType:
        return InputEventType.MOUSE_SCROLL
    
    def value_as_string(self) -> str:
        return f'({self.scroll_dt.x}, {self.scroll_dt.y}) @ ({self.point.x}, {self.point.y})'
    
