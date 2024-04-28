from PyQt5.QtWidgets import *

from Model.InputEvent import InputEventDescription


class RecordScriptTableDataSource:
    data = []
    file_format = 'json'
    
    def count(self) -> int:
        return len(self.data)
    
    def item(self, column, row) -> QTableWidgetItem:
        assert column <= 2
        
        entry: InputEventDescription = self.data[row]
        
        match column:
            case 0: return QTableWidgetItem(entry.time)
            case 1: return QTableWidgetItem(entry.type)
            case 2: return QTableWidgetItem(entry.value)


class RecordScriptTable(QTableWidget):
    COLUMNS = 3
    
    data_source: RecordScriptTableDataSource
    
    def __init__(self, parent=None):
        super(RecordScriptTable, self).__init__(parent)
        self.setup()
    
    def setup(self):
        self.setColumnCount(self.COLUMNS)
        self.setRowCount(0)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
    
    def update_data(self):
        if self.data_source is not None:
            self.setRowCount(self.data_source.count())
            
            for row in range(0, self.data_source.count()):
                for column in range(0, self.COLUMNS):
                    self.setItem(row, column, self.data_source.item(column, row))
            
            if self.data_source.count() > 0:
                self.selectRow(0)
