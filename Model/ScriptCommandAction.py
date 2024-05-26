from Model.ScriptAction import ScriptAction
from Model.ScriptActionType import ScriptActionType
from Utilities.Path import Path

FLOAT_ROUND_DECIMALS = 3


class ScriptCommandAction(ScriptAction):
    
    # - Init
    
    def __init__(self, directory: Path, command: str, time: float):
        super(ScriptCommandAction, self).__init__()
        self.timestamp = time
        self.directory_path = directory
        self.command_value = command
    
    def copy(self):
        result = ScriptCommandAction(self.directory(), self.command(), self.time())
        return result
    
    # - Properties
    
    def time(self):
        return self.timestamp
    
    def set_time(self, value):
        self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
    def directory(self) -> Path:
        return self.directory_path
    
    def set_directory(self, directory: Path):
        self.directory_path = directory
    
    def command(self) -> str:
        return self.command_value
    
    def set_command(self, command: str):
        self.command_value = command
    
    def action_type(self) -> ScriptActionType:
        return ScriptActionType.COMMAND
    
    def value_as_string(self) -> str:
        return f'cmd {self.command_value}'
