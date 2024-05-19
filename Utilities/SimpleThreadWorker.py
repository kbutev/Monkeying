import threading
from typing import Any

from PyQt5 import QtCore
from PyQt5.QtCore import QThread


def current_thread_is_main(): return threading.current_thread() is threading.main_thread()


def get_current_thread_name():
    return 'main' if current_thread_is_main() else threading.get_ident()


def get_current_thread_description():
    return f'thread.{get_current_thread_name()}'


def run_on_main(handle) -> Any:
    if current_thread_is_main():
        handle()
        return None
    
    worker = SimpleMainThreadWorker(handle)
    worker.start()
    return worker


class SimpleMainThreadWorker(QtCore.QObject):
    main_signal = QtCore.pyqtSignal()
    
    def __init__(self, handle):
        super(SimpleMainThreadWorker, self).__init__()
        self.handle = handle
        self.main_signal.connect(self.run_on_main)
    
    def start(self):
        self.main_signal.emit()
    
    def run_on_main(self):
        self.handle()
        self.handle = None


class SimpleThreadWorker(QThread):
    
    def __init__(self, process, completion, completion_with_result):
        super(SimpleThreadWorker, self).__init__()
        self.process = process
        self.completion = completion
        self.completion_with_result = completion_with_result
        self.result = None
        self.completion_worker = None
    
    def run(self):
        if self.completion_with_result:
            self.result = self.process()
        else:
            self.process()
        
        self.process = None
        
        self.completion_worker = run_on_main(self.on_finish)
    
    def on_finish(self):
        if self.completion is not None:
            if self.completion_with_result:
                self.completion(self.result)
            else:
                self.completion()
            
            self.completion = None
        
        self.result = None
        self.completion_worker = None
