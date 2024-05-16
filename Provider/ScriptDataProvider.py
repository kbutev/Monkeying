from typing import Protocol

from PyQt5.QtCore import QThread, pyqtSignal

from Model.ScriptData import ScriptData
from Service.ScriptStorage import ScriptStorage
from Utilities.Path import Path


class ScriptDataProviderProtocol(Protocol):
    def get_file_path(self) -> Path: return None
    def fetch(self, completion, failure): pass


class ScriptDataProviderWorker(QThread):
    
    # Signal automatically binds to every unique instance
    signal_main = pyqtSignal(ScriptData, name='ScriptDataProviderWorker.on_finish')
    
    def __init__(self, storage: ScriptStorage, completion, failure):
        super(ScriptDataProviderWorker, self).__init__()
        self.storage = storage
        self.completion = completion
        self.failure = failure
        self.signal_main.connect(self.on_finish)
    
    def run(self):
        self.signal_main.emit(self.storage.read_from_file())
    
    def on_finish(self, result):
        if result is None:
            self.failure(result)
        else:
            self.completion(result)
        
        self.completion = None
        self.failure = None


class ScriptDataProvider(ScriptDataProviderProtocol):
    
    def __init__(self, file_path: Path):
        assert file_path is not None
        self.storage = ScriptStorage(file_path)
    
    def get_file_path(self) -> Path: return self.storage.get_file_path()
    
    def fetch(self, completion, failure):
        worker = ScriptDataProviderWorker(self.storage, completion, failure)
        worker.start()
