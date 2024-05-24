from Model.ScriptConfiguration import ScriptConfiguration
from Model.ScriptActions import ScriptActions
from Model.ScriptInfo import ScriptInfo
from Model.ScriptSummary import ScriptSummary
from Utilities.Path import Path


class ScriptData:
    
    def __init__(self, actions=ScriptActions([]), summary=ScriptSummary()):
        self.actions = actions.copy()
        self.summary = summary.copy()
    
    def get_actions(self) -> ScriptActions: return self.actions
    def set_actions(self, value): self.actions = value
    def get_summary(self) -> ScriptSummary: return self.summary.copy()
    def get_info(self) -> ScriptInfo: return self.summary.info.copy()
    def set_info(self, value): self.summary.info = value.copy()
    def get_config(self) -> ScriptConfiguration: return self.summary.config.copy()
    def set_config(self, value): self.summary.config = value.copy()
    def get_file_path(self) -> Path: return self.summary.get_file_path()
    def set_file_path(self, value): self.summary.set_file_path(value)
    
    def copy(self):
        result = ScriptData()
        result.actions = self.actions.copy()
        result.summary = self.summary.copy()
        return result
    
    def __copy__(self):
        return self.copy()
    
    def sort_actions(self):
        self.actions.data.sort()
    
    def update_modified_date(self):
        self.summary.info.update_modified_date()
