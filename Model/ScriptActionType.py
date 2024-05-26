import enum


# When adding a new type, add a new class for the corresponding type and then,
# search for "# ScriptAction implement" and implement the appropriate code
class ScriptActionType(enum.StrEnum):
    KEYBOARD_PRESS = "keyboard.press"
    KEYBOARD_RELEASE = "keyboard.release"
    KEYBOARD_CLICK = "keyboard.click"
    MOUSE_PRESS = "mouse.press"
    MOUSE_RELEASE = "mouse.release"
    MOUSE_CLICK = "mouse.click"
    MOUSE_MOVE = "mouse.move"
    MOUSE_SCROLL = "mouse.scroll"
    
    MESSAGE = "action.message"
    RUN_SCRIPT = "action.run_script"
    SNAPSHOT = "action.snapshot"
    COMMAND = "action.command"
    
    # - Helpers
    
    def is_keyboard(self) -> bool:
        return (self == ScriptActionType.KEYBOARD_PRESS or
                self == ScriptActionType.KEYBOARD_RELEASE or
                self == ScriptActionType.KEYBOARD_CLICK)
    
    def is_mouse(self) -> bool:
        return (self == ScriptActionType.MOUSE_PRESS or
                self == ScriptActionType.MOUSE_RELEASE or
                self == ScriptActionType.MOUSE_CLICK or
                self == ScriptActionType.MOUSE_MOVE or
                self == ScriptActionType.MOUSE_SCROLL)
