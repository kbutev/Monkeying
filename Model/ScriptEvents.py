from dataclasses import dataclass
from Model.InputEvent import InputEvent


@dataclass
class ScriptEvents:
    data: [InputEvent]
    
    def copy(self):
        return ScriptEvents(self.data.copy())
    
    def count(self) -> int:
        return len(self.data)
    
    def duration(self) -> float:
        return self.data[self.count() - 1].time() if self.count() > 0 else 0
    
    def sort(self):
        self.data.sort()
