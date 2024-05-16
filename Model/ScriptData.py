from Model.ScriptConfiguration import ScriptConfiguration
from Model.ScriptEvents import ScriptEvents
from Model.ScriptInfo import ScriptInfo
from Utilities.Path import Path


class ScriptData:
    
    def __init__(self, events=ScriptEvents([]), info=ScriptInfo(), config=ScriptConfiguration()):
        self.events = events.copy()
        self.info = info.copy()
        self.config = config.copy()
        self.file_path = None
    
    def get_events(self) -> ScriptEvents: return self.events
    def set_events(self, value): self.events = value
    def get_info(self) -> ScriptInfo: return self.info
    def set_info(self, value): self.info = value
    def get_config(self) -> ScriptConfiguration: return self.config
    def set_config(self, value): self.config = value
    def get_file_path(self) -> Path: return self.file_path
    def set_file_path(self, value): self.file_path = value
    
    def copy(self):
        result = ScriptData()
        result.events = self.events.copy()
        result.info = self.info.copy()
        result.config = self.config.copy()
        return result
    
    def sort_events(self):
        self.events.data.sort()
    
    def update_modified_date(self):
        self.info.update_modified_date()
