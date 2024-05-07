import time
from typing import Protocol

from PyQt5.QtCore import QTimer

from Parser.EventActionParser import EventActionToStringParserProtocol, EventActionToStringParser
from Presenter.Presenter import Presenter
from Service.EventMonitor import KeyboardEventMonitor
from Service.EventStorage import EventStorage
from Service.EventSimulatorManager import EventSimulatorManager
from OpenScriptView.RunScriptWidget import RunScriptWidgetProtocol
from pynput.keyboard import Key as KButton

from Utilities import Path


class RunScriptPresenterRouter(Protocol):
    def enable_tabs(self, enabled): pass

class RunScriptPresenter(Presenter):
    widget: RunScriptWidgetProtocol = None
    router: RunScriptPresenterRouter = None
    
    working_dir = 'scripts'
    file_format = 'json'
    
    storage_data = []
    script: str
    
    is_running = False
    
    simulator: EventSimulatorManager = None
    keyboard_monitor = KeyboardEventMonitor()
    
    event_parser: EventActionToStringParserProtocol = EventActionToStringParser()
    
    trigger_key = KButton.esc
    
    update_timer: QTimer
    
    # When used, the hotkey is suspended for a short period
    hotkey_click_time = 0
    hotkey_suspend_interval = 0.5
    
    def __init__(self, script):
        super(RunScriptPresenter, self).__init__()
        
        storage = EventStorage()
        storage.read_from_file(Path.combine(self.working_dir, script))
        self.storage_data = storage.data
        self.script = script
        
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(False)
        self.update_timer.setInterval(100)
        self.update_timer.timeout.connect(self.update_events)
    
    def start(self):
        self.keyboard_monitor.setup(self.noop_on_key_press, self.on_key_press)
        self.keyboard_monitor.start()
        
        events = list(map(lambda event: self.event_parser.parse(event), self.storage_data))
        self.widget.set_events_data(events)
        self.widget.update_progress(0, 0)
    
    def stop(self):
        if self.keyboard_monitor.is_running:
            self.keyboard_monitor.stop()
        
        if self.simulator is not None and self.simulator.is_running:
            self.simulator.cancel()
        
        self.is_running = False
        
        self.update_timer.stop()
    
    def is_script_active(self) -> bool:
        return self.is_running
    
    def can_run_script(self) -> bool:
        return not self.is_running
    
    def run_script(self, sender):
        assert self.widget is not None
        assert not self.is_running
        
        print('RunScriptPresenter run script')
        
        self.is_running = True
        storage = EventStorage()
        storage.data = self.storage_data
        self.simulator = EventSimulatorManager(storage)
        self.simulator.delegate = self
        self.simulator.start()

        self.update_timer.start()
        
        if sender is not self.widget and self.widget is not None:
            self.widget.run_script(sender=self)
    
    def stop_script(self, sender):
        assert self.is_running
        
        print('RunScriptPresenter stop script')
        self.update_events()
        
        self.is_running = False

        self.update_timer.stop()
        
        if sender is not self.simulator:
            self.simulator.cancel()
        
        if sender is not self.widget and self.widget is not None:
            # Always set sender=self, as the widget does not know about the simulator
            self.widget.stop_script(sender=self)
    
    def pause_script(self, sender):
        self.simulator.pause_script(sender)
        
    def resume_script(self, sender):
        self.simulator.resume_script(sender)
    
    def enable_tabs(self, value):
        self.router.enable_tabs(value)
    
    def on_key_press(self, event):
        time_since_last_usage = time.time() - self.hotkey_click_time
        
        if time_since_last_usage < self.hotkey_suspend_interval:
            return
        
        self.hotkey_click_time = time.time()
        
        if event.key == self.trigger_key:
            if self.is_running:
                self.stop_script(sender=self)
            else:
                print('RunScriptPresenter cancel script')
                self.run_script(sender=self)
    
    def noop_on_key_press(self, key):
        pass
    
    def update_events(self):
        index = self.simulator.current_event_index()
        progress = int(self.simulator.progress_fraction() * 100.0)
        #print(f'RunScriptPresenter update_events index={index} progress={progress}')
        self.widget.update_progress(index, progress)
