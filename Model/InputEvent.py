from typing import Protocol, runtime_checkable


@runtime_checkable
class InputEvent(Protocol):
    def copy(self): return None
    
    def time(self): assert False
    def set_time(self, value): assert False
    def value_as_string(self) -> str: assert False
    
    # Sort
    def __lt__(self, other): return self.time() < other.time()

