import json
from typing import Protocol, Any
from kink import inject, di

from Model.ScriptActions import ScriptActions
from Model.ScriptConfiguration import ScriptConfiguration
from Model.ScriptData import ScriptData
from Model.ScriptInfo import ScriptInfo
from Model.ScriptSummary import ScriptSummary
from Parser.ScriptActionsParser import ScriptActionsParserProtocol
from Utilities.Logger import LoggerProtocol

JSON_DEFAULT_ROOT = 'root'
JSON_INFO = 'info'
JSON_CONFIGURATION = 'configuration'
JSON_ACTIONS = 'actions'

CURRENT_VERSION = '1.0'
JSON_VERSION = 'version'
JSON_NAME = 'name'
JSON_DESCRIPTION = 'description'
JSON_CDATE = 'date-created'
JSON_MDATE = 'date-modified'
JSON_EVENT_COUNT = 'event-count'
JSON_REPEAT_COUNT = 'repeat-count'
JSON_REPEAT_FOREVER = 'repeat-forever'
JSON_NOTIFY_START = 'notify-start'
JSON_NOTIFY_END = 'notify-end'


DEFAULT_INDENT = 2


class ScriptDataParserProtocol(Protocol):
    def parse_to_dict(self, script: ScriptData) -> dict: pass
    def parse_to_json(self, script: ScriptData) -> Any: pass
    def parse_to_script(self, data, ignore_actions=False) -> ScriptData: pass


@inject(use_factory=True, alias=ScriptDataParserProtocol)
class ScriptDataParser(ScriptDataParserProtocol):
    
    def __init__(self, root=JSON_DEFAULT_ROOT):
        self.root = root
        self.actions_parser = di[ScriptActionsParserProtocol]
        self.logger = di[LoggerProtocol]
        self.indent = DEFAULT_INDENT
    
    def get_root(self) -> str: return self.root
    def set_root(self, value: str): self.root = value
    def get_indent(self) -> int: return self.indent
    def set_indent(self, value: int): self.indent = value

    def parse_to_dict(self, script: ScriptData) -> dict:
        actions = self.actions_parser.parse_to_list(script.get_actions())
        info = self.parse_script_info_to_dict(script.get_info(), script.get_actions().count())
        config = self.parse_script_config_to_dict(script.get_config())
        return {
            self.root: {
                JSON_INFO: info,
                JSON_CONFIGURATION: config,
                JSON_ACTIONS: actions
            }
        }
    
    def parse_to_json(self, script: ScriptData) -> Any:
        json_data = self.parse_to_dict(script)
        return json.dumps(json_data, indent=self.indent)
    
    def parse_to_script(self, data, ignore_actions=False) -> ScriptData:
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception as error:
                raise error
        
        if not isinstance(data, dict):
            raise ValueError("Bad given script data")
        
        if self.root not in data:
            raise ValueError("Bad script json, no root")
        
        contents = data[self.root]
        
        def get_value(key):
            if key not in contents:
                raise ValueError(f"Bad script json, key '{key}' not found")
            return contents[key]
        
        actions = ScriptActions([]) if ignore_actions else self.actions_parser.parse_to_actions(get_value(JSON_ACTIONS))
        info = self.parse_json_to_script_info(get_value(JSON_INFO))
        config = self.parse_json_to_script_config(get_value(JSON_CONFIGURATION))
        summary = ScriptSummary(info, config)
        script = ScriptData(actions, summary)
        return script
    
    def parse_script_info_to_dict(self, info: ScriptInfo, count: int) -> dict:
        return {
            JSON_VERSION: info.version,
            JSON_NAME: info.name,
            JSON_DESCRIPTION: info.description,
            JSON_CDATE: info.date_created,
            JSON_MDATE: info.date_modified,
            JSON_EVENT_COUNT: count
        }
    
    def parse_json_to_script_info(self, data: dict) -> ScriptInfo:
        info = ScriptInfo()
        info.version = data[JSON_VERSION]
        info.name = data[JSON_NAME]
        info.description = data[JSON_DESCRIPTION]
        info.date_created = data[JSON_CDATE]
        info.date_modified = data[JSON_MDATE]
        return info
    
    def parse_script_config_to_dict(self, config: ScriptConfiguration) -> dict:
        return {
            JSON_REPEAT_COUNT: config.repeat_count,
            JSON_REPEAT_FOREVER: config.repeat_forever,
            JSON_NOTIFY_START: config.notify_on_start,
            JSON_NOTIFY_END: config.notify_on_end
        }
    
    def parse_json_to_script_config(self, data: dict) -> ScriptConfiguration:
        config = ScriptConfiguration()
        config.repeat_count = data[JSON_REPEAT_COUNT]
        config.repeat_forever = data[JSON_REPEAT_FOREVER]
        config.notify_on_start = data[JSON_NOTIFY_START]
        config.notify_on_end = data[JSON_NOTIFY_END]
        return config

