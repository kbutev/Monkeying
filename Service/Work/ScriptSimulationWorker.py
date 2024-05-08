import enum
import threading
from PyQt5.QtCore import QThread
from Service.Work.EventExecution import ScriptExecution
from Service.Work.EventExecutionBuilder import EventExecutionBuilder

WAIT_INTERVAL = 2 # Time to wait (in ms) when idle
WAIT_INTERVAL_WHEN_PAUSED = 10

class ScriptSimulationWorkerState(enum.IntEnum):
    IDLE = 0
    RUNNING = 1
    PAUSED = 2
    FINISHED = 3

class ScriptSimulationWorker(QThread):
    _state = ScriptSimulationWorkerState.IDLE
    _cancelled = False
    
    current_execution: ScriptExecution = None
    
    lock = threading.Lock()
    
    print_callback = None
    
    def __init__(self, events):
        super(ScriptSimulationWorker, self).__init__()
        self.current_execution = ScriptExecution(events, EventExecutionBuilder())
    
    def state(self) -> ScriptSimulationWorkerState:
        with self.lock:
            result = self._state
        
        return result
    
    def current_event_index(self) -> int:
        return self.current_execution.current_event_index()
    
    def is_cancelled(self):
        with self.lock:
            result = self._cancelled
        
        return result
    
    def elapsed_time(self) -> float:
        if self.state() == ScriptSimulationWorkerState.FINISHED:
            return self.duration()
        
        return self.current_execution.elapsed_time()
    
    def time_elapsed_since_start(self) -> float:
        return self.current_execution.time_elapsed_since_start()
    
    def duration(self) -> float:
        return self.current_execution.duration()
    
    def run(self):
        assert self._state is ScriptSimulationWorkerState.IDLE
        
        print('EventSimulatorWorker started')
        
        self.current_execution.print_callback = self.print_callback
        
        with self.lock:
            self._state = ScriptSimulationWorkerState.RUNNING
        
        self.current_execution.execute()
        
        while self.state() != ScriptSimulationWorkerState.FINISHED:
            # Wait forever while paused until resumed
            while self.state() == ScriptSimulationWorkerState.PAUSED:
                self.msleep(WAIT_INTERVAL_WHEN_PAUSED)
                continue
            
            if not self.current_execution.update():
                self.mark_as_finished()
        
        if not self.is_cancelled():
            self.print('EventSimulatorWorker ended')
        else:
            self.print('EventSimulatorWorker cancelled')
    
    def cancel(self):
        with self.lock:
            if self.current_execution.is_running():
                self.current_execution.pause()
            
            self._state = ScriptSimulationWorkerState.FINISHED
            self._cancelled = True
    
    def pause(self):
        with self.lock:
            if self.current_execution.is_running():
                self.current_execution.pause()
            
            self._state = ScriptSimulationWorkerState.PAUSED
    
    def resume(self):
        with self.lock:
            self.current_execution.resume()
            
            if self._state == ScriptSimulationWorkerState.PAUSED:
                self._state = ScriptSimulationWorkerState.RUNNING
    
    def mark_as_finished(self):
        with self.lock:
            self._state = ScriptSimulationWorkerState.FINISHED
    
    def print(self, message):
        if self.print_callback is not None:
            self.print_callback(message)
