
from PyQt5 import QtCore

class ThreadSignal(QtCore.QObject):
    ''' Why a whole new class? See here: 
    https://stackoverflow.com/a/25930966/2441026 '''
    sig_no_args = QtCore.pyqtSignal()
    
    def run_on_main(self, callback):
        self.sig_no_args.connect(callback)
