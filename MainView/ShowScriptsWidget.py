from typing import Protocol
from PyQt5.QtWidgets import *
from kink import di

from MainView.ShowScriptsTable import ShowScriptsTableDataSource, ShowScriptsTable
from Utilities.Logger import LoggerProtocol


class ShowScriptsWidgetProtocol(Protocol):
    def set_data(self, data): pass


class ShowScriptsWidgetDelegate(Protocol):
    def can_open_script(self, index) -> bool: pass
    def open_script(self, index): pass


class ShowScriptsWidget(QWidget):
    
    # - Init
    
    def __init__(self, parent=None):
        super(ShowScriptsWidget, self).__init__(parent)
        
        self.delegate = None
        
        layout = QVBoxLayout()
        
        self.table = ShowScriptsTable()
        layout.addWidget(self.table)
        
        open_button = QPushButton('Open')
        layout.addWidget(open_button)
        open_button.clicked.connect(self.open_selected_script)
        
        self.setLayout(layout)
        
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def get_delegate(self) -> ShowScriptsWidgetDelegate: return self.delegate
    def set_delegate(self, delegate): self.delegate = delegate
    def get_data_source(self) -> ShowScriptsTableDataSource: return self.table.data_source
    def set_data_source(self, data_source): self.table.data_source = data_source
    
    def set_data(self, data):
        self.get_data_source().data = data
        self.update_data()
    
    # - Actions
    
    def selected_index(self) -> int:
        assert self.table.selectionModel().hasSelection()
        index = self.table.selectedIndexes()[0].row()
        return index
    
    def selected_item(self) -> str:
        return self.get_data_source().data[self.selected_index()]
    
    def open_selected_script(self):
        if self.delegate is not None:
            name = self.selected_item()
            index = self.selected_index()
            
            if self.delegate.can_open_script(index):
                self.open_script(name, index)
    
    def open_script(self, name, index):
        assert self.delegate is not None
        
        self.logger.info(f'open script \'{name}\' at {index}')
        
        self.delegate.open_script(index)
    
    def update_data(self):
        self.table.update_data()
