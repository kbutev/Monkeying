from typing import Protocol
from kink import di
from Model.KeyPressType import KeyPressType
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.ScriptActionJSON import default_event_as_json
from Model.ScriptActionType import ScriptActionType
from Model.ScriptActions import ScriptActions
from Model.ScriptData import ScriptData
from Model.ScriptInputEventAction import ScriptInputEventAction
from OpenScriptView.EditScriptWidget import EditScriptWidgetProtocol
from Parser.ScriptActionDescriptionParser import ScriptActionDescriptionParserProtocol
from Parser.ScriptActionParser import ScriptActionParserProtocol
from Presenter.Presenter import Presenter
from Provider.ScriptDataProvider import ScriptDataProvider
from Service.ScriptStorage import ScriptStorage
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from Utilities.Path import Path


INSERT_EVENT_TIME_ADVANCE = 0.1 # When inserting a new event, it's time is based on the currently selected event plus this value


class EditScriptPresenterRouter(Protocol):
    def enable_tabs(self, enabled): pass
    def insert_script_action(self, parent, action): pass
    def edit_script_action(self, parent, action_index): pass
    def configure_script(self, parent): pass
    def on_save_edit_script_action(self, action_index, action): pass


class EditScriptPresenter(Presenter):
    
    # Init
    
    def __init__(self, script_data: ScriptData):
        super(EditScriptPresenter, self).__init__()
        
        self.widget = None
        self.router = None
        settings: SettingsManagerProtocol = di[SettingsManagerProtocol]
        self.action_parser = di[ScriptActionParserProtocol]
        self.action_string_parser = di[ScriptActionDescriptionParserProtocol]
        self.file_format = settings.field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT)
        self.script_data = script_data.copy()
        self.script_provider = ScriptDataProvider(script_data.get_file_path())
        self.action_descriptions = []
    
    # Properties
    
    def get_widget(self) -> EditScriptWidgetProtocol: return self.widget
    def set_widget(self, widget): self.widget = widget
    def get_router(self) -> EditScriptPresenterRouter: return self.router
    def set_router(self, router): self.router = router
    def get_file_format(self) -> str: return self.file_format
    def get_actions(self) -> ScriptActions: return self.script_data.get_actions()
    def get_action_descriptions(self) -> []: return self.action_descriptions
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
        self.setup_action_descriptions(self.script_data.get_actions())
        self.widget.set_events_data(self.action_descriptions)
        
        if completion is not None: completion()
    
    def setup_action_descriptions(self, script_actions: ScriptActions):
        self.action_descriptions = self.action_string_parser.parse_actions(script_actions)
    
    def on_save(self):
        ScriptStorage(self.get_script_path()).write_script_data_to_file(self.script_data)
        self.update_data(self.script_data)
    
    def on_configure_script(self):
        self.router.configure_script(self.widget)
    
    def update_script_configuration(self, result: ScriptData):
        self.script_data = result.copy()
        self.on_save()
    
    def insert_script_action(self, action_index):
        assert 0 <= action_index
        
        actions = self.get_actions()
        
        default_action_json = default_event_as_json(ScriptActionType.KEYBOARD_CLICK)
        new_action = self.action_parser.parse_to_action(default_action_json)
        
        if actions.count() > 0 and action_index < actions.count():
            new_action.set_time(actions.data[action_index].time() + INSERT_EVENT_TIME_ADVANCE)
        else:
            new_action.set_time(0)
        
        self.router.insert_script_action(self.widget, new_action)
    
    def delete_script_action(self, action_index):
        actions_data = self.get_actions().data
        actions_data.remove(actions_data[action_index])
        self.script_data.events = ScriptActions(actions_data)
        self.update_data(self.script_data)
        self.widget.on_script_action_changed()
    
    def edit_script_action(self, action_index):
        actions = self.get_actions()
        
        assert 0 <= action_index and action_index < actions.count()
        
        action = actions.data[action_index]
        self.router.edit_script_action(self.widget, action_index, action)
    
    def on_save_insert_script_action(self, input_event):
        if input_event is None:
            return
        
        actions_data = self.get_actions().data
        actions_data.append(input_event)
        self.script_data.events = ScriptActions(actions_data)
        self.script_data.events.sort()
        
        self.widget.on_script_action_changed()
        
        self.update_data(self.script_data)
        
        self.widget.select_next_index() # Select next index (to point at the new event)
    
    def on_save_edit_script_action(self, action_index, action):
        if action is None:
            return
        
        actions = self.get_actions()
        
        assert 0 <= action_index and action_index < actions.count()
        
        self.widget.on_script_action_changed()
        
        actions.data[action_index] = action
        
        self.script_data.get_actions().sort()
        
        self.update_data(self.script_data)
    
    def handle_error(self, error, completion):
        if completion is not None: completion()

