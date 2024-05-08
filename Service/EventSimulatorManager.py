from typing import Protocol
from Parser.EventActionParser import EventActionParser, EventActionParserProtocol
from Service.EventStorage import EventStorage
from Service.Work.ScriptSimulationWorker import ScriptSimulationWorker, ScriptSimulationWorkerState


class EventSimulatorDelegate(Protocol):
    def stop_script(self, sender): pass

class EventSimulatorManager:
    delegate: EventSimulatorDelegate
    storage: EventStorage
    
    running = False
    worker: ScriptSimulationWorker
    
    parser: EventActionParserProtocol = EventActionParser()
    
    print_callback = print
    
    def __init__(self, storage):
        self.storage = storage
    
    def is_running(self) -> bool:
        return self.running
    
    def is_paused(self) -> bool:
        return self.worker.state() == ScriptSimulationWorkerState.PAUSED
    
    def start(self):
        assert self.delegate is not None
        assert not self.running
        
        print('EventSimulatorManager start')
        
        self.running = True
        data = list(map(lambda event: self.parser.parse_json(event), self.storage.data.copy()))
        worker = ScriptSimulationWorker(data)
        worker.print_callback = self.print_callback
        worker.delegate = self
        worker.finished.connect(self.on_end)
        self.worker = worker
        worker.start()
    
    def cancel(self):
        assert self.running
        print('EventSimulatorManager cancel')
        self.worker.cancel()
    
    def pause_script(self, sender):
        assert self.running
        print('EventSimulatorManager pause')
        self.worker.pause()
    
    def resume_script(self, sender):
        assert self.running
        print('EventSimulatorManager resume')
        self.worker.resume()
    
    def on_start(self): pass
    
    def on_end(self):
        self.running = False
        
        if not self.worker.is_cancelled():
            print('EventSimulatorManager on end')
            self.delegate.stop_script(sender=self)
        else:
            print('EventSimulatorManager on cancel')
    
    def current_event_index(self) -> int:
        return self.worker.current_event_index()
    
    def progress_fraction(self) -> float:
        current = self.worker.elapsed_time()
        duration = self.worker.duration()
        return current / duration if duration > 0 else 1
    
    def print(self, message):
        if self.print_callback is not None:
            self.print_callback(message)
