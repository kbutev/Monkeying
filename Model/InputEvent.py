from typing import Protocol, runtime_checkable
from pynput.keyboard import Key as KeyboardKey
from pynput.keyboard import KeyCode as KeyboardKeyCode
from pynput.mouse import Button as MouseKey
from Model.InputEventType import InputEventType
from Model.Point import Point

FLOAT_ROUND_DECIMALS = 3

@runtime_checkable
class InputEvent(Protocol):
    def time(self): assert False
    def set_time(self, value): assert False
    def event_type(self) -> InputEventType: assert False
    def value_as_string(self) -> str: assert False
    
    # Sort
    def __lt__(self, other):
        return self.time() < other.time()

class InputEventDescription:
    timestamp = ""
    type = ""
    value = ""
    
    def value_as_string(self) -> str:
        return self.value

class KeystrokeEvent(InputEvent):
    timestamp = 0
    is_pressed = False # Press or release event
    key = None # Key or KeyCode
    
    def __init__(self, is_pressed, key):
        super(KeystrokeEvent, self).__init__()
        self.is_pressed = is_pressed
        self.set_key(key)
    
    def time(self): return self.timestamp
    def set_time(self, value): self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
    def key_as_string(self) -> str:
        return self.key.char if isinstance(self.key, KeyboardKeyCode) else str(self.key.name)
    
    def event_type(self) -> InputEventType:
        return InputEventType.KEYBOARD_PRESS if self.is_pressed else InputEventType.KEYBOARD_RELEASE
    
    def value_as_string(self) -> str:
        return f'{self.key}'
    
    def set_key(self, key):
        if isinstance(key, KeyboardKey) or isinstance(key, KeyboardKeyCode):
            self.key = key
        elif isinstance(key, str):
            if len(key) == 1:
                self.key = KeyboardKeyCode.from_char(key)
            else:
                self.key = KeyboardKey[key]
        else:
            assert False

class MouseClickEvent(InputEvent):
    timestamp = 0
    is_pressed = False  # Press or release event
    key: MouseKey = None
    point = Point(0, 0)
    
    def __init__(self, is_pressed, key, point):
        super(MouseClickEvent, self).__init__()
        self.is_pressed = is_pressed
        self.key = key
        self.set_point(point)
        self.set_key(key)
    
    def time(self): return self.timestamp
    def set_time(self, value): self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
    def key_as_string(self) -> str:
        return self.key.name
    
    def event_type(self) -> InputEventType:
        return InputEventType.MOUSE_PRESS if self.is_pressed else InputEventType.MOUSE_RELEASE
    
    def value_as_string(self) -> str:
        return f'{self.key} @ ({self.point.x}, {self.point.y})'
    
    def set_key(self, key):
        if isinstance(key, MouseKey):
            self.key = key
        elif isinstance(key, str):
            self.key = MouseKey[key]
        else:
            assert False
    
    def get_point(self):
        return self.point
    
    def set_point(self, point):
        self.point = point

class MouseMoveEvent(InputEvent):
    timestamp = 0
    point = Point(0, 0)
    
    def __init__(self, point):
        super(MouseMoveEvent, self).__init__()
        self.set_point(point)
    
    def time(self): return self.timestamp
    def set_time(self, value): self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
    def event_type(self) -> InputEventType:
        return InputEventType.MOUSE_MOVE
    
    def value_as_string(self) -> str:
        return f'({self.point.x}, {self.point.y})'
    
    def get_point(self):
        return self.point
    
    def set_point(self, point):
        self.point = Point(round(point.x, FLOAT_ROUND_DECIMALS), round(point.y, FLOAT_ROUND_DECIMALS))

class MouseScrollEvent(InputEvent):
    timestamp = 0
    point = Point(0, 0)
    scroll_dt = Point(0, 0)
    
    def __init__(self, point, scroll_dt):
        super(MouseScrollEvent, self).__init__()
        self.set_point(point)
        self.set_scroll_dt(scroll_dt)
    
    def time(self): return self.timestamp
    def set_time(self, value): self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
    def event_type(self) -> InputEventType:
        return InputEventType.MOUSE_SCROLL
    
    def value_as_string(self) -> str:
        return f'({self.scroll_dt.x}, {self.scroll_dt.y}) @ ({self.point.x}, {self.point.y})'
    
    def get_point(self):
        return self.point
    
    def set_point(self, point):
        self.point = Point(round(point.x, FLOAT_ROUND_DECIMALS), round(point.y, FLOAT_ROUND_DECIMALS))
    
    def get_scroll_dt(self):
        return self.scroll_dt
    
    def set_scroll_dt(self, point):
        self.scroll_dt = Point(round(point.x, FLOAT_ROUND_DECIMALS), round(point.y, FLOAT_ROUND_DECIMALS))

