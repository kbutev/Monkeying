from Model.ScriptConfiguration import ScriptConfiguration
from Model.ScriptActions import ScriptActions
from Model.ScriptInfo import ScriptInfo
from Utilities.Path import Path


class ScriptData:
    
    def __init__(self, actions=ScriptActions([]), info=ScriptInfo(), config=ScriptConfiguration()):
        self.actions = actions.copy()
        self.info = info.copy()
        self.config = config.copy()
        self.file_path = None
    
    def get_actions(self) -> ScriptActions: return self.actions
    def set_actions(self, value): self.actions = value
    def get_info(self) -> ScriptInfo: return self.info
    def set_info(self, value): self.info = value
    def get_config(self) -> ScriptConfiguration: return self.config
    def set_config(self, value): self.config = value
    def get_file_path(self) -> Path: return self.file_path
    def set_file_path(self, value): self.file_path = value
    
    def copy(self):
        result = ScriptData()
        result.actions = self.actions.copy()
        result.info = self.info.copy()
        result.config = self.config.copy()
        result.file_path = self.file_path.copy()
        return result
    
    def __copy__(self):
        return self.copy()
    
    def sort_actions(self):
        self.actions.data.sort()
    
    def update_modified_date(self):
        self.info.update_modified_date()
