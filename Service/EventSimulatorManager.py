from typing import Protocol
from kink import di
from Model.ScriptData import ScriptData
from Parser.ScriptActionParser import ScriptActionParserProtocol
from Service.Work.ScriptSimulationWorker import ScriptSimulationWorker, ScriptSimulationWorkerState
from Utilities.Logger import LoggerProtocol


class EventSimulatorDelegate(Protocol):
    def stop_script(self, sender): pass


class EventSimulatorManager:
    
    # - Init
    
    def __init__(self, script_data: ScriptData):
        self.delegate = None
        self.running = False
        self.script_data = script_data
        self.worker = None
        self.parser = di[ScriptActionParserProtocol]
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def get_delegate(self) -> EventSimulatorDelegate: return self.delegate
    def set_delegate(self, delegate): self.delegate = delegate
    def get_worker(self) -> ScriptSimulationWorker: return self.worker
    
    def is_running(self) -> bool:
        return self.running
    
    # - Actions
    
    def is_paused(self) -> bool:
        return self.worker.state() == ScriptSimulationWorkerState.PAUSED
    
    def start(self):
        assert self.delegate is not None
        assert not self.running
        
        self.logger.info('EventSimulatorManager start')
        
        self.running = True
        worker = ScriptSimulationWorker(self.script_data)
        worker.delegate = self
        worker.finished.connect(self.on_end)
        self.worker = worker
        worker.start()
    
    def cancel(self):
        assert self.running
        self.logger.info('EventSimulatorManager cancel')
        self.worker.cancel()
    
    def pause_script(self, sender):
        assert self.running
        self.logger.info('EventSimulatorManager pause')
        self.worker.pause()
    
    def resume_script(self, sender):
        assert self.running
        self.logger.info('EventSimulatorManager resume')
        self.worker.resume()
    
    def on_start(self): pass
    
    def on_end(self):
        self.running = False
        
        if not self.worker.is_cancelled():
            self.logger.info('EventSimulatorManager on end')
            self.delegate.stop_script(sender=self)
        else:
            self.logger.info('EventSimulatorManager on cancel')
    
    def current_action_index(self) -> int:
        return self.worker.current_action_index()
    
    def progress_fraction(self) -> float:
        current = self.worker.elapsed_time()
        duration = self.worker.duration()
        return current / duration if duration > 0 else 1
