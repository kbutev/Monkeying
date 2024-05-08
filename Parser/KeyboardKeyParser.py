
from pynput.keyboard import Key as KeyboardKey
from pynput.keyboard import KeyCode as KeyboardKeyCode

def key_to_string(key) -> str:
    if isinstance(key, KeyboardKeyCode):
        return key.char
    elif isinstance(key, KeyboardKey):
        return str(key.name)
    else:
        assert False

def string_to_key(value):
    if isinstance(value, KeyboardKey) or isinstance(value, KeyboardKeyCode):
        return value
    elif isinstance(value, str):
        if len(value) == 1:
            return KeyboardKeyCode.from_char(value)
        else:
            return KeyboardKey[value]
    else:
        assert False
