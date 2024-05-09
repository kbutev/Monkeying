from PyQt5.QtWidgets import *
from Model.InputEvent import InputEventDescription


class RecordScriptTableDataSource:
    data = []
    
    def count(self) -> int:
        return len(self.data)
    
    def item(self, column, row) -> QTableWidgetItem:
        assert column <= 2
        
        entry: InputEventDescription = self.data[row]
        
        match column:
            case 0: return QTableWidgetItem(entry.timestamp)
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
            current_selection = self.currentIndex().row()
            
            self.setRowCount(self.data_source.count())
            
            for row in range(0, self.data_source.count()):
                for column in range(0, self.COLUMNS):
                    self.setItem(row, column, self.data_source.item(column, row))
            
            if self.data_source.count() > 0:
                current_selection = 0 if current_selection < 0 else current_selection
                new_index = current_selection if current_selection < self.data_source.count() else self.data_source.count() - 1
                self.selectRow(new_index)
