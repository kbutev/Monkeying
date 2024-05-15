from PyQt5.QtWidgets import *
from kink import inject, di


@inject(use_factory=True)
class ShowScriptsTableDataSource:
    
    # - Init
    
    def __init__(self, data=None):
        self.data = data if data is not None else []
    
    # - Properties
    
    def count(self) -> int:
        return len(self.data)
    
    def item(self, index) -> QTableWidgetItem:
        return QTableWidgetItem(self.data[index])


class ShowScriptsTable(QTableWidget):
    
    # - Init
    
    def __init__(self, parent=None):
        super(ShowScriptsTable, self).__init__(parent)
        self.data_source = di[ShowScriptsTableDataSource]
        self.setColumnCount(1)
        self.setRowCount(0)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
    
    # - Properties
    
    def get_data_source(self) -> ShowScriptsTableDataSource: return self.data_source
    def set_data_source(self, data_source): self.data_source = data_source
    
    # - Actions
    
    def update_data(self):
        if self.data_source is not None:
            self.setRowCount(self.data_source.count())
            
            for i in range(0, self.data_source.count()):
                self.setItem(i, 0, self.data_source.item(i))
            
            if self.data_source.count() > 0:
                self.selectRow(0)
