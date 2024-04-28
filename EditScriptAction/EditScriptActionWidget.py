from PyQt5.QtWidgets import *
from typing import Protocol

from EditScriptAction.EditScriptActionTable import EditScriptActionTable, EditScriptActionTableDataSource


class EditScriptActionWidgetProtocol(Protocol):
    def save_changes(self): pass
    def cancel_changes(self): pass

class EditWidgetDelegate(Protocol):
    def save(self): pass
    def close(self): pass

class EditScriptActionWidget(QWidget):
    delegate: EditWidgetDelegate = None
    
    timestamp_text: QLabel
    timestamp_field: QLineEdit
    action_kind: QComboBox
    table: EditScriptActionTable
    save_button: QPushButton
    cancel_button: QPushButton
    
    data_source = EditScriptActionTableDataSource()
    
    def __init__(self, parent=None):
        super(EditScriptActionWidget, self).__init__(parent)
        self.setup()
    
    def setup(self):
        layout = QVBoxLayout()
        
        self.timestamp_text = QLabel('Time')
        layout.addWidget(self.timestamp_text)
        self.timestamp_field = QLineEdit()
        self.timestamp_field.resize(280, 40)
        layout.addWidget(self.timestamp_field)
        
        self.action_kind = QComboBox()
        self.action_kind.addItem('Keyboard press')
        self.action_kind.addItem('Keyboard release')
        self.action_kind.addItem('Mouse press')
        self.action_kind.addItem('Mouse release')
        layout.addWidget(self.action_kind)
        
        self.table = EditScriptActionTable()
        self.table.data_source = self.data_source
        layout.addWidget(self.table)
        
        self.save_button = QPushButton('Save')
        layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_changes)
        
        self.cancel_button = QPushButton('Cancel')
        layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.cancel_changes)
        
        self.setLayout(layout)
    
    def save_changes(self):
        pass
    
    def cancel_changes(self):
        pass
