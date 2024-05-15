from Utilities import Logger


CURRENT_VERSION = '1.0'
JSON_VERSION = 'version'
JSON_NAME = 'name'
JSON_DESCRIPTION = 'description'
JSON_CDATE = 'date-created'
JSON_MDATE = 'date-modified'
JSON_EVENT_COUNT = 'event-count'

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
    
    def json(self, count):
        return {
            JSON_VERSION: self.version,
            JSON_NAME: self.name,
            JSON_DESCRIPTION: self.description,
            JSON_CDATE: self.date_created,
            JSON_MDATE: self.date_modified,
            JSON_EVENT_COUNT: count
        }
    
    def read_from_json(self, json):
        self.version = json[JSON_VERSION]
        self.name = json[JSON_NAME]
        self.description = json[JSON_DESCRIPTION]
        self.date_created = json[JSON_CDATE]
        self.date_modified = json[JSON_MDATE]
