from PyQt5.QtWidgets import *
from Service.SettingsManager import *
from Service import SettingsManager


class ShowScriptsTableDataSource:
    data = []
    file_format: str
    
    def __init__(self):
        self.file_format = SettingsManager.singleton.field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT)
    
    def count(self) -> int:
        return len(self.data)
    
    def item(self, index) -> QTableWidgetItem:
        label = self.data[index].replace(f'.{self.file_format}', '')
        return QTableWidgetItem(label)


class ShowScriptsTable(QTableWidget):
    data_source: ShowScriptsTableDataSource
    
    def __init__(self, parent=None):
        super(ShowScriptsTable, self).__init__(parent)
        self.setup()
    
    def setup(self):
        self.setColumnCount(1)
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
            
            for i in range(0, self.data_source.count()):
                self.setItem(i, 0, self.data_source.item(i))
            
            if self.data_source.count() > 0:
                self.selectRow(0)
