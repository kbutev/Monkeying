import enum
import json
import os
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


class SettingsManagerProtocol(Protocol):
    def write_to_file(self, permissions='w', encoding="utf-8"): pass
    def read_from_file(self, permissions='r', encoding="utf-8"): pass
    
    def field_value(self, key: SettingsManagerField): pass
    def set_field_value(self, key: SettingsManagerField, value): pass
    def setup_defaults(self): pass


@inject(alias=SettingsManagerProtocol)
class SettingsManager:
    
    # - Init
    
    def __init__(self):
        self.path = Path('settings.json')
        self.all_values = {}
        self.hotkeys = {}
        self.config = {}
        self.logger = di[LoggerProtocol]
        self.indent = DEFAULT_INDENT
        
        if self.file_exists():
            self.read_from_file()
        else:
            self.setup_defaults()
            self.write_to_file()
    
    # - Properties
    
    def get_path(self) -> Path: return self.path
    def get_all_values(self) -> {}: return self.all_values
    def get_hotkeys(self) -> {}: return self.hotkeys # KeyboardKey or KeyboardKeyCode
    def get_config(self) -> {}: return self.config # other string values
    
    def field_value(self, key: SettingsManagerField):
        assert key in self.all_values
        
        result = self.all_values[key]
        
        if key.is_hotkey():
            result = string_to_key(result)
        
        if key.is_path():
            result = Path(result)
        
        return result
    
    def set_field_value(self, key: SettingsManagerField, value):
        if isinstance(value, KeyboardKey) or isinstance(value, KeyboardKeyCode):
            value = key_to_string(value)
            self.hotkeys[key] = value
        elif isinstance(value, Path):
            value = value.absolute
            self.config[key] = value
        else:
            assert isinstance(value, str)
            self.config[key] = value
        
        self.all_values[key] = value
    
    def data_as_json(self):
        data = {
            ROOT: {
                KEY_VERSION: VERSION, KEY_HOTKEYS: self.hotkeys, KEY_CONFIG: self.config
            }
        }
        
        return json.dumps(data, indent=self.indent)
    
    def file_exists(self) -> bool:
        path = self.path.absolute
        return os.path.isfile(path)
    
    # - Setup
    
    def setup_defaults(self):
        self.set_field_value(SettingsManagerField.PLAY_HOTKEY, KeyboardKey.esc)
        self.set_field_value(SettingsManagerField.PAUSE_HOTKEY, KeyboardKey.delete)
        self.set_field_value(SettingsManagerField.RECORD_HOTKEY, KeyboardKey.esc)
        self.set_field_value(SettingsManagerField.SCRIPTS_PATH, SCRIPTS_DEFAULT_DIR)
        self.set_field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT, SCRIPT_FILE_FORMAT)
    
    def write_to_file(self, permissions='w', encoding="utf-8"):
        path = self.path.absolute
        self.logger.info(f"write settings to \'{path}\'")
        file = open(path, permissions, encoding=encoding)
        file.write(self.data_as_json())
        file.close()
    
    def read_from_file(self, permissions='r', encoding="utf-8"):
        path = self.path.absolute
        self.logger.info(f"read settings from \'{path}\'")
        file = open(path, permissions, encoding=encoding)
        file_contents = file.read()
        
        if len(file_contents) > 0:
            contents = json.loads(file_contents)[ROOT]
            self.all_values = {}
            self.hotkeys = {}
            self.config = {}
            
            loaded_hotkeys = contents[KEY_HOTKEYS]
            
            for index, key in enumerate(loaded_hotkeys):
                self.all_values[key] = loaded_hotkeys[key]
                self.hotkeys[key] = loaded_hotkeys[key]
            
            loaded_config = contents[KEY_CONFIG]
            
            for index, key in enumerate(loaded_config):
                self.all_values[key] = loaded_config[key]
                self.config[key] = loaded_config[key]
        else:
            self.setup_defaults()
        
        file.close()
