from Model.ScriptAction import ScriptAction
from Model.ScriptActionType import ScriptActionType

FLOAT_ROUND_DECIMALS = 3


class ScriptSnapshotAction(ScriptAction):
    
    # - Init
    
    def __init__(self, file_name: str, time: float):
        super(ScriptSnapshotAction, self).__init__()
        self.timestamp = time
        self.path = file_name
    
    def copy(self):
        result = ScriptSnapshotAction(self.path, self.time())
        return result
    
    # - Properties
    
    def time(self):
        return self.timestamp
    
    def set_time(self, value):
        self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
    def file_name(self) -> str:
        return self.path
    
    def set_file_name(self, name: str):
        self.path = name
    
    def action_type(self) -> ScriptActionType:
        return ScriptActionType.SNAPSHOT
    
    def value_as_string(self) -> str:
        return 'snapshot'
