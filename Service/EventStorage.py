import json
from typing import Any
from datetime import datetime
from Model.InputEvent import InputEvent
from Model.MouseInputEvent import MouseScrollEvent
from Model.InputEventType import InputEventType
from Model.JSONInputEvent import POINT_NAME_GENERIC, POINT_NAME_SCROLL
from Parser.JSONInputEventParser import JSONInputEventParser
from Utilities.Path import Path

CURRENT_VERSION = '1.0'

JSON_DEFAULT_ROOT = 'root'
JSON_INFO = 'info'
JSON_INFO_VERSION = 'version'
JSON_INFO_CDATE = 'date-created'
JSON_INFO_MDATE = 'date-modified'
JSON_INFO_EVENT_COUNT = 'event-count'
JSON_EVENTS = 'events'

def current_date():
    return datetime.today().strftime('%Y.%m.%d %H:%M:%S')

class EventStorageInfo:
    version = CURRENT_VERSION
    date_created = None
    date_modified = None
    
    def __init__(self):
        self.date_created = current_date()
        self.date_modified = current_date()
    
    def json(self, count):
        return {
            JSON_INFO_VERSION: self.version,
            JSON_INFO_CDATE: self.date_created,
            JSON_INFO_MDATE: self.date_modified,
            JSON_INFO_EVENT_COUNT: count
        }
    
    def read_from_json(self, json):
        self.version = json[JSON_INFO_VERSION]
        self.date_created = json[JSON_INFO_CDATE]
        self.date_modified = json[JSON_INFO_MDATE]

class EventStorage:
    data = []
    parser = JSONInputEventParser()
    
    info = EventStorageInfo()
    
    print_callback = None
    
    def clear(self):
        self.data = []
        
        print("clear data")
    
    def update_modified_date(self):
        self.info.date_modified = current_date()
    
    def json(self, root=JSON_DEFAULT_ROOT):
        data = {
            root: {
                JSON_INFO: self.info.json(len(self.data)),
                JSON_EVENTS: self.data
            }
        }
        
        return json.dumps(data, indent=self.parser.indent)
    
    def record(self, event: InputEvent):
        event_type = event.event_type()
        
        event: Any = event
        
        match event_type:
            case InputEventType.KEYBOARD_PRESS:
                entry = self.parser.build_entry(event.time(), event_type)
                entry.set_keystroke(event.key_as_string())
            case InputEventType.KEYBOARD_RELEASE:
                entry = self.parser.build_entry(event.time(), event_type)
                entry.set_keystroke(event.key_as_string())
            case InputEventType.MOUSE_MOVE:
                entry = self.parser.build_entry(event.time(), event_type)
                entry.set_point(event.point)
            case InputEventType.MOUSE_PRESS:
                entry = self.parser.build_entry(event.time(), event_type)
                entry.set_keystroke(event.key_as_string())
                entry.set_point(event.point)
            case InputEventType.MOUSE_RELEASE:
                entry = self.parser.build_entry(event.time(), event_type)
                entry.set_keystroke(event.key_as_string())
                entry.set_point(event.point)
            case InputEventType.MOUSE_SCROLL:
                scroll_value: MouseScrollEvent = event
                entry = self.parser.build_entry(event.time(), event_type)
                entry.set_named_point(POINT_NAME_GENERIC, scroll_value.point)
                entry.set_named_point(POINT_NAME_SCROLL, scroll_value.scroll_dt)
            case _:
                raise ValueError("Invalid event")
        
        self.data.append(entry.values.copy())
    
    def first_entry(self) -> map:
        assert len(self.data) > 0
        
        return self.data[0]
    
    def data_as_json(self, root="root"):
        return self.json(root)
    
    def write_to_file(self, path, permissions='w', encoding="utf-8", root="root"):
        if isinstance(path, Path):
            path = path.absolute
        
        print(f"write data to \'{path}\'")
        file = open(path, permissions, encoding=encoding)
        file.write(self.data_as_json(root=root))
        file.close()
        print(f"data written {path}")
    
    def read_from_file(self, path, permissions='r', encoding="utf-8", root="root"):
        if isinstance(path, Path):
            path = path.absolute
        
        print(f"read data from \'{path}\'")
        self.clear()
        file = open(path, permissions, encoding=encoding)
        file_contents = file.read()
        
        contents = json.loads(file_contents)[root]
        self.info.read_from_json(contents[JSON_INFO])
        self.data = contents[JSON_EVENTS]
        file.close()
        print("data read successfully")
    
    def print(self, string):
        if self.print_callback is not None:
            self.print_callback(string)
