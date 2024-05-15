import time
from PyQt5.QtCore import QThread
from kink import di

from Service.ScriptStorage import ScriptStorage
from Service.EventMonitor import MouseEventMonitor, KeyboardEventMonitor
from Utilities.Logger import LoggerProtocol


class EventMonitorWorker(QThread):
    
    # - Init
    
    def __init__(self, storage: ScriptStorage):
        super(EventMonitorWorker, self).__init__()
        self.start_time = 0
        self.storage = storage
        self.filter_keys = []
        
        self.keyboard_monitor = di[KeyboardEventMonitor]
        self.keyboard_monitor.setup(self.on_keyboard_press, self.on_keyboard_release)
        
        self.mouse_monitor = di[MouseEventMonitor]
        self.mouse_monitor.setup(self.on_mouse_move, self.on_mouse_press, self.on_mouse_release, self.on_mouse_scroll)
        
        self.logger = di[LoggerProtocol]
    
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
        self.storage.record(event)
    
    def on_mouse_press(self, event):
        event.set_time(self.elapsed_time())
        self.storage.record(event)
    
    def on_mouse_release(self, event):
        event.set_time(self.elapsed_time())
        self.storage.record(event)
    
    def on_mouse_scroll(self, event):
        event.set_time(self.elapsed_time())
        self.storage.record(event)
    
    def on_keyboard_press(self, event):
        if event.key in self.filter_keys:
            return
        
        event.set_time(self.elapsed_time())
        self.storage.record(event)
    
    def on_keyboard_release(self, event):
        if event.key in self.filter_keys:
            return
        
        event.set_time(self.elapsed_time())
        self.storage.record(event)


class EventMonitorManager:
    
    # - Init
    
    def __init__(self, storage: ScriptStorage):
        self.storage = storage
        self.running = False
        self.worker = None
        self.filter_keys = []
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def is_running(self) -> bool:
        return self.running
    
    # - Actions
    
    def start(self):
        assert not self.running
        
        self.logger.info('EventMonitorManager start')
        
        self.running = True
        worker = EventMonitorWorker(self.storage)
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
