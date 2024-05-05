import enum


class InputEventType(enum.StrEnum):
    KEYBOARD_PRESS = "keyboard.press"
    KEYBOARD_RELEASE = "keyboard.release"
    KEYBOARD_CLICK = "keyboard.click"
    MOUSE_PRESS = "mouse.press"
    MOUSE_RELEASE = "mouse.release"
    MOUSE_CLICK = "mouse.click"
    MOUSE_MOVE = "mouse.move"
    MOUSE_SCROLL = "mouse.scroll"
    
    def is_keyboard(self) -> bool:
        return (self == InputEventType.KEYBOARD_PRESS or 
                self == InputEventType.KEYBOARD_RELEASE or
                self == InputEventType.KEYBOARD_CLICK)
    
    def is_mouse(self) -> bool:
        return not self.is_keyboard()
