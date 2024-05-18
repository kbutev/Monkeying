from Model.InputEvent import InputEvent
from Model.KeyPressType import KeyPressType
from Model.ScriptActionType import ScriptActionType
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
    
    def copy(self):
        result = KeystrokeEvent(self.press, self.key)
        result.timestamp = self.timestamp
        return result
    
    # - Properties
    
    def time(self):
        return self.timestamp
    
    def set_time(self, value):
        self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
    def key_value(self): return self.key
    
    def key_as_string(self) -> str:
        return key_to_string(self.key)
    
    def action_type(self) -> ScriptActionType:
        match self.press:
            case KeyPressType.PRESS:
                return ScriptActionType.KEYBOARD_PRESS
            case KeyPressType.RELEASE:
                return ScriptActionType.KEYBOARD_RELEASE
            case KeyPressType.CLICK:
                return ScriptActionType.KEYBOARD_CLICK
    
    def value_as_string(self) -> str:
        return f'{self.key}'
    
    def set_key(self, key):
        self.key = string_to_key(key)
    
    def press_type(self) -> KeyPressType:
        return self.press
