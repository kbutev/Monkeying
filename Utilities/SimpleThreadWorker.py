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


class SignalMain(QtCore.QObject):
    signal = QtCore.pyqtSignal(object)
    
    def __init__(self):
        assert current_thread_is_main() # Main signal must be initialized on the main thread!
        super(SignalMain, self).__init__()
        self.signal.connect(self._perform_on_main)
    
    def emit(self, handle):
        self.signal.emit(handle)
    
    def _perform_on_main(self, handle):
        handle()


main_signal = SignalMain()


class SimpleMainThreadWorker(QtCore.QObject):
    def __init__(self, handle):
        super(SimpleMainThreadWorker, self).__init__()
        self.handle = handle
    
    def start(self):
        main_signal.emit(self.run_on_main)
    
    def run_on_main(self):
        assert current_thread_is_main()
        self.handle()
        self.handle = None


class SimpleThreadWorker(QThread):
    
    def __init__(self, process, completion, process_with_param=None, completion_with_result=False):
        super(SimpleThreadWorker, self).__init__()
        self.process = process
        self.completion = completion
        self.process_with_param = process_with_param
        self.completion_with_result = completion_with_result
        self.result = None
        self.completion_worker = None
    
    def run(self):
        if self.completion_with_result:
            self.result = self.perform_process()
        else:
            self.perform_process()
        
        self.completion_worker = run_on_main(self.on_finish)
    
    def perform_process(self):
        assert not current_thread_is_main()
        
        if self.process_with_param is not None:
            result = self.process(self.process_with_param)
        else:
            result = self.process()
        
        self.process = None
        self.process_with_param = None
        
        return result
    
    def on_finish(self):
        assert current_thread_is_main()
        
        if self.completion is not None:
            if self.completion_with_result:
                self.completion(self.result)
            else:
                self.completion()
            
            self.completion = None
        
        self.result = None
        self.completion_worker = None
