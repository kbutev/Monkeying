import threading
import time
from PyQt5.QtCore import QThread
from kink import di

from Model.ScriptEvents import ScriptEvents
from Service.ScriptStorage import ScriptStorage
from Service.EventMonitor import MouseEventMonitor, KeyboardEventMonitor
from Utilities.Logger import LoggerProtocol


class EventMonitorWorker(QThread):
    
    # - Init
    
    def __init__(self):
        super(EventMonitorWorker, self).__init__()
        
        self.lock = threading.Lock()
        
        self.events = ScriptEvents([])
        self.start_time = 0
        self.filter_keys = []
        
        self.keyboard_monitor = di[KeyboardEventMonitor]
        self.keyboard_monitor.setup(self.on_keyboard_press, self.on_keyboard_release)
        
        self.mouse_monitor = di[MouseEventMonitor]
        self.mouse_monitor.setup(self.on_mouse_move, self.on_mouse_press, self.on_mouse_release, self.on_mouse_scroll)
        
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def get_events(self) -> ScriptEvents:
        with self.lock:
            result = ScriptEvents(self.events.data.copy())
        
        return result
    
    def set_events(self, events):
        with self.lock:
            self.events = events
    
    # - Actions
    
    def run(self):
        self.logger.info('EventMonitorWorker started')
        self.start_time = time.time()
        self.mouse_monitor.start()
        self.keyboard_monitor.start()
        self.keyboard_monitor.join()
        self.logger.info('EventMonitorWorker exited')
    
    def stop(self):
        self.mouse_monitor.stop()
        self.mouse_monitor.reset()
        self.keyboard_monitor.stop()
        self.keyboard_monitor.reset()
    
    def elapsed_time(self) -> float:
        return time.time() - self.start_time
    
    def on_mouse_move(self, event):
        event.set_time(self.elapsed_time())
        self.events.data.append(event)
    
    def on_mouse_press(self, event):
        event.set_time(self.elapsed_time())
        self.events.data.append(event)
    
    def on_mouse_release(self, event):
        event.set_time(self.elapsed_time())
        self.events.data.append(event)
    
    def on_mouse_scroll(self, event):
        event.set_time(self.elapsed_time())
        self.events.data.append(event)
    
    def on_keyboard_press(self, event):
        if event.key in self.filter_keys:
            return
        
        event.set_time(self.elapsed_time())
        self.events.data.append(event)
    
    def on_keyboard_release(self, event):
        if event.key in self.filter_keys:
            return
        
        event.set_time(self.elapsed_time())
        self.events.data.append(event)


class EventMonitorManager:
    
    # - Init
    
    def __init__(self):
        self.running = False
        self.worker = None
        self.events = []
        self.filter_keys = []
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def is_running(self) -> bool: return self.running
    
    def get_events(self) -> ScriptEvents:
        assert self.worker is not None
        return self.worker.get_events()
    
    def set_events(self, events):
        assert self.worker is not None
        self.worker.set_events(events)
    
    # - Actions
    
    def start(self):
        assert not self.running
        
        self.logger.info('EventMonitorManager start')
        
        self.running = True
        worker = EventMonitorWorker()
        worker.filter_keys = self.filter_keys
        worker.finished.connect(self.on_stop)
        self.worker = worker
        worker.start()
    
    def stop(self):
        assert self.running
        self.logger.info('EventMonitorManager stop')
        self.worker.stop()
    
    def on_stop(self):
        assert self.running
        self.logger.info('EventMonitorManager on stop')
        self.running = False
