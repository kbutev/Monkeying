from Model.InputEventType import InputEventType
from Model.Point import Point


class JSONInputEvent:
    ENTRY_TIME = "t"
    ENTRY_TYPE = "e"
    ENTRY_KEYSTROKE = "v"
    ENTRY_POINT_X = "x"
    ENTRY_POINT_Y = "y"
    ENTRY_POINTS = "points"
    
    POINT_NAME_GENERIC = '0'
    POINT_NAME_SCROLL = '1'
    
    values = {}
    
    def __init__(self, values = {}):
        if isinstance(values, dict):
            self.values = values
        elif values is JSONInputEvent:
            self.values = values.values
        else:
            assert False
    
    def get_time(self) -> float:
        return float(self.values[JSONInputEvent.ENTRY_TIME])
    
    def set_time(self, time: float):
        self.values[JSONInputEvent.ENTRY_TIME] = str(time)
    
    def get_type(self) -> InputEventType:
        name = self.values[JSONInputEvent.ENTRY_TYPE]
        return InputEventType(name)
    
    def set_type(self, type: InputEventType):
        self.values[JSONInputEvent.ENTRY_TYPE] = str(type)
    
    def get_keystroke(self) -> str:
        return self.values[JSONInputEvent.ENTRY_KEYSTROKE]
    
    def set_keystroke(self, key: str):
        self.values[JSONInputEvent.ENTRY_KEYSTROKE] = str(key)
    
    def get_point(self) -> Point:
        return Point(float(self.values[JSONInputEvent.ENTRY_POINT_X]), float(self.values[JSONInputEvent.ENTRY_POINT_Y]))
    
    def set_point(self, point: Point):
        self.values[JSONInputEvent.ENTRY_POINT_X] = str(point.x)
        self.values[JSONInputEvent.ENTRY_POINT_Y] = str(point.y)
    
    def get_named_point(self, name: str) -> Point:
        if JSONInputEvent.ENTRY_POINTS in self.values:
            point_values = self.values[JSONInputEvent.ENTRY_POINTS]
            
            if name in point_values:
                point = point_values[name]
                return Point(float(point[JSONInputEvent.ENTRY_POINT_X]), float(point[JSONInputEvent.ENTRY_POINT_Y]))
        
        assert False
        return Point(0, 0)
    
    def set_named_point(self, name: str, point: Point):
        if JSONInputEvent.ENTRY_POINTS not in self.values:
            self.values[JSONInputEvent.ENTRY_POINTS] = {}
        
        point_values = self.values[JSONInputEvent.ENTRY_POINTS]
        point_values[name] = {JSONInputEvent.ENTRY_POINT_X: str(point.x), JSONInputEvent.ENTRY_POINT_Y: str(point.y)}
