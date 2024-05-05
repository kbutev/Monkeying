import threading
import time
from typing import Protocol
from PyQt5.QtCore import QThread

from Model.InputEvent import InputEvent
from Model.JSONInputEvent import JSONInputEvent
from Parser.EventActionParser import EventActionParser, EventActionParserProtocol
from Service.EventStorage import EventStorage
from Service.EventSimulator import MouseEventSimulator, KeyboardEventSimulator

class EventSimulatorWorker(QThread):
    cancelled = True
    
    events = []
    start_time = 0
    event_index = 0
    wait_interval = 2 # Time to wait (in ms) when loop finishes
    
    mouse_simulator = MouseEventSimulator()
    keyboard_simulator = KeyboardEventSimulator()
    
    _is_running = True
    lock = threading.Lock()
    
    print_callback = None
    
    def __init__(self, events):
        super(EventSimulatorWorker, self).__init__()
        self.events = events
    
    def run(self):
        print('EventSimulatorWorker started')
        self.mouse_simulator.print_callback = self.print_callback
        self.keyboard_simulator.print_callback = self.print_callback
        self.start_time = time.time()
        
        while self.is_running() and len(self.events) > 0:
            next_event = self.events[0]
            
            if next_event.time() <= self.elapsed_time():
                self.simulate_event(next_event)
                self.events.pop(0)
                
                if len(self.events) > 0:
                    self.increment_current_event_index()
            else:
                self.msleep(self.wait_interval)
        
        self.cancelled = not self.is_running()
        
        if not self.cancelled:
            self.print('EventSimulatorWorker ended')
        else:
            self.print('EventSimulatorWorker cancelled')
    
    def is_running(self) -> bool:
        with self.lock: 
            result = self._is_running
        
        return result
    
    def current_event_index(self) -> int:
        with self.lock:
            result = self.event_index
        
        return result
    
    def increment_current_event_index(self):
        with self.lock:
            self.event_index += 1
    
    def cancel(self):
        with self.lock:
            self._is_running = False
    
    def elapsed_time(self) -> float:
        return time.time() - self.start_time
    
    def simulate_event(self, event: InputEvent):
        self.print(f'simulate {event.event_type().name} : {event.value_as_string()}')
        
        if event.event_type().is_keyboard():
            self.keyboard_simulator.simulate(event)
        else:
            self.mouse_simulator.simulate(event)
    
    def print(self, message):
        if self.print_callback is not None:
            self.print_callback(message)

class EventSimulatorDelegate(Protocol):
    def stop_script(self, sender): pass

class EventSimulatorManager:
    delegate: EventSimulatorDelegate
    storage: EventStorage
    
    is_running = False
    worker: EventSimulatorWorker
    
    parser: EventActionParserProtocol = EventActionParser()
    
    print_callback = print
    
    def __init__(self, storage):
        self.storage = storage
    
    def start(self):
        assert self.delegate is not None
        assert not self.is_running
        
        print('EventSimulatorManager start')
        
        self.is_running = True
        data = list(map(lambda event: self.parser.parse_json(event), self.storage.data.copy()))
        worker = EventSimulatorWorker(data)
        worker.print_callback = self.print_callback
        worker.delegate = self
        worker.finished.connect(self.on_end)
        self.worker = worker
        worker.start()
    
    def cancel(self):
        assert self.is_running
        print('EventSimulatorManager cancel')
        self.worker.cancel()
    
    def on_start(self): pass
    
    def on_end(self):
        self.is_running = False
        
        if not self.worker.cancelled:
            print('EventSimulatorManager on end')
            self.delegate.stop_script(sender=self)
        else:
            print('EventSimulatorManager on cancel')
    
    def current_event_index(self) -> int:
        return self.worker.current_event_index()
    
    def progress_fraction(self) -> float:
        index = self.current_event_index() + 1
        length = len(self.storage.data)
        return float(index) / float(length) if length > 0 else 0
    
    def print(self, message):
        if self.print_callback is not None:
            self.print_callback(message)
