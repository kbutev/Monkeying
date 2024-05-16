from Utilities import Logger


CURRENT_VERSION = '1.0'
DEFAULT_SCRIPT_NAME = 'script'
DEFAULT_SCRIPT_DESCRIPTION = ''


class ScriptInfo:
    
    # - Init
    
    def __init__(self):
        self.version = CURRENT_VERSION
        self.name = DEFAULT_SCRIPT_NAME
        self.description = DEFAULT_SCRIPT_DESCRIPTION
        self.date_created = Logger.current_date()
        self.date_modified = Logger.current_date()
    
    def copy(self):
        result = ScriptInfo()
        result.version = self.version
        result.name = self.name
        result.description = self.description
        result.date_created = self.date_created
        result.date_modified = self.date_modified
        return result
    
    # - Properties
    
    def get_version(self) -> str: return self.version
    def set_version(self, version): self.version = version
    def get_name(self) -> str: return self.name
    def set_name(self, name): self.name = name
    def get_description(self) -> str: return self.description
    def set_description(self, description): self.description = description
    def get_date_created(self) -> str: return self.date_created
    def set_date_created(self, date): self.date_created = date
    def get_date_modified(self) -> str: return self.date_modified
    def set_date_modified(self, date): self.date_modified = date
    
    def is_name_default(self) -> bool:
        return self.name == DEFAULT_SCRIPT_NAME
    
    def update_modified_date(self):
        self.date_modified = Logger.current_date()
