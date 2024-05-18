from dataclasses import dataclass
from Model.ScriptAction import ScriptAction


@dataclass
class ScriptActions:
    data: [ScriptAction]
    
    def copy(self):
        return ScriptActions(self.data.copy())
    
    def __cmp__(self):
        return self.copy()
    
    def count(self) -> int:
        return len(self.data)
    
    def duration(self) -> float:
        return self.data[self.count() - 1].time() if self.count() > 0 else 0
    
    def sort(self):
        self.data.sort()
    
    def reverse(self):
        self.data = list(reversed(self.data))
