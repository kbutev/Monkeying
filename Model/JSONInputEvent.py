from Model.InputEventType import InputEventType
from Model.Point import Point
from Utilities.Path import Path
from pynput.mouse import Button as MouseKey

ENTRY_TIME = "t"
ENTRY_TYPE = "e"
ENTRY_KEYSTROKE = "v"
ENTRY_POINT_X = "x"
ENTRY_POINT_Y = "y"
ENTRY_POINTS = "points"
ENTRY_MESSAGE = "message"
ENTRY_MESSAGE_NOTIFICATION = "notification"
ENTRY_PATH = "path"

POINT_NAME_GENERIC = '0'
POINT_NAME_SCROLL = '1'


class JSONInputEvent:
    
    # - Init
    
    def __init__(self, values = None):
        if isinstance(values, dict):
            self.values = values.copy()
        elif isinstance(values, JSONInputEvent):
            self.values = values.values.copy()
        else:
            self.values = dict()
    
    # - Setup
    
    def set_defaults(self, type):
        self.set_type(type)
        self.set_keystroke('x' if self.type().is_keyboard() else MouseKey.left.name)
        self.set_path('')
    
    # - Properties
    
    def time(self) -> float:
        return float(self.values[ENTRY_TIME])
    
    def set_time(self, time: float):
        self.values[ENTRY_TIME] = str(time)
    
    def type(self) -> InputEventType:
        name = self.values[ENTRY_TYPE]
        return InputEventType(name)
    
    def set_type(self, type: InputEventType):
        self.values[ENTRY_TYPE] = str(type)
    
    def keystroke(self) -> str:
        return self.values[ENTRY_KEYSTROKE]
    
    def set_keystroke(self, key: str):
        self.values[ENTRY_KEYSTROKE] = str(key)
    
    def point(self) -> Point:
        if ENTRY_POINT_X not in self.values or ENTRY_POINT_Y not in self.values: return Point(0, 0)
        
        return Point(float(self.values[ENTRY_POINT_X]), float(self.values[ENTRY_POINT_Y]))
    
    def set_point(self, point: Point):
        self.values[ENTRY_POINT_X] = str(point.x)
        self.values[ENTRY_POINT_Y] = str(point.y)
    
    def named_point(self, name: str) -> Point:
        if ENTRY_POINTS in self.values:
            point_values = self.values[ENTRY_POINTS]
            
            if name in point_values:
                point = point_values[name]
                return Point(float(point[ENTRY_POINT_X]), float(point[ENTRY_POINT_Y]))
        
        return Point(0, 0)
    
    def set_named_point(self, name: str, point: Point):
        if ENTRY_POINTS not in self.values:
            self.values[ENTRY_POINTS] = {}
        
        point_values = self.values[ENTRY_POINTS]
        point_values[name] = {ENTRY_POINT_X: str(point.x), ENTRY_POINT_Y: str(point.y)}
    
    def message(self) -> str:
        if ENTRY_MESSAGE not in self.values:
            return ''
        
        return self.values[ENTRY_MESSAGE]
    
    def set_message(self, value):
        self.values[ENTRY_MESSAGE] = value
    
    def message_notification(self) -> bool:
        if ENTRY_MESSAGE_NOTIFICATION not in self.values:
            return False
        
        return bool(self.values[ENTRY_MESSAGE_NOTIFICATION])
    
    def set_message_notification(self, value):
        self.values[ENTRY_MESSAGE_NOTIFICATION] = str(value)
    
    def path(self) -> Path:
        return Path(self.values[ENTRY_PATH])
    
    def set_path(self, value):
        if isinstance(value, Path):
            self.values[ENTRY_PATH] = value.absolute
        elif isinstance(value, str):
            self.values[ENTRY_PATH] = value
        else:
            assert False
