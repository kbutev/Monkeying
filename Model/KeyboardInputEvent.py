from Model.InputEvent import InputEvent
from pynput.keyboard import Key as KeyboardKey
from pynput.keyboard import KeyCode as KeyboardKeyCode
from Model.InputEventType import InputEventType
from Model.KeyPressType import KeyPressType

FLOAT_ROUND_DECIMALS = 3

class KeystrokeEvent(InputEvent):
    timestamp: float
    press: KeyPressType
    key = None  # Key or KeyCode
    
    def __init__(self, press, key):
        super(KeystrokeEvent, self).__init__()
        self.press = press
        self.set_key(key)
    
    def time(self):
        return self.timestamp
    
    def set_time(self, value):
        self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
    def key_as_string(self) -> str:
        if isinstance(self.key, KeyboardKeyCode):
            return self.key.char
        elif isinstance(self.key, KeyboardKey):
            return str(self.key.name)
        else:
            assert False
    
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
        if isinstance(key, KeyboardKey) or isinstance(key, KeyboardKeyCode):
            self.key = key
        elif isinstance(key, str):
            if len(key) == 1:
                self.key = KeyboardKeyCode.from_char(key)
            else:
                self.key = KeyboardKey[key]
        else:
            assert False
