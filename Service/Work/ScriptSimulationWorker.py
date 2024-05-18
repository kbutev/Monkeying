import enum
import threading
from PyQt5.QtCore import QThread
from kink import di
from Model.ScriptConfiguration import ScriptConfiguration
from Model.ScriptData import ScriptData
from Model.ScriptInfo import ScriptInfo
from Parser.ScriptActionParser import ScriptActionParserProtocol
from Service.OSNotificationCenter import OSNotificationCenterProtocol
from Service.Work.ScriptActionExecutionBuilder import ScriptActionExecutionBuilderProtocol
from Service.Work.ScriptActionExecutionCluster import ScriptActionScriptExecution
from Utilities.Logger import LoggerProtocol


NOTIFICATION_TITLE = 'Monkeying'
WAIT_INTERVAL = 2 # Time to wait (in ms) when idle
WAIT_INTERVAL_WHEN_PAUSED = 10


class ScriptSimulationWorkerState(enum.IntEnum):
    IDLE = 0
    RUNNING = 1
    PAUSED = 2
    FINISHED = 3


class ScriptSimulationWorker(QThread):
    
    # - Init
    
    def __init__(self, script_data: ScriptData):
        super(ScriptSimulationWorker, self).__init__()
        
        self.lock = threading.Lock()
        
        self._state = ScriptSimulationWorkerState.IDLE
        self._cancelled = False
        
        self.script_data = script_data.copy()
        self.script_path = script_data.file_path
        self.action_parser = di[ScriptActionParserProtocol]
        
        self.execution_count = 0
        
        if self.script_config().repeat_forever:
            self.execution_limit = None
        else:
            self.execution_limit = 1 + self.script_config().repeat_count
        
        self.current_execution = self.build_execution_script()
        
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def script_info(self) -> ScriptInfo:
        return self.script_data.info
    
    def script_config(self) -> ScriptConfiguration:
        return self.script_data.config
    
    def state(self) -> ScriptSimulationWorkerState:
        with self.lock:
            result = self._state
        
        return result
    
    def current_action_index(self) -> int:
        with self.lock:
            result = self.current_execution.current_action_index()
        
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
    
    def build_execution_script(self) -> ScriptActionScriptExecution:
        builder = di[ScriptActionExecutionBuilderProtocol]
        return ScriptActionScriptExecution(self.script_path, self.script_data.get_actions(), builder)
    
    def notification_center(self) -> OSNotificationCenterProtocol:
        return di[OSNotificationCenterProtocol]
    
    # - Actions
    
    def run(self):
        assert self._state is ScriptSimulationWorkerState.IDLE
        
        self.logger.info('ScriptSimulatorWorker started')
        
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
            self.logger.info('ScriptSimulatorWorker ended')
        else:
            self.logger.info('ScriptSimulatorWorker cancelled')
    
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
    
    def show_start_notification(self):
        if not self.script_config().notify_on_start:
            return
        
        self.notification_center().show(NOTIFICATION_TITLE, f'{self.script_info().name} started')
    
    def show_end_notification(self):
        if not self.script_config().notify_on_end:
            return
        
        self.notification_center().show(NOTIFICATION_TITLE, f'{self.script_info().name} ended')
