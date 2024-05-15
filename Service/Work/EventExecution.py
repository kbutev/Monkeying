from typing import Protocol


class EventExecution(Protocol):
    
    def is_running(self) -> bool: return False
    
    def execute(self, parent=None): pass
    
    def pause(self): pass
    def resume(self): pass
    
    # Returns the result of is_running().
    def update(self) -> bool: pass
