from dataclasses import dataclass


@dataclass
class ScriptActionDescription:
    timestamp: str
    type: str
    value: str
    
    def value_as_string(self) -> str:
        return self.value
