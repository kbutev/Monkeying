from Model.InputEvent import InputEvent
from Model.InputEventType import InputEventType
from Utilities.Path import Path
from Utilities import Path as PathUtil

FLOAT_ROUND_DECIMALS = 3


class ScriptInputEvent(InputEvent):
    
    # - Init
    
    def __init__(self, path: Path):
        super(ScriptInputEvent, self).__init__()
        self.timestamp = 0
        self.path = path
    
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
    
    def event_type(self) -> InputEventType:
        return InputEventType.RUN_SCRIPT
    
    def value_as_string(self) -> str:
        return f'{self.path.last_component()}'
