from PyQt5.QtWidgets import *
from typing import Protocol
from OpenScriptView.EditScriptTable import EditScriptTable, EditScriptTableDataSource


class EditScriptWidgetProtocol(Protocol):
    def set_events_data(self, data): pass
    def select_index(self, index): pass
    def select_next_index(self): pass
    def on_script_action_changed(self): pass


class EditScriptWidgetDelegate(Protocol):
    def on_begin(self): pass
    def on_stop(self): pass
    def on_save(self): pass
    def on_configure_script(self): pass
    def insert_script_action(self, index): pass
    def delete_script_action(self, index): pass
    def edit_script_action(self, index): pass


class EditScriptWidget(QWidget):
    
    # - Init
    
    def __init__(self, parent=None):
        super(EditScriptWidget, self).__init__(parent)
        
        self.delegate = None
        
        layout = QVBoxLayout()
        
        self.table = EditScriptTable()
        layout.addWidget(self.table)
        
        self.insert_button = QPushButton('Insert')
        layout.addWidget(self.insert_button)
        self.insert_button.clicked.connect(self.insert_event)
        
        self.delete_button = QPushButton('Delete')
        layout.addWidget(self.delete_button)
        self.delete_button.clicked.connect(self.delete_event)
        
        self.edit_button = QPushButton('Edit')
        layout.addWidget(self.edit_button)
        self.edit_button.clicked.connect(self.edit_event)
        
        self.save_button = QPushButton('Save')
        layout.addWidget(self.save_button)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save)
        
        # This option will remain visible only in Run script (for now)
        #self.config_button = QPushButton('Configuration')
        #layout.addWidget(self.config_button)
        #self.config_button.clicked.connect(self.configure_script)
        
        self.setLayout(layout)
    
    # - Properties
    
    def get_delegate(self) -> EditScriptWidgetDelegate: return self.delegate
    def set_delegate(self, delegate): self.delegate = delegate
    def get_data_source(self) -> EditScriptTableDataSource: return self.table.data_source
    def set_data_source(self, data_source): self.table.data_source = data_source
    
    def set_events_data(self, data):
        data_source = self.get_data_source()
        data_source.data = data
        self.table.update_data()
        
        self.delete_button.setEnabled(len(data_source.data) > 0)
        self.edit_button.setEnabled(len(data_source.data) > 0)
    
    # - Actions
    
    def select_index(self, index):
        self.table.selectRow(index)
    
    def select_next_index(self):
        current_index = self.table.currentRow()
        
        if current_index + 1 < self.get_data_source().count():
            self.table.selectRow(current_index + 1)
    
    def on_script_action_changed(self):
        self.save_button.setEnabled(True)
    
    def insert_event(self):
        index = self.table.currentRow()
        index = index if index >= 0 else 0
        self.delegate.insert_script_action(index)
    
    def delete_event(self):
        self.delegate.delete_script_action(self.table.currentRow())
        self.delete_button.setEnabled(len(self.get_data_source().data) > 0)
    
    def edit_event(self):
        self.delegate.edit_script_action(self.table.currentRow())
    
    def save(self):
        self.save_button.setEnabled(False)
        
        if self.delegate is not None: self.delegate.on_save()
    
    def configure_script(self):
        if self.delegate is not None: self.delegate.on_configure_script()
