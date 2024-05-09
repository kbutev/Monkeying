from typing import Protocol
from Model.KeyPressType import KeyPressType
from Model.KeyboardInputEvent import KeystrokeEvent
from OpenScriptView.EditScriptWidget import EditScriptWidgetProtocol
from Parser.EventActionParser import EventActionToStringParserProtocol, EventActionToStringParser, \
    EventActionParserProtocol, EventActionParser
from Presenter.Presenter import Presenter
from Service.EventStorage import EventStorage
from Service.SettingsManager import SettingsManagerField
from Service import SettingsManager
from Utilities import Path as PathUtils
from Utilities.Path import Path

INSERT_EVENT_TIME_ADVANCE = 0.1 # When inserting a new event, it's time is based on the currently selected event plus this value

class EditScriptPresenterRouter(Protocol):
    def enable_tabs(self, enabled): pass
    def insert_script_action(self, parent, input_event): pass
    def edit_script_action(self, parent, event_index, input_event): pass
    def on_save_edit_script_action(self, event_index, input_event): pass

class EditScriptPresenter(Presenter):
    widget: EditScriptWidgetProtocol = None
    router: EditScriptPresenterRouter = None
    
    working_dir: Path
    file_format: str
    
    storage = EventStorage()
    events = []
    event_descriptions = []
    _script_path: Path
    
    event_parser: EventActionParserProtocol = EventActionParser()
    event_string_parser: EventActionToStringParserProtocol = EventActionToStringParser()
    
    def __init__(self, script):
        super(EditScriptPresenter, self).__init__()
        
        settings = SettingsManager.singleton
        self.working_dir = settings.field_value(SettingsManagerField.SCRIPTS_PATH)
        self.file_format = settings.field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT)
        
        self._script_path = PathUtils.combine_paths(self.working_dir, script)
        self.storage.read_from_file(self._script_path)
        self.events = list(map(lambda event: self.event_parser.parse_json(event), self.storage.data))
        self.setup_event_descriptions()
    
    def script_path(self) -> Path:
        return self._script_path
    
    def start(self):
        self.update_data()
    
    def stop(self):
        pass
    
    def update_data(self):
        self.events.sort()
        self.setup_event_descriptions()
        self.widget.set_events_data(self.event_descriptions)
    
    def setup_event_descriptions(self):
        self.event_descriptions = list(map(lambda event: self.event_string_parser.parse(event), self.events))
    
    def on_save(self):
        storage_data = []
        
        for event in self.events:
            result = self.event_parser.parse_input_event(event)
            storage_data.append(result.values)
        
        self.storage.data = storage_data
        self.storage.update_modified_date()
        self.storage.write_to_file(self._script_path)
    
    def insert_script_action(self, event_index):
        assert 0 <= event_index
        new_event = KeystrokeEvent(KeyPressType.CLICK, 'x')
        
        if len(self.events) > 0:
            new_event.set_time(self.events[event_index].time() + INSERT_EVENT_TIME_ADVANCE)
        else:
            new_event.set_time(0)
        
        self.router.insert_script_action(self.widget, new_event)
    
    def delete_script_action(self, event_index):
        self.events.remove(self.events[event_index])
        self.update_data()
        self.widget.on_script_action_changed()
    
    def edit_script_action(self, event_index):
        assert 0 <= event_index and event_index < len(self.events)
        input_event = self.events[event_index]
        self.router.edit_script_action(self.widget, event_index, input_event)
    
    def on_save_insert_script_action(self, input_event):
        if input_event is None:
            return
        
        self.events.append(input_event)
        self.widget.on_script_action_changed()
        self.update_data()
        
        # Select next index (to point at the new event)
        self.widget.select_next_index()
    
    def on_save_edit_script_action(self, event_index, input_event):
        if input_event is None:
            return
        
        assert 0 <= event_index and event_index < len(self.events)
        
        self.widget.on_script_action_changed()
        
        self.events[event_index] = input_event
        self.update_data()
        

