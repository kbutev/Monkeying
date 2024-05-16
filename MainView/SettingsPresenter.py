from typing import Protocol
from MainView.SettingsWidget import SettingsWidgetProtocol
from Model.KeyboardInputEvent import KeystrokeEvent
from Parser import KeyboardKeyParser
from Presenter.Presenter import Presenter
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from kink import di

from Utilities.Logger import LoggerProtocol
from Utilities.SimpleWorker import run_in_background


class SettingsPresenterRouter(Protocol):
    def enable_tabs(self, value): pass
    def prompt_choose_key_dialog(self, sender): pass


class SettingsPresenter(Presenter):
    
    # - Init
    
    def __init__(self):
        super(SettingsPresenter, self).__init__()
        self.router = None
        self.widget = None
        self.settings = di[SettingsManagerProtocol]
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def get_router(self) -> SettingsPresenterRouter: return self.router
    def set_router(self, router): self.router = router
    def get_widget(self) -> SettingsWidgetProtocol: return self.widget
    def set_widget(self, widget): self.widget = widget
    
    # - Actions
    
    def start(self):
        self.read_settings_from_file()
    
    def stop(self):
        pass
    
    def read_settings_from_file(self):
        self.logger.info('reading settings...')
        run_in_background(self.settings.read_from_file, lambda result: self.update_data())
    
    def update_data(self):
        self.logger.info('settings values loaded')
        
        play_hotkey = SettingsManagerField.PLAY_HOTKEY
        self.widget.setup_field(play_hotkey, KeyboardKeyParser.key_to_string(self.settings.field_value(play_hotkey)))
        pause_hotkey = SettingsManagerField.PAUSE_HOTKEY
        self.widget.setup_field(pause_hotkey, KeyboardKeyParser.key_to_string(self.settings.field_value(pause_hotkey)))
        record_hotkey = SettingsManagerField.RECORD_HOTKEY
        self.widget.setup_field(record_hotkey, KeyboardKeyParser.key_to_string(self.settings.field_value(record_hotkey)))
    
    def save_settings(self):
        run_in_background(self.settings.write_to_file)
    
    def assign_hotkey(self, parameter: SettingsManagerField):
        self.router.prompt_choose_key_dialog(parameter)
    
    def on_key_chosen(self, parameter: SettingsManagerField, value):
        if isinstance(value, KeystrokeEvent):
            self.settings.set_field_value(parameter, value.key)
            self.widget.setup_field(parameter, value.key_as_string())
        else:
            assert False # bad logic
        
        self.save_settings()
