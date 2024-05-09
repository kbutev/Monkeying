import time
from typing import Protocol
from PyQt5.QtCore import QTimer
from Parser.EventActionParser import EventActionToStringParserProtocol, EventActionToStringParser
from Presenter.Presenter import Presenter
from Service.EventMonitor import KeyboardEventMonitor
from Service.EventStorage import EventStorage
from Service.EventSimulatorManager import EventSimulatorManager
from OpenScriptView.RunScriptWidget import RunScriptWidgetProtocol
from Service.SettingsManager import SettingsManagerField
from Service import SettingsManager
from Utilities import Path as PathUtils
from Utilities.Path import Path


class RunScriptPresenterRouter(Protocol):
    def enable_tabs(self, enabled): pass

class RunScriptPresenter(Presenter):
    widget: RunScriptWidgetProtocol = None
    router: RunScriptPresenterRouter = None
    
    working_dir: Path
    file_format: str
    
    storage = []
    script: str
    
    running = False
    
    simulator: EventSimulatorManager = None
    keyboard_monitor = KeyboardEventMonitor()
    
    event_parser: EventActionToStringParserProtocol = EventActionToStringParser()
    
    play_trigger_key = None
    pause_trigger_key = None
    
    update_timer: QTimer
    
    # When used, the hotkey is suspended for a short period
    hotkey_click_time = 0
    hotkey_suspend_interval = 0.5
    
    def __init__(self, script):
        super(RunScriptPresenter, self).__init__()
        
        settings = SettingsManager.singleton
        self.working_dir = settings.field_value(SettingsManagerField.SCRIPTS_PATH)
        self.file_format = settings.field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT)
        
        storage = EventStorage()
        storage.read_from_file(PathUtils.combine_paths(self.working_dir, script))
        self.storage = storage
        self.script = script
        
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(False)
        self.update_timer.setInterval(100)
        self.update_timer.timeout.connect(self.update_events)
    
    def start(self):
        settings = SettingsManager.singleton
        self.play_trigger_key = settings.field_value(SettingsManagerField.PLAY_HOTKEY)
        self.pause_trigger_key = settings.field_value(SettingsManagerField.PAUSE_HOTKEY)
        
        self.keyboard_monitor.setup(self.noop_on_key_press, self.on_key_press)
        self.keyboard_monitor.start()
        
        events = list(map(lambda event: self.event_parser.parse(event), self.storage.data))
        self.widget.set_events_data(events)
        self.widget.update_progress(0, 0)
    
    def stop(self):
        if self.keyboard_monitor.is_running():
            self.keyboard_monitor.stop()
        
        if self.simulator is not None and self.simulator.is_running():
            self.simulator.cancel()
        
        self.running = False
        
        self.update_timer.stop()
    
    def is_script_active(self) -> bool:
        return self.running
    
    def can_run_script(self) -> bool:
        return not self.running
    
    def run_script(self, sender):
        assert self.widget is not None
        assert not self.running
        
        print('RunScriptPresenter run script')
        
        self.running = True
        self.simulator = EventSimulatorManager(self.storage)
        self.simulator.delegate = self
        self.simulator.start()

        self.update_timer.start()
        
        if sender is not self.widget and self.widget is not None:
            self.widget.run_script(sender=self)
    
    def stop_script(self, sender):
        assert self.running
        
        print('RunScriptPresenter stop script')
        self.update_events()
        
        self.running = False
        
        self.update_timer.stop()
        
        if sender is not self.simulator:
            self.simulator.cancel()
        
        if sender is not self.widget and self.widget is not None:
            # Always set sender=self, as the widget does not know about the simulator
            self.widget.stop_script(sender=self)
    
    def pause_script(self, sender):
        self.simulator.pause_script(sender)
        
        if sender is not self.widget and self.widget is not None:
            # Always set sender=self, as the widget does not know about the simulator
            self.widget.pause_script(sender=self)
        else:
            assert sender is self.widget
    
    def resume_script(self, sender):
        self.simulator.resume_script(sender)
        
        if sender is not self.widget and self.widget is not None:
            # Always set sender=self, as the widget does not know about the simulator
            self.widget.resume_script(sender=self)
        else:
            assert sender is self.widget
    
    def enable_tabs(self, value):
        self.router.enable_tabs(value)
    
    def on_key_press(self, event):
        time_since_last_usage = time.time() - self.hotkey_click_time
        
        if time_since_last_usage < self.hotkey_suspend_interval:
            print('RunScriptPresenter hotkey pass')
            return
        
        if event.key == self.play_trigger_key:
            print('RunScriptPresenter play hotkey triggered')
            
            if self.running:
                self.stop_script(sender=self)
            else:
                self.run_script(sender=self)
        elif event.key == self.pause_trigger_key and self.running:
            print('RunScriptPresenter pause hotkey triggered')
            
            if self.simulator.is_paused():
                self.resume_script(sender=self)
            else:
                self.pause_script(sender=self)
        else:
            return
        
        # Update timer only when hotkey is used
        self.hotkey_click_time = time.time()
    
    def noop_on_key_press(self, key):
        pass
    
    def update_events(self):
        index = self.simulator.current_event_index()
        progress = int(self.simulator.progress_fraction() * 100.0)
        #print(f'RunScriptPresenter update_events index={index} progress={progress}')
        self.widget.update_progress(index, progress)
