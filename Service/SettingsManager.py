import dataclasses
import enum
import json
import os
from dataclasses import dataclass
from typing import Protocol
from kink import inject, di
from pynput.keyboard import Key as KeyboardKey
from pynput.keyboard import KeyCode as KeyboardKeyCode
from Parser.KeyboardKeyParser import key_to_string, string_to_key
from Utilities.Logger import LoggerProtocol
from Utilities.Path import Path

VERSION = '1.0'
SCRIPTS_DEFAULT_DIR = 'scripts'
SCRIPT_FILE_FORMAT = 'json'

ROOT = 'settings'
KEY_VERSION = 'version'
KEY_HOTKEYS = 'hotkeys'
KEY_CONFIG = 'config'


DEFAULT_INDENT = 2


class SettingsManagerField(enum.StrEnum):
    PLAY_HOTKEY = 'play'
    PAUSE_HOTKEY = 'pause'
    RECORD_HOTKEY = 'record'
    SCRIPTS_PATH = 'scripts-path'
    SCRIPTS_FILE_FORMAT = 'scripts-file-format'
    
    def is_hotkey(self) -> bool:
        return (self == SettingsManagerField.PLAY_HOTKEY or
                self == SettingsManagerField.PAUSE_HOTKEY or
                self == SettingsManagerField.RECORD_HOTKEY)
    
    def is_path(self) -> bool:
        return self == SettingsManagerField.SCRIPTS_PATH


@dataclass
class SettingsManagerValues:
    all_values: dict
    hotkeys: dict
    config: dict
    
    def data_as_json(self, indent):
        data = {ROOT: {KEY_VERSION: VERSION, KEY_HOTKEYS: self.hotkeys, KEY_CONFIG: self.config}}
        return json.dumps(data, indent=indent)
    
    def write_to_file(self, path: Path, indent=DEFAULT_INDENT, permissions='w', encoding="utf-8"):
        path = path.absolute
        file = open(path, permissions, encoding=encoding)
        file.write(self.data_as_json(indent))
        file.close()
    
    def read_from_file(self, path: Path, permissions='r', encoding="utf-8") -> bool:
        path = path.absolute
        file = open(path, permissions, encoding=encoding)
        file_contents = file.read()
        
        if len(file_contents) == 0:
            file.close()
            return False
        
        contents = json.loads(file_contents)
        
        self.all_values = {}
        self.hotkeys = {}
        self.config = {}
        
        if ROOT not in contents:
            file.close()
            raise ValueError("Bad settings json")
        
        contents = contents[ROOT]
        
        if KEY_HOTKEYS not in contents or KEY_CONFIG not in contents:
            file.close()
            raise ValueError("Bad settings json")
        
        loaded_hotkeys = contents[KEY_HOTKEYS]
        
        for index, key in enumerate(loaded_hotkeys):
            self.all_values[key] = loaded_hotkeys[key]
            self.hotkeys[key] = loaded_hotkeys[key]
        
        loaded_config = contents[KEY_CONFIG]
        
        for index, key in enumerate(loaded_config):
            self.all_values[key] = loaded_config[key]
            self.config[key] = loaded_config[key]
        
        file.close()
        return True


class SettingsManagerProtocol(Protocol):
    def get_path(self) -> Path: return None
    
    def write_to_file(self, permissions='w', encoding="utf-8"): pass
    def read_from_file(self, permissions='r', encoding="utf-8"): pass
    def read_from_data(self, values: SettingsManagerValues): pass
    
    def field_value(self, key: SettingsManagerField): pass
    def set_field_value(self, key: SettingsManagerField, value): pass
    def setup_defaults(self): pass


@inject(alias=SettingsManagerProtocol)
class SettingsManager:
    
    # - Init
    
    def __init__(self):
        self.path = Path('settings.json')
        self.values = SettingsManagerValues({}, {}, {})
        self.logger = di[LoggerProtocol]
        self.indent = DEFAULT_INDENT
        
        success = False
        
        if self.file_exists():
            try:
                self.read_from_file()
                success = True
            except Exception as error:
                self.logger.error(f"Failed to read settings, error: {error}")
        
        if not success:
            self.setup_defaults()
            self.write_to_file()
    
    # - Properties
    
    def get_path(self) -> Path: return self.path
    def get_all_values(self) -> {}: return self.values.all_values
    def get_hotkeys(self) -> {}: return self.values.hotkeys # KeyboardKey or KeyboardKeyCode
    def get_config(self) -> {}: return self.values.config # other string values
    
    def field_value(self, key: SettingsManagerField):
        assert key in self.values.all_values
        
        result = self.values.all_values[key]
        
        if key.is_hotkey():
            result = string_to_key(result)
        
        if key.is_path():
            result = Path(result)
        
        return result
    
    def set_field_value(self, key: SettingsManagerField, value):
        if isinstance(value, KeyboardKey) or isinstance(value, KeyboardKeyCode):
            value = key_to_string(value)
            self.values.hotkeys[key] = value
        elif isinstance(value, Path):
            value = value.absolute
            self.values.config[key] = value
        else:
            assert isinstance(value, str)
            self.values.config[key] = value
        
        self.values.all_values[key] = value
    
    def file_exists(self) -> bool:
        path = self.path.absolute
        return os.path.isfile(path)
    
    # - Setup
    
    def setup_defaults(self):
        self.logger.info("setup settings defaults")
        self.set_field_value(SettingsManagerField.PLAY_HOTKEY, KeyboardKey.esc)
        self.set_field_value(SettingsManagerField.PAUSE_HOTKEY, KeyboardKey.delete)
        self.set_field_value(SettingsManagerField.RECORD_HOTKEY, KeyboardKey.esc)
        self.set_field_value(SettingsManagerField.SCRIPTS_PATH, SCRIPTS_DEFAULT_DIR)
        self.set_field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT, SCRIPT_FILE_FORMAT)
    
    def write_to_file(self, permissions='w', encoding="utf-8"):
        self.logger.info(f"write settings to \'{self.path.absolute}\'")
        self.values.write_to_file(self.path, indent=self.indent, permissions=permissions, encoding=encoding)
    
    def read_from_file(self, permissions='r', encoding="utf-8"):
        result = SettingsManagerValues({}, {}, {})
        
        self.logger.info(f"read settings from \'{self.path.absolute}\'")
        success = result.read_from_file(self.path, permissions=permissions, encoding=encoding)
        
        if success:
            self.values = result
        else:
            self.setup_defaults()
    
    def read_from_data(self, values: SettingsManagerValues):
        self.values = dataclasses.replace(values)

