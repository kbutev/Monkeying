from typing import Protocol
from kink import di
from Model.KeyPressType import KeyPressType
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.ScriptData import ScriptData
from Model.ScriptEvents import ScriptEvents
from OpenScriptView.EditScriptWidget import EditScriptWidgetProtocol
from Parser.ScriptActionDescriptionParser import ScriptActionDescriptionParserProtocol
from Parser.ScriptActionsParser import ScriptActionsParserProtocol
from Presenter.Presenter import Presenter
from Provider.ScriptDataProvider import ScriptDataProviderProtocol, ScriptDataProvider
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
    
    def __init__(self, script_data: ScriptData):
        super(EditScriptPresenter, self).__init__()
        
        self.widget = None
        self.router = None
        settings: SettingsManagerProtocol = di[SettingsManagerProtocol]
        self.event_string_parser = di[ScriptActionDescriptionParserProtocol]
        self.file_format = settings.field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT)
        self.script_data = script_data.copy()
        self.script_provider = ScriptDataProvider(script_data.get_file_path())
        self.event_descriptions = []
    
    # Properties
    
    def get_widget(self) -> EditScriptWidgetProtocol: return self.widget
    def set_widget(self, widget): self.widget = widget
    def get_router(self) -> EditScriptPresenterRouter: return self.router
    def set_router(self, router): self.router = router
    def get_file_format(self) -> str: return self.file_format
    def get_events(self) -> ScriptEvents: return self.script_data.events
    def get_event_descriptions(self) -> []: return self.event_descriptions
    def get_script_data(self) -> ScriptData: return self.script_data.copy()
    def get_script_path(self) -> Path: return self.script_provider.get_file_path()
    
    # Actions
    
    def start(self):
        assert self.widget is not None
        assert self.router is not None
        
        self.reload_data()
    
    def stop(self):
        pass
    
    def reload_data(self, completion = None):
        assert self.widget is not None
        assert self.router is not None
        
        self.script_provider.fetch(lambda script: self.update_data(script, completion),
                                   lambda error: self.handle_error(error, completion))
    
    def update_data(self, script: ScriptData, completion=None):
        self.script_data = script
        self.setup_event_descriptions(self.script_data.events)
        self.widget.set_events_data(self.event_descriptions)
        
        if completion is not None: completion()
    
    def setup_event_descriptions(self, script_actions: ScriptEvents):
        self.event_descriptions = list(map(lambda event: self.event_string_parser.parse(event), script_actions.data))
    
    def on_save(self):
        ScriptStorage(self.get_script_path()).write_to_file(self.script_data)
        self.update_data(self.script_data)
    
    def on_configure_script(self):
        self.router.configure_script(self.widget)
    
    def update_script_configuration(self, result: ScriptData):
        self.script_data = result.copy()
        self.on_save()
    
    def insert_script_action(self, event_index):
        assert 0 <= event_index
        
        events = self.get_events()
        new_event = KeystrokeEvent(KeyPressType.CLICK, 'x')
        
        if events.count() > 0 and event_index < events.count():
            new_event.set_time(events.data[event_index].time() + INSERT_EVENT_TIME_ADVANCE)
        else:
            new_event.set_time(0)
        
        self.router.insert_script_action(self.widget, new_event)
    
    def delete_script_action(self, event_index):
        events_data = self.get_events().data
        events_data.remove(events_data[event_index])
        self.script_data.events = ScriptEvents(events_data)
        self.update_data(self.script_data)
        self.widget.on_script_action_changed()
    
    def edit_script_action(self, event_index):
        events = self.get_events()
        
        assert 0 <= event_index and event_index < events.count()
        
        input_event = events.data[event_index]
        self.router.edit_script_action(self.widget, event_index, input_event)
    
    def on_save_insert_script_action(self, input_event):
        if input_event is None:
            return
        
        events_data = self.get_events().data
        events_data.append(input_event)
        self.script_data.events = ScriptEvents(events_data)
        self.script_data.events.sort()
        
        self.widget.on_script_action_changed()
        
        self.update_data(self.script_data)
        
        self.widget.select_next_index() # Select next index (to point at the new event)
    
    def on_save_edit_script_action(self, event_index, input_event):
        if input_event is None:
            return
        
        events = self.get_events()
        
        assert 0 <= event_index and event_index < events.count()
        
        self.widget.on_script_action_changed()
        
        events.data[event_index] = input_event
        
        self.script_data.events.sort()
        
        self.update_data(self.script_data)
    
    def handle_error(self, error, completion):
        if completion is not None: completion()

