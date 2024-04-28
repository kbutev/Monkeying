from PyQt5.QtWidgets import *
from typing import Protocol

from OpenScriptView.EditScriptTable import EditScriptTable, EditScriptTableDataSource


class EditScriptWidgetProtocol(Protocol):
    def set_events_data(self, data): pass
    def stop(self): pass

class EditScriptWidgetDelegate(Protocol):
    def on_begin(self): pass
    def on_stop(self): pass
    def on_save(self): pass
    def edit_script_action(self, index): pass

class EditScriptWidget(QWidget):
    delegate: EditScriptWidgetDelegate = None
    
    table: EditScriptTable
    data_source = EditScriptTableDataSource()
    
    edit_button: QPushButton
    save_button: QPushButton
    
    def __init__(self, parent=None):
        super(EditScriptWidget, self).__init__(parent)
        self.setup()
    
    def setup(self):
        layout = QVBoxLayout()
        
        self.table = EditScriptTable()
        self.table.data_source = self.data_source
        layout.addWidget(self.table)
        
        config_button = QPushButton('Configuration')
        layout.addWidget(config_button)
        
        self.edit_button = QPushButton('Edit')
        layout.addWidget(self.edit_button)
        self.edit_button.clicked.connect(self.edit_event)
        
        self.save_button = QPushButton('Save')
        layout.addWidget(self.save_button)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save)
        
        self.setLayout(layout)
    
    def set_events_data(self, data):
        self.data_source.data = data
        self.table.update_data()
        
    def edit_event(self):
        index = 0
        self.delegate.edit_script_action(index)
    
    def save(self):
        if self.delegate is not None: self.delegate.on_save()
