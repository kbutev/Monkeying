import threading
from typing import Any

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QThread


class MainThreadSignalWorker(QtCore.QObject):
    sig_no_args = QtCore.pyqtSignal()
    
    def run_on_main(self, callback):
        self.sig_no_args.connect(callback)


class SimpleWorker(QThread):
    # Signal automatically binds to every unique instance
    signal_main = pyqtSignal(int, name='ThreadSignal.on_finish')
    
    def __init__(self, process, completion):
        super(SimpleWorker, self).__init__()
        self.process = process
        self.completion = completion
        self.signal_main.connect(self.on_finish)
        self.result = None
    
    def run(self):
        self.result = self.process()
        self.process = None
        self.signal_main.emit(True)
    
    def on_finish(self, result):
        if self.completion is not None:
            self.completion(self.result)
            self.result = None
            self.completion = None


def current_thread_is_main(): return threading.current_thread() is threading.main_thread()
    

def run_on_main(handle):
    if current_thread_is_main():
        handle()
        return
    
    worker = MainThreadSignalWorker()
    worker.run_on_main(handle)


def run_in_background(process_handle, completion_on_main_handle=None):
    worker = SimpleWorker(process_handle, completion_on_main_handle)
    worker.start()

