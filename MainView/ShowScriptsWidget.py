from typing import Protocol
from PyQt5.QtWidgets import *
from MainView.ShowScriptsTable import ShowScriptsTableDataSource, ShowScriptsTable


class ShowScriptsWidgetProtocol(Protocol):
    def set_data(self, data): pass

class ShowScriptsWidgetDelegate(Protocol):
    def can_open_script(self, item) -> bool: pass
    def open_script(self, item): pass

class ShowScriptsWidget(QWidget):
    delegate: ShowScriptsWidgetDelegate = None
    
    table: ShowScriptsTable
    data_source = ShowScriptsTableDataSource()
    
    def __init__(self, parent=None):
        super(ShowScriptsWidget, self).__init__(parent)
        self.setup()
    
    def setup(self):
        layout = QVBoxLayout()
        
        self.table = ShowScriptsTable()
        self.table.data_source = self.data_source
        layout.addWidget(self.table)
        
        open_button = QPushButton('Open')
        layout.addWidget(open_button)
        open_button.clicked.connect(self.open_selected_script)
        
        self.setLayout(layout)
    
    def set_data(self, data):
        self.data_source.data = data
        self.update_data()
    
    def selected_index(self) -> int:
        assert self.table.selectionModel().hasSelection()
        index = self.table.selectedIndexes()[0].row()
        return index
    
    def selected_item(self) -> str:
        return self.data_source.data[self.selected_index()]
    
    def open_selected_script(self):
        if self.delegate is not None:
            item = self.selected_item()
            
            if self.delegate.can_open_script(item):
                self.open_script(item)
    
    def open_script(self, item):
        assert self.delegate is not None
        
        print(f'open script \'{item}\'')
        
        self.delegate.open_script(item)
    
    def update_data(self):
        self.table.update_data()
