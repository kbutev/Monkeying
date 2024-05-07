from typing import Protocol
from Parser.EventActionParser import EventActionParser, EventActionParserProtocol
from Service.EventStorage import EventStorage
from Service.Work.ScriptSimulationWorker import ScriptSimulationWorker


class EventSimulatorDelegate(Protocol):
    def stop_script(self, sender): pass

class EventSimulatorManager:
    delegate: EventSimulatorDelegate
    storage: EventStorage
    
    is_running = False
    worker: ScriptSimulationWorker
    
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
        worker = ScriptSimulationWorker(data)
        worker.print_callback = self.print_callback
        worker.delegate = self
        worker.finished.connect(self.on_end)
        self.worker = worker
        worker.start()
    
    def cancel(self):
        assert self.is_running
        print('EventSimulatorManager cancel')
        self.worker.cancel()
    
    def pause_script(self, sender):
        assert self.is_running
        print('EventSimulatorManager pause')
        self.worker.pause()
    
    def resume_script(self, sender):
        assert self.is_running
        print('EventSimulatorManager resume')
        self.worker.resume()
    
    def on_start(self): pass
    
    def on_end(self):
        self.is_running = False
        
        if not self.worker.is_cancelled():
            print('EventSimulatorManager on end')
            self.delegate.stop_script(sender=self)
        else:
            print('EventSimulatorManager on cancel')
    
    def current_event_index(self) -> int:
        return self.worker.current_event_index()
    
    def progress_fraction(self) -> float:
        current = self.worker.elapsed_time()
        duration = self.worker.total_duration()
        return current / duration if duration > 0 else 1
    
    def print(self, message):
        if self.print_callback is not None:
            self.print_callback(message)
