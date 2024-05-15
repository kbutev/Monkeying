from typing import Protocol
from kink import di
from Model.KeyPressType import KeyPressType
from Model.KeyboardInputEvent import KeystrokeEvent
from OpenScriptView.EditScriptWidget import EditScriptWidgetProtocol
from Parser.EventActionParser import EventActionToStringParserProtocol, EventActionParserProtocol
from Presenter.Presenter import Presenter
from Service.ScriptStorage import ScriptStorage
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from Utilities.Path import Path

INSERT_EVENT_TIME_ADVANCE = 0.1 # When inserting a new event, it's time is based on the currently selected event plus this value

class EditScriptPresenterRouter(Protocol):
    def enable_tabs(self, enabled): pass
    def insert_script_action(self, parent, input_event): pass
    def edit_script_action(self, parent, event_index, input_event): pass
    def configure_script(self, parent): pass
    def on_save_edit_script_action(self, event_index, input_event): pass

class EditScriptPresenter(Presenter):
    
    # Init
    
    def __init__(self, script):
        super(EditScriptPresenter, self).__init__()
        
        self.widget = None
        self.router = None
        settings: SettingsManagerProtocol = di[SettingsManagerProtocol]
        self.file_format = settings.field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT)
        self.storage = ScriptStorage()
        self.storage.read_from_file(script)
        self.event_descriptions = []
        self.event_parser = di[EventActionParserProtocol]
        self.event_string_parser = di[EventActionToStringParserProtocol]
        self.events = list(map(lambda event: self.event_parser.parse_json(event), self.storage.data))
        self.setup_event_descriptions()
    
    # Properties
    
    def get_widget(self) -> EditScriptWidgetProtocol: return self.widget
    def set_widget(self, widget): self.widget = widget
    def get_router(self) -> EditScriptPresenterRouter: return self.router
    def set_router(self, router): self.router = router
    def get_file_format(self) -> str: return self.file_format
    def get_events(self) -> []: return self.events
    def get_event_descriptions(self) -> []: return self.event_descriptions
    def get_script_path(self) -> Path: return self.storage.file_path
    
    # Actions
    
    def start(self):
        assert self.widget is not None
        assert self.router is not None
        
        self.update_data()
    
    def stop(self):
        pass
    
    def update_data(self):
        assert self.widget is not None
        assert self.router is not None
        
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
        self.storage.write_to_file(self.storage.file_path)
    
    def on_configure_script(self):
        self.router.configure_script(self.widget)
    
    def update_script_configuration(self, info):
        self.storage.info = info
        self.on_save()
    
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

