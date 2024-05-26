from Model.ScriptAction import ScriptAction
from Model.ScriptActionType import ScriptActionType
from Utilities.Path import Path
from Utilities import Path as PathUtil

FLOAT_ROUND_DECIMALS = 3
NOOP_SCRIPT = '<noop>'

class ScriptRunAction(ScriptAction):
    
    # - Init
    
    def __init__(self, path, time: float):
        if isinstance(path, str):
            path = Path(path)
        
        assert isinstance(path, Path)
        
        super(ScriptRunAction, self).__init__()
        self.timestamp = time
        self.path = path
    
    def copy(self):
        result = ScriptRunAction(self.path.copy(), self.time())
        return result
    
    # - Properties
    
    def time(self):
        return self.timestamp
    
    def set_time(self, value):
        self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
    def absolute_path(self) -> str:
        return self.path.absolute
    
    def file_name(self) -> str:
        return self.path.last_component()
    
    def set_absolute_path(self, value):
        if isinstance(value, Path):
            self.path = value
        elif isinstance(value, str):
            self.path = Path(value)
        else:
            assert False
    
    def set_file_name(self, value):
        assert isinstance(value, str)
        base = self.path.base_path()
        self.path = PathUtil.combine_paths(base, value)
    
    def action_type(self) -> ScriptActionType:
        return ScriptActionType.RUN_SCRIPT
    
    def value_as_string(self) -> str:
        return f'{self.path.last_component()}'


class NOOPScriptRunAction(ScriptRunAction):
    
    # - Init
    
    def __init__(self, time: float):
        super(NOOPScriptRunAction, self).__init__(NOOP_SCRIPT, time)
        self.timestamp = time
    
    def copy(self):
        result = NOOPScriptRunAction(self.time())
        return result
    
    # - Properties
    
    def time(self):
        return self.timestamp
    
    def set_time(self, value):
        self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
    def action_type(self) -> ScriptActionType:
        return ScriptActionType.RUN_SCRIPT
    
    def value_as_string(self) -> str:
        return f'NOOP'

