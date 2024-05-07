
import time
from PyQt5.QtCore import QThread
from Service.EventStorage import EventStorage
from Service.EventMonitor import MouseEventMonitor, KeyboardEventMonitor

class EventMonitorWorker(QThread):
    storage: EventStorage
    
    start_time = 0
    
    keyboard_monitor = KeyboardEventMonitor()
    mouse_monitor = MouseEventMonitor()
    
    filter_keys = []
    
    def __init__(self, storage):
        super(EventMonitorWorker, self).__init__()
        self.storage = storage
        self.keyboard_monitor.setup(self.on_keyboard_press, self.on_keyboard_release)
        self.keyboard_monitor.print_callback = print
        self.mouse_monitor.setup(self.on_mouse_move, self.on_mouse_press, self.on_mouse_release, self.on_mouse_scroll)
        self.mouse_monitor.print_callback = print
    
    def run(self):
        print('EventMonitorWorker started')
        self.start_time = time.time()
        self.mouse_monitor.start()
        self.keyboard_monitor.start()
        self.keyboard_monitor.join()
        print('EventMonitorWorker exited')
    
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
    storage: EventStorage
    
    running = False
    worker: EventMonitorWorker
    
    filter_keys = []
    
    def __init__(self, storage):
        self.storage = storage
    
    def is_running(self) -> bool:
        return self.running
    
    def start(self):
        assert not self.running
        
        print('EventMonitorManager start')
        
        self.running = True
        worker = EventMonitorWorker(self.storage)
        worker.filter_keys = self.filter_keys
        worker.finished.connect(self.on_stop)
        self.worker = worker
        worker.start()
    
    def stop(self):
        assert self.running
        print('EventMonitorManager stop')
        self.worker.stop()
    
    def on_stop(self):
        assert self.running
        print('EventMonitorManager on stop')
        self.running = False
