from typing import Protocol
from MainView.SettingsWidget import SettingsWidgetProtocol
from Model.KeyboardInputEvent import KeystrokeEvent
from Parser import KeyboardKeyParser
from Presenter.Presenter import Presenter
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from kink import di
from Service.ThreadWorkerManager import ThreadWorkerManagerProtocol
from Utilities.Logger import LoggerProtocol
from Utilities.Threading import run_in_background


THREAD_WORKER_READ_LABEL = 'read'
THREAD_WORKER_WRITE_LABEL = 'write'


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
        self.thread_worker_manager = di[ThreadWorkerManagerProtocol]
    
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
        if self.thread_worker_manager.is_running_worker(THREAD_WORKER_READ_LABEL):
            return
        
        self.logger.info('reading settings...')
        worker = run_in_background(self.settings.read_from_file, self._read_settings_from_file_completion)
        self.thread_worker_manager.add_worker(worker, THREAD_WORKER_READ_LABEL)
    
    def _read_settings_from_file_completion(self):
        self.thread_worker_manager.remove_worker(THREAD_WORKER_READ_LABEL)
        self.update_data()
    
    def update_data(self):
        self.logger.info('settings values loaded')
        
        play_hotkey = SettingsManagerField.PLAY_HOTKEY
        self.widget.setup_field(play_hotkey, KeyboardKeyParser.key_to_string(self.settings.field_value(play_hotkey)))
        pause_hotkey = SettingsManagerField.PAUSE_HOTKEY
        self.widget.setup_field(pause_hotkey, KeyboardKeyParser.key_to_string(self.settings.field_value(pause_hotkey)))
        record_hotkey = SettingsManagerField.RECORD_HOTKEY
        self.widget.setup_field(record_hotkey, KeyboardKeyParser.key_to_string(self.settings.field_value(record_hotkey)))
    
    def save_settings(self):
        if self.thread_worker_manager.is_running_worker(THREAD_WORKER_WRITE_LABEL):
            return
        
        worker = run_in_background(self.settings.write_to_file, self._save_settings_completion)
        self.thread_worker_manager.add_worker(worker, THREAD_WORKER_WRITE_LABEL)
    
    def _save_settings_completion(self):
        self.thread_worker_manager.remove_worker(THREAD_WORKER_WRITE_LABEL)
    
    def assign_hotkey(self, parameter: SettingsManagerField):
        self.router.prompt_choose_key_dialog(parameter)
    
    def on_key_chosen(self, parameter: SettingsManagerField, value):
        if isinstance(value, KeystrokeEvent):
            self.settings.set_field_value(parameter, value.key)
            self.widget.setup_field(parameter, value.key_as_string())
        else:
            assert False # bad logic
        
        self.save_settings()
