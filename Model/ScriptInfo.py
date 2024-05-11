from datetime import datetime

CURRENT_VERSION = '1.0'
JSON_VERSION = 'version'
JSON_NAME = 'name'
JSON_DESCRIPTION = 'description'
JSON_CDATE = 'date-created'
JSON_MDATE = 'date-modified'
JSON_EVENT_COUNT = 'event-count'

DEFAULT_SCRIPT_NAME = 'script'
DEFAULT_SCRIPT_DESCRIPTION = ''

def current_date():
    return datetime.today().strftime('%Y.%m.%d %H:%M:%S')

class ScriptInfo:
    version = CURRENT_VERSION
    name = DEFAULT_SCRIPT_NAME
    description = DEFAULT_SCRIPT_DESCRIPTION
    date_created = None
    date_modified = None
    
    def __init__(self):
        self.date_created = current_date()
        self.date_modified = current_date()
    
    def is_name_default(self) -> bool:
        return self.name == DEFAULT_SCRIPT_NAME
    
    def update_modified_date(self):
        self.date_modified = current_date()
    
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
