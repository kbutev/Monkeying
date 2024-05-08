import json
import os
from pynput.keyboard import Key as KeyboardKey

from Parser.KeyboardKeyParser import key_to_string, string_to_key
from Utilities.Path import Path

ROOT = 'settings'
VERSION = '1.0'
KEY_VERSION = 'version'
KEY_HOTKEYS = 'hotkeys'
KEY_HOTKEY_PLAY = 'play'
KEY_HOTKEY_PAUSE = 'pause'
KEY_HOTKEY_RECORD = 'record'

class SettingsManager:
    
    path = Path('settings.json')
    
    # KeyboardKey or KeyboardKeyCode
    _record_hotkey = None
    _play_hotkey = None
    _pause_hotkey = None
    
    def __init__(self):
        if self.file_exists():
            self.read_from_file()
        else:
            self.setup_defaults()
            self.write_to_file()
    
    def play_hotkey(self):
        return self._play_hotkey
    
    def play_hotkey_as_string(self) -> str:
        return key_to_string(self.play_hotkey())
    
    def set_play_hotkey(self, key):
        self._play_hotkey = key
    
    def pause_hotkey(self):
        return self._pause_hotkey
    
    def pause_hotkey_as_string(self) -> str:
        return key_to_string(self.pause_hotkey())
    
    def set_pause_hotkey(self, key):
        self._pause_hotkey = key
    
    def record_hotkey(self):
        return self._record_hotkey
    
    def record_hotkey_as_string(self) -> str:
        return key_to_string(self.record_hotkey())
    
    def set_record_hotkey(self, key):
        self._record_hotkey = key
    
    def setup_defaults(self):
        self._play_hotkey = KeyboardKey.esc
        self._pause_hotkey = KeyboardKey.delete
        self._record_hotkey = KeyboardKey.esc
    
    def data_as_json(self):
        data = {
            ROOT: {
                KEY_VERSION: VERSION,
                KEY_HOTKEYS: {
                    KEY_HOTKEY_PLAY: self.play_hotkey_as_string(),
                    KEY_HOTKEY_PAUSE: self.pause_hotkey_as_string(),
                    KEY_HOTKEY_RECORD: self.record_hotkey_as_string()
                }
            }
        }
        
        return json.dumps(data)
    
    def file_exists(self) -> bool:
        path = self.path.absolute
        return os.path.isfile(path)
    
    def write_to_file(self, permissions='w', encoding="utf-8"):
        path = self.path.absolute
        print(f"write settings to \'{path}\'")
        file = open(path, permissions, encoding=encoding)
        file.write(self.data_as_json())
        file.close()
    
    def read_from_file(self, permissions='r', encoding="utf-8"):
        path = self.path.absolute
        print(f"read settings from \'{path}\'")
        file = open(path, permissions, encoding=encoding)
        file_contents = file.read()
        
        if len(file_contents) > 0:
            contents = json.loads(file_contents)[ROOT]
            hotkeys = contents[KEY_HOTKEYS]
            self._play_hotkey = string_to_key(hotkeys[KEY_HOTKEY_PLAY])
            self._pause_hotkey = string_to_key(hotkeys[KEY_HOTKEY_PAUSE])
            self._record_hotkey = string_to_key(hotkeys[KEY_HOTKEY_RECORD])
        else:
            self.setup_defaults()
        
        file.close()
