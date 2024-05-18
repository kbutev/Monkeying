from Model.InputEvent import InputEvent
from Model.ScriptAction import ScriptAction
from Model.ScriptActionType import ScriptActionType


class ScriptInputEventAction(ScriptAction):
    
    # - Init
    
    def __init__(self, type: ScriptActionType, event: InputEvent, time=0):
        self.type = type
        self.event = event
        self.set_time(time)
    
    def copy(self):
        result = ScriptInputEventAction(self.type, self.event, self.time())
        return result
    
    # - Properties
    
    def time(self):
        return self.event.time()
    
    def set_time(self, value):
        return self.event.set_time(value)
    
    def action_type(self) -> ScriptActionType:
        return self.type
    
    def value_as_string(self) -> str:
        return self.event.value_as_string()
    
    def get_event(self) -> InputEvent:
        return self.event
