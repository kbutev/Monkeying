import time
from typing import Protocol
from PyQt5.QtCore import QTimer
from Model.InputEventType import InputEventType
from Parser.EventActionParser import EventActionToStringParser, EventActionToStringParserProtocol, \
    EventActionToStringParserGrouping
from Presenter.Presenter import Presenter
from Service.EventMonitor import KeyboardEventMonitor
from Service.EventMonitorManager import EventMonitorManager
from MainView.RecordScriptWidget import RecordScriptWidgetProtocol
from Service.ScriptStorage import ScriptStorage
from Service.SettingsManager import SettingsManagerField
from Service import SettingsManager
from Utilities.Path import Path


class RecordScriptPresenterRouter(Protocol):
    def enable_tabs(self, value): pass
    def pick_save_file(self, directory) -> Path: pass
    def configure_script(self, script_path, parent): pass

class RecordScriptPresenter(Presenter):
    router: RecordScriptPresenterRouter = None
    widget: RecordScriptWidgetProtocol = None
    
    storage = ScriptStorage()
    event_monitor = EventMonitorManager(storage)
    keyboard_monitor = KeyboardEventMonitor()
    
    running = False
    
    file_format = '.json'
    
    trigger_key = None
    
    events_data = []
    
    event_parser: EventActionToStringParserProtocol = EventActionToStringParser()
    
    update_timer: QTimer
    
    # When used, the hotkey is suspended for a short period
    hotkey_click_time = 0
    hotkey_suspend_interval = 0.5
    
    def __init__(self):
        super(RecordScriptPresenter, self).__init__()
        self.event_monitor.delegate = self
        
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(False)
        self.update_timer.setInterval(100)
        self.update_timer.timeout.connect(self.update_events)
    
    def is_running(self) -> bool:
        return self.running
    
    def start(self):
        self.trigger_key = SettingsManager.singleton.field_value(SettingsManagerField.RECORD_HOTKEY)
        
        self.keyboard_monitor = KeyboardEventMonitor()
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
    
    def enable_tabs(self, value):
        self.router.enable_tabs(value)
    
    def begin_recording(self, sender):
        assert not self.running
        assert self.widget is not None
        
        print('RecordScriptPresenter begin')
        
        self.running = True
        self.storage.clear()
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
        
        print('RecordScriptPresenter stop recording')
        
        self.running = False
        self.event_monitor.stop()
        self.update_timer.stop()
        
        # If command was initiated by the widget, do not forward it back
        if sender is not self.widget:
            self.widget.stop_recording(sender=self)
    
    def configure_script(self):
        self.router.configure_script(self.widget, self.storage)
    
    def save_recording(self):
        assert self.router is not None
        
        print(f'RecordScriptPresenter save {self.storage.info.name}')
        scripts_dir = SettingsManager.singleton.field_value(SettingsManagerField.SCRIPTS_PATH)
        file = self.router.pick_save_file(scripts_dir)
        
        if file is None:
            return
        
        if not file.absolute.endswith(self.file_format):
            file.append_to_end(self.file_format)
        
        # When name is not set, set it to equal file name
        if self.storage.info.is_name_default():
            self.storage.info.name = file.stem()
        
        self.storage.write_to_file(path=file)
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
        storage_data = self.storage.data.copy()
        events = self.event_parser.parse_list(reversed(storage_data), group_options=EventActionToStringParserGrouping(InputEventType.MOUSE_MOVE))
        self.widget.set_events_data(events)

