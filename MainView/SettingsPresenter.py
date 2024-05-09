from typing import Protocol
from MainView.SettingsWidget import SettingsWidgetProtocol
from Model.KeyboardInputEvent import KeystrokeEvent
from Parser import KeyboardKeyParser
from Presenter.Presenter import Presenter
from Service.SettingsManager import SettingsManagerField
from Service import SettingsManager


class SettingsPresenterRouter(Protocol):
    def enable_tabs(self, value): pass
    def prompt_choose_key_dialog(self, sender): pass


class SettingsPresenter(Presenter):
    router: SettingsPresenterRouter = None
    widget: SettingsWidgetProtocol = None
    
    manager = SettingsManager.singleton
    
    def __init__(self):
        super(SettingsPresenter, self).__init__()
    
    def start(self):
        self.manager.read_from_file()
        self.load_default_values()
    
    def stop(self):
        pass
    
    def load_default_values(self):
        play_hotkey = SettingsManagerField.PLAY_HOTKEY
        self.widget.setup_field(play_hotkey, KeyboardKeyParser.key_to_string(self.manager.field_value(play_hotkey)))
        pause_hotkey = SettingsManagerField.PAUSE_HOTKEY
        self.widget.setup_field(pause_hotkey, KeyboardKeyParser.key_to_string(self.manager.field_value(pause_hotkey)))
        record_hotkey = SettingsManagerField.RECORD_HOTKEY
        self.widget.setup_field(record_hotkey, KeyboardKeyParser.key_to_string(self.manager.field_value(record_hotkey)))
    
    def save_settings(self):
        self.manager.write_to_file()
    
    def assign_hotkey(self, parameter: SettingsManagerField):
        self.router.prompt_choose_key_dialog(parameter)
    
    def on_key_chosen(self, parameter: SettingsManagerField, value):
        if isinstance(value, KeystrokeEvent):
            self.manager.set_field_value(parameter, value.key)
            self.widget.setup_field(parameter, value.key_as_string())
        else:
            assert False # bad logic
        
        self.save_settings()
