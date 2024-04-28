from PyQt5.QtWidgets import *
from MainView.RecordScriptTable import RecordScriptTableDataSource, RecordScriptTable


class RunScriptTableDataSource(RecordScriptTableDataSource):
    pass


class RunScriptTable(RecordScriptTable):
    def __init__(self, parent=None):
        super(RunScriptTable, self).__init__(parent)
        
    def setup(self):
        super(RunScriptTable, self).setup()

