from Model.InputEvent import InputEvent
from Model.InputEventType import InputEventType
from Model.KeyPressType import KeyPressType
from Parser.KeyboardKeyParser import key_to_string, string_to_key

FLOAT_ROUND_DECIMALS = 3


class KeystrokeEvent(InputEvent):
    
    # - Init
    
    def __init__(self, press, key):
        super(KeystrokeEvent, self).__init__()
        self.timestamp = 0
        self.press = press
        self.key = None # Key or KeyCode
        self.set_key(key)
    
    # - Properties
    
    def time(self):
        return self.timestamp
    
    def set_time(self, value):
        self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
    def key_value(self): return self.key
    
    def key_as_string(self) -> str:
        return key_to_string(self.key)
    
    def event_type(self) -> InputEventType:
        match self.press:
            case KeyPressType.PRESS:
                return InputEventType.KEYBOARD_PRESS
            case KeyPressType.RELEASE:
                return InputEventType.KEYBOARD_RELEASE
            case KeyPressType.CLICK:
                return InputEventType.KEYBOARD_CLICK
    
    def value_as_string(self) -> str:
        return f'{self.key}'
    
    def set_key(self, key):
        self.key = string_to_key(key)
