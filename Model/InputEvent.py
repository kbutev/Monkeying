from dataclasses import dataclass
from typing import Protocol, runtime_checkable
from Model.InputEventType import InputEventType


@runtime_checkable
class InputEvent(Protocol):
    def time(self): assert False
    def set_time(self, value): assert False
    def event_type(self) -> InputEventType: assert False
    def value_as_string(self) -> str: assert False
    
    # Sort
    def __lt__(self, other):
        return self.time() < other.time()


@dataclass
class InputEventDescription:
    timestamp: str
    type: str
    value: str
    
    def value_as_string(self) -> str:
        return self.value

