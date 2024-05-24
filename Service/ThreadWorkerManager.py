from typing import Protocol
from kink import inject


class ThreadWorkerManagerProtocol(Protocol):
    def is_running_worker(self, label: str) -> bool: return False
    def add_worker(self, worker, label: str): pass
    def remove_worker(self, label: str): pass


@inject(use_factory=True, alias=ThreadWorkerManagerProtocol)
class ThreadWorkerManager(ThreadWorkerManagerProtocol):
    
    def __init__(self):
        self.workers = {}

    def is_running_worker(self, label: str) -> bool:
        return label in self.workers
    
    def add_worker(self, worker, label: str):
        assert label not in self.workers # Already added
        self.workers[label] = worker
    
    def remove_worker(self, label):
        assert label in self.workers
        del self.workers[label]
