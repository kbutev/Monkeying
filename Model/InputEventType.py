import enum


class InputEventType(enum.StrEnum):
    KEYBOARD_PRESS = "keyboard.press"
    KEYBOARD_RELEASE = "keyboard.release"
    MOUSE_PRESS = "mouse.press"
    MOUSE_RELEASE = "mouse.release"
    MOUSE_MOVE = "mouse.move"
    MOUSE_SCROLL = "mouse.scroll"
    
    def is_keyboard(self) -> bool:
        return self == InputEventType.KEYBOARD_PRESS or self == InputEventType.KEYBOARD_RELEASE
    
    def is_mouse(self) -> bool:
        return not self.is_keyboard()
