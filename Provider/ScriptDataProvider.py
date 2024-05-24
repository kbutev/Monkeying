from typing import Protocol
from kink import di
from Service.ScriptStorage import ScriptStorage
from Service.ThreadWorkerManager import ThreadWorkerManagerProtocol
from Utilities.Path import Path
from Utilities.Threading import run_in_background_with_result


THREAD_WORKER_FETCH_LABEL = 'fetch'


class ScriptDataProviderProtocol(Protocol):
    def get_file_path(self) -> Path: return None
    def fetch(self, completion, failure): pass


class ScriptDataProvider(ScriptDataProviderProtocol):
    
    def __init__(self, file_path: Path):
        assert file_path is not None
        self.storage = ScriptStorage(file_path)
        self.thread_worker_manager = di[ThreadWorkerManagerProtocol]
    
    def get_file_path(self) -> Path: return self.storage.get_file_path()
    
    def fetch(self, completion, failure):
        if self.thread_worker_manager.is_running_worker(THREAD_WORKER_FETCH_LABEL):
            return
        
        worker = run_in_background_with_result(self.read_storage_data,
                                               lambda result: self.handle_completion(result, completion, failure))
        self.thread_worker_manager.add_worker(worker, THREAD_WORKER_FETCH_LABEL)
    
    def read_storage_data(self):
        try:
            return self.storage.read_script_data_from_file()
        except Exception as error:
            return error
    
    def handle_completion(self, result, completion, failure):
        self.thread_worker_manager.remove_worker(THREAD_WORKER_FETCH_LABEL)
        
        if isinstance(result, Exception):
            failure(result)
        else:
            completion(result)
