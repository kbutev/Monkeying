import enum
import threading
import time

from PyQt5.QtCore import QThread
from Model.ScriptConfiguration import ScriptConfiguration
from Service.OSNotification import OSNotification
from Service.ScriptStorage import ScriptStorage
from Service.Work.EventExecution import ScriptExecution
from Service.Work.EventExecutionBuilder import EventExecutionBuilder
from Utilities.Path import Path

NOTIFICATION_TITLE = 'Monkeying'
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
    
    script_path: Path
    events = []
    current_execution: ScriptExecution = None
    execution_count = 0
    execution_limit = 1
    configuration: ScriptConfiguration
    
    lock = threading.Lock()
    
    print_callback = None
    
    def __init__(self, storage: ScriptStorage, event_parser):
        super(ScriptSimulationWorker, self).__init__()
        self.script_path = storage.file_path
        self.events = list(map(lambda event: event_parser.parse_json(event), storage.data.copy()))
        self.configuration = storage.configuration
        
        if self.configuration.repeat_forever:
            self.execution_limit = None
        else:
            self.execution_limit = 1 + self.configuration.repeat_count
        
        self.current_execution = self.build_execution_script()
    
    def state(self) -> ScriptSimulationWorkerState:
        with self.lock:
            result = self._state
        
        return result
    
    def current_event_index(self) -> int:
        with self.lock:
            result = self.current_execution.current_event_index()
        
        return result
    
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
    
    def build_execution_script(self) -> ScriptExecution:
        return ScriptExecution(self.script_path, self.events.copy(), EventExecutionBuilder())
    
    def run(self):
        assert self._state is ScriptSimulationWorkerState.IDLE
        
        print('EventSimulatorWorker started')
        
        self.current_execution.print_callback = self.print_callback
        
        with self.lock:
            self._state = ScriptSimulationWorkerState.RUNNING
            self.execution_count += 1
        
        self.show_start_notification()
        self.current_execution.execute(None)
        
        while self.state() != ScriptSimulationWorkerState.FINISHED:
            # Wait forever while paused until resumed
            while self.state() == ScriptSimulationWorkerState.PAUSED:
                self.msleep(WAIT_INTERVAL_WHEN_PAUSED)
                continue
            
            with self.lock:
                running = self.current_execution.update()
            
            if not running:
                self.mark_as_finished()
        
        self.show_end_notification()
        
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
            # None = repeat forever
            if self.execution_limit is not None and self.execution_count >= self.execution_limit:
                self._state = ScriptSimulationWorkerState.FINISHED
            else:
                self.execution_count += 1
                start_time = self.current_execution.start_time
                self.current_execution = self.build_execution_script()
                self.current_execution.execute(self)
                self.current_execution.start_time = start_time
    
    def script_name(self) -> str:
        return self.script_path.last_component()
    
    def show_start_notification(self):
        if not self.configuration.notify_on_start:
            return
        
        notification = OSNotification(NOTIFICATION_TITLE, f'{self.script_name()} started')
        notification.show()
    
    def show_end_notification(self):
        if not self.configuration.notify_on_end:
            return
        
        notification = OSNotification(NOTIFICATION_TITLE, f'{self.script_name()} ended')
        notification.show()
    
    def print(self, message):
        if self.print_callback is not None:
            self.print_callback(message)
