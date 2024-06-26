from Model.InputEvent import InputEvent
from pynput.mouse import Button as MouseKey
from Model.KeyPressType import KeyPressType
from Utilities.Point import Point


FLOAT_ROUND_DECIMALS = 3


class MouseClickEvent(InputEvent):
    
    # - Init
    
    def __init__(self, press, key, point):
        super(MouseClickEvent, self).__init__()
        self.timestamp = 0
        self.press = press
        self.key = key
        self.point = point
        self.set_key(key)
    
    def copy(self):
        result = MouseClickEvent(self.press, self.key, self.point)
        result.timestamp = self.timestamp
        return result
    
    # - Properties
    
    def time(self):
        return self.timestamp
    
    def set_time(self, value):
        self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
    def key_value(self): return self.key
    
    def key_as_string(self) -> str:
        return self.key.name
    
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
    
    def press_type(self) -> KeyPressType:
        return self.press


class MouseMoveEvent(InputEvent):
    timestamp = 0
    point = Point(0, 0)
    
    def __init__(self, point):
        super(MouseMoveEvent, self).__init__()
        self.set_point(point)
    
    def time(self): return self.timestamp
    
    def set_time(self, value): self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
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

