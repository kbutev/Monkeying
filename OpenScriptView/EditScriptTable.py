from PyQt5.QtWidgets import *
from MainView.RecordScriptTable import RecordScriptTableDataSource, RecordScriptTable


class EditScriptTableDataSource(RecordScriptTableDataSource):
    pass


class EditScriptTable(RecordScriptTable):
    def __init__(self, parent=None):
        super(EditScriptTable, self).__init__(parent)
    
    def setup(self):
        super(EditScriptTable, self).setup()

