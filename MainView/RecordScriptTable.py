from PyQt5.QtWidgets import *
from kink import inject, di

from Model.InputEvent import InputEventDescription


@inject(use_factory=True)
class RecordScriptTableDataSource:
    
    # - Init
    
    def __init__(self, data=None):
        self.data = data if data is not None else []
    
    # - Properties
    
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
    
    # - Init
    
    def __init__(self, parent=None):
        super(RecordScriptTable, self).__init__(parent)
        self.data_source = di[RecordScriptTableDataSource]
        self.setColumnCount(RecordScriptTable.COLUMNS)
        self.setRowCount(0)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
    
    # - Properties
    
    def get_data_source(self) -> RecordScriptTableDataSource: return self.data_source
    def set_data_source(self, data_source): self.data_source = data_source
    
    # - Setup
    
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
