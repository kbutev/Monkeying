from typing import Protocol
from Model.InputEvent import InputEvent
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.ScriptActionType import ScriptActionType


class ScriptAction(Protocol):
    def copy(self): return None
    
    def time(self): assert False
    def set_time(self, value): assert False
    def action_type(self) -> ScriptActionType: return None
    def value_as_string(self) -> str: return None
    
    # Sort
    def __lt__(self, other): return self.time() < other.time()


def event_action_type(event: InputEvent) -> ScriptActionType:
    if isinstance(event, KeystrokeEvent):
        pass

