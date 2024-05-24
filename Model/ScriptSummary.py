from Model.ScriptConfiguration import ScriptConfiguration
from Model.ScriptInfo import ScriptInfo
from Utilities.Path import Path


class ScriptSummary:
    def __init__(self, info=ScriptInfo(), config=ScriptConfiguration()):
        self.info = info.copy()
        self.config = config.copy()
        self.file_path = None
    
    def copy(self):
        result = ScriptSummary(self.info.copy(), self.config.copy())
        result.file_path = self.file_path.copy() if self.file_path is not None else None
        return result
    
    def get_info(self) -> ScriptInfo: return self.info
    def get_config(self) -> ScriptConfiguration: return self.config
    def get_file_path(self) -> Path: return self.file_path
    def set_file_path(self, path): self.file_path = path.copy()
