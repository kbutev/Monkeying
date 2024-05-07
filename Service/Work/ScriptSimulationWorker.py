import enum
import threading
import time
from PyQt5.QtCore import QThread
from Service.Work.EventExecution import EventExecution
from Service.Work.EventExecutionBuilder import EventExecutionBuilder, EventExecutionBuilderProtocol
from Utilities.Timer import Timer

WAIT_INTERVAL = 2 # Time to wait (in ms) when idle
WAIT_INTERVAL_WHEN_PAUSED = 10

class ScriptSimulationWorkerState(enum.IntEnum):
    IDLE = 0
    RUNNING = 1
    PAUSED = 2
    FINISHED = 3

class ScriptSimulationWorker(QThread):
    events = []
    start_time = 0
    timer: Timer
    duration = 0
    event_index = 0
    
    _state = ScriptSimulationWorkerState.IDLE
    _cancelled = False
    
    current_execution: EventExecution = None
    
    lock = threading.Lock()
    
    builder: EventExecutionBuilderProtocol = EventExecutionBuilder()
    
    print_callback = None
    
    def __init__(self, events):
        super(ScriptSimulationWorker, self).__init__()
        self.events = events
        self.duration = self.events[len(self.events)-1].time()
        self.timer = Timer()
    
    def run(self):
        print('EventSimulatorWorker started')
        
        with self.lock:
            self.timer.start()
            
            self._state = ScriptSimulationWorkerState.RUNNING
        
        while self.state() != ScriptSimulationWorkerState.FINISHED:
            # Wait forever while paused until resumed
            while self.state() == ScriptSimulationWorkerState.PAUSED:
                self.msleep(WAIT_INTERVAL_WHEN_PAUSED)
                continue
            
            # Update current event until it finishes
            while self.is_executing_event():
                if self.current_execution.update():
                    self.msleep(WAIT_INTERVAL)
                else:
                    break
            
            # Try to execute the next event
            if len(self.events) == 0:
                self.mark_as_finished()
                break
            
            next_event = self.events[0]
            
            # If it's time, execute event
            if next_event.time() <= self.elapsed_time():
                self.current_execution = self.builder.build(next_event, self.print_callback)
                self.current_execution.execute()
                
                if not self.current_execution.update():
                    self.next_event()
            else:
                # Else, wait
                self.msleep(WAIT_INTERVAL)
        
        if not self.is_cancelled():
            self.print('EventSimulatorWorker ended')
        else:
            self.print('EventSimulatorWorker cancelled')
    
    def cancel(self):
        with self.lock:
            self.timer.stop()
            
            self._state = ScriptSimulationWorkerState.FINISHED
            self._cancelled = True
    
    def pause(self):
        with self.lock:
            self.timer.pause()
            
            self._state = ScriptSimulationWorkerState.PAUSED
    
    def resume(self):
        with self.lock:
            self.timer.resume()
            
            if self._state == ScriptSimulationWorkerState.PAUSED:
                self._state = ScriptSimulationWorkerState.RUNNING
    
    def state(self) -> ScriptSimulationWorkerState:
        with self.lock:
            result = self._state
        
        return result
    
    def mark_as_finished(self):
        with self.lock:
            self._state = ScriptSimulationWorkerState.FINISHED
    
    def is_cancelled(self):
        with self.lock:
            result = self._cancelled
        
        return result
    
    def current_event_index(self) -> int:
        with self.lock:
            result = self.event_index
        
        return result
    
    def increment_current_event_index(self):
        with self.lock:
            self.event_index += 1
    
    def is_executing_event(self):
        return self.current_execution is not None
    
    def next_event(self):
        self.events.pop(0)
        
        if len(self.events) > 0:
            self.increment_current_event_index()
    
    def elapsed_time(self) -> float:
        if self.state() == ScriptSimulationWorkerState.IDLE:
            return self.total_duration()
        
        return self.timer.elapsed_time()
    
    def time_elapsed_since_start(self) -> float:
        return time.time() - self.start_time
    
    def total_duration(self) -> float:
        return self.duration
    
    def on_complete(self, success):
        self.current_execution = None
    
    def print(self, message):
        if self.print_callback is not None:
            self.print_callback(message)
