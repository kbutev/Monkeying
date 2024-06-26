import time
from kink import di
from typing import Protocol
from PyQt5.QtCore import QTimer
from Model.ScriptActionType import ScriptActionType
from Model.ScriptActions import ScriptActions
from Model.ScriptConfiguration import ScriptConfiguration
from Model.ScriptData import ScriptData
from Model.ScriptInfo import ScriptInfo
from Model.ScriptInputEventAction import ScriptInputEventAction
from Model.ScriptSummary import ScriptSummary
from Parser.ScriptActionDescriptionParser import ScriptActionDescriptionParserProtocol, Grouping
from Parser.ScriptActionTypeParser import ScriptActionTypeParserProtocol
from Presenter.Presenter import Presenter
from Service.EventMonitor import KeyboardEventMonitor
from Service.EventMonitorManager import EventMonitorManager
from MainView.RecordScriptWidget import RecordScriptWidgetProtocol
from Service.ScriptStorage import ScriptStorage
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from Utilities.Logger import LoggerProtocol
from Utilities.Path import Path


class RecordScriptPresenterRouter(Protocol):
    def enable_tabs(self, value): pass
    def pick_save_file(self, directory) -> Path: pass
    def configure_script(self, parent, script: ScriptData): pass


class RecordScriptPresenter(Presenter):
    
    # - Init
    
    def __init__(self):
        super(RecordScriptPresenter, self).__init__()
        
        self.router = None
        self.widget = None
        
        self.settings = di[SettingsManagerProtocol]
        self.keyboard_monitor = di[KeyboardEventMonitor]
        self.description_parser = di[ScriptActionDescriptionParserProtocol]
        self.action_type_parser = di[ScriptActionTypeParserProtocol]
        
        self.event_monitor = EventMonitorManager()
        self.script_info = ScriptInfo()
        self.script_config = ScriptConfiguration()
        
        self.running = False
        self.file_format = '.json'
        self.trigger_key = None
        
        # When used, the hotkey is suspended for a short period
        self.hotkey_click_time = 0
        self.hotkey_suspend_interval = 0.5
        
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(False)
        self.update_timer.setInterval(100)
        self.update_timer.timeout.connect(self.update_events)
        
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def is_running(self) -> bool: return self.running
    def get_widget(self) -> RecordScriptWidgetProtocol: return self.widget
    def set_widget(self, widget): self.widget = widget
    def get_router(self) -> RecordScriptPresenterRouter: return self.router
    def set_router(self, router): self.router = router
    def get_recorded_events(self) -> []: return self.event_monitor.get_events()
    def get_script_info(self) -> ScriptInfo: return self.script_info
    def get_script_config(self) -> ScriptConfiguration: return self.script_config
    def get_recorded_events_as_actions(self) -> ScriptActions:
        type_parser = self.action_type_parser
        events = self.get_recorded_events()
        
        result = list(map(lambda event: ScriptInputEventAction(type_parser.type_for_input_event(event),
                                                               event,
                                                               event.time()), events))
        
        return ScriptActions(result)
    
    # - Setup
    
    def start(self):
        self.trigger_key = self.settings.field_value(SettingsManagerField.RECORD_HOTKEY)
        
        self.keyboard_monitor = di[KeyboardEventMonitor]
        self.keyboard_monitor.setup(self.noop_on_key_press, self.on_key_press)
        self.keyboard_monitor.start()
        
        self.event_monitor.filter_keys.append(self.trigger_key)
    
    def stop(self):
        if self.keyboard_monitor.is_running():
            self.keyboard_monitor.stop()
        
        if self.is_running():
            self.stop_recording(sender=self)
        
        if self.trigger_key in self.event_monitor.filter_keys:
            self.event_monitor.filter_keys.remove(self.trigger_key)
    
    # - Actions
    
    def enable_tabs(self, value):
        self.router.enable_tabs(value)
    
    def begin_recording(self, sender):
        assert not self.running
        assert self.widget is not None
        
        self.logger.info('RecordScriptPresenter begin')
        
        self.running = True
        self.event_monitor.start()
        self.update_events()
        self.update_timer.start()
        self.hotkey_click_time = time.time()
        
        # If command was initiated by the widget, do not forward it back
        if sender is not self.widget:
            self.widget.begin_recording(sender=self)
    
    def stop_recording(self, sender):
        assert self.running
        assert self.widget is not None
        
        self.logger.info('RecordScriptPresenter stop recording')
        
        self.running = False
        self.event_monitor.stop()
        self.update_timer.stop()
        
        # If command was initiated by the widget, do not forward it back
        if sender is not self.widget:
            self.widget.stop_recording(sender=self)
    
    def configure_script(self):
        actions = self.get_recorded_events_as_actions()
        info = self.get_script_info().copy()
        config = self.get_script_config().copy()
        summary = ScriptSummary(info, config)
        script = ScriptData(actions, summary)
        self.router.configure_script(self.widget, script)
    
    def update_script_configuration(self, result: ScriptData):
        # ignore actions
        self.script_info = result.get_info().copy()
        self.script_config = result.get_config().copy()
    
    def save_recording(self):
        assert self.router is not None
        
        actions = self.get_recorded_events_as_actions()
        info = self.get_script_info().copy()
        config = self.get_script_config().copy()
        
        self.logger.info(f'RecordScriptPresenter save {info.name}')
        scripts_dir = self.settings.field_value(SettingsManagerField.SCRIPTS_PATH)
        file_path = self.router.pick_save_file(scripts_dir)
        
        if file_path is None:
            return
        
        if not file_path.absolute.endswith(self.file_format):
            file_path.append_to_end(self.file_format)
        
        # When name is not set, set it to equal file name
        if info.is_name_default():
            info.name = file_path.stem()
        
        summary = ScriptSummary(info, config)
        script = ScriptData(actions, summary)
        ScriptStorage(file_path).write_script_data_to_file(script)
        
        self.widget.disable_save_recording()
        self.widget.on_script_save()
    
    def on_key_press(self, event):
        time_since_last_usage = time.time() - self.hotkey_click_time
        
        if time_since_last_usage < self.hotkey_suspend_interval:
            return
        
        if event.key == self.trigger_key:
            self.hotkey_click_time = time.time()
            
            if self.is_running():
                self.stop_recording(sender=self)
            else:
                self.begin_recording(sender=self)
    
    def noop_on_key_press(self, key):
        pass
    
    def update_events(self):
        actions = self.get_recorded_events_as_actions()
        actions.reverse()
        descriptions = self.description_parser.parse_actions(actions, group_options=Grouping(ScriptActionType.MOUSE_MOVE))
        self.widget.set_events_data(descriptions)

