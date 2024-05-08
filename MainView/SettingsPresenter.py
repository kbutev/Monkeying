import enum
from typing import Protocol
from MainView.SettingsWidget import SettingsWidgetProtocol, SettingsParameter
from Model.KeyboardInputEvent import KeystrokeEvent
from Parser.KeyboardKeyParser import key_to_string
from Presenter.Presenter import Presenter
from Service.SettingsManager import SettingsManager

class SettingsPresenterRouter(Protocol):
    def enable_tabs(self, value): pass
    def prompt_choose_key_dialog(self, sender): pass


class SettingsPresenter(Presenter):
    router: SettingsPresenterRouter = None
    widget: SettingsWidgetProtocol = None
    
    manager = SettingsManager()
    
    def __init__(self):
        super(SettingsPresenter, self).__init__()
    
    def start(self):
        self.manager.read_from_file()
        self.load_default_values()
    
    def stop(self):
        pass
    
    def load_default_values(self):
        self.widget.setup_field(SettingsParameter.HOTKEY_PLAY, self.manager.play_hotkey_as_string())
        self.widget.setup_field(SettingsParameter.HOTKEY_PAUSE, self.manager.pause_hotkey_as_string())
        self.widget.setup_field(SettingsParameter.HOTKEY_RECORD, self.manager.record_hotkey_as_string())
    
    def save_settings(self):
        self.manager.write_to_file()
    
    def assign_hotkey(self, parameter: SettingsParameter):
        self.router.prompt_choose_key_dialog(parameter)
    
    def on_key_chosen(self, parameter: SettingsParameter, value):
        if isinstance(value, KeystrokeEvent):
            match parameter:
                case SettingsParameter.HOTKEY_PLAY:
                    self.manager.set_play_hotkey(value.key)
                case SettingsParameter.HOTKEY_PAUSE:
                    self.manager.set_pause_hotkey(value.key)
                case SettingsParameter.HOTKEY_RECORD:
                    self.manager.set_record_hotkey(value.key)
                case _:
                    assert False # Missing parameter
            
            self.widget.setup_field(parameter, value.key_as_string())
        else:
            assert False # bad logic
        
        self.save_settings()
