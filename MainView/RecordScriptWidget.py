from PyQt5.QtWidgets import *
from typing import Protocol

from MainView.RecordScriptTable import RecordScriptTable, RecordScriptTableDataSource


class RecordScriptWidgetProtocol(Protocol):
    def begin_recording(self, sender): pass
    def stop_recording(self, sender): pass
    def disable_save_recording(self): pass
    def set_events_data(self, data): pass

class RecordWidgetDelegate(Protocol):
    def begin_recording(self, sender): pass
    def stop_recording(self, sender): pass
    def save_recording(self): pass
    def enable_tabs(self, value): pass

class RecordScriptWidget(QWidget):
    delegate: RecordWidgetDelegate = None
    
    table: RecordScriptTable
    data_source = RecordScriptTableDataSource()
    
    state_button: QPushButton
    save_button: QPushButton
    
    def __init__(self, parent=None):
        super(RecordScriptWidget, self).__init__(parent)
        self.setup()
    
    def setup(self):
        layout = QVBoxLayout()
        
        self.table = RecordScriptTable()
        self.table.data_source = self.data_source
        layout.addWidget(self.table)
        
        self.state_button = QPushButton('Begin')
        layout.addWidget(self.state_button)
        self.state_button.clicked.connect(lambda: self.begin_recording(sender=self))
        
        config_button = QPushButton('Configuration')
        layout.addWidget(config_button)
        
        self.save_button = QPushButton('Save')
        layout.addWidget(self.save_button)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_recording)
        
        self.setLayout(layout)
    
    def begin_recording(self, sender):
        self.state_button.setText('Stop')
        self.state_button.clicked.disconnect()
        self.state_button.clicked.connect(lambda: self.stop_recording(sender=self))
        
        if self.delegate is not None: self.delegate.enable_tabs(False)
        
        if sender is self:
            if self.delegate is not None: self.delegate.begin_recording(sender=self)
        else:
            assert sender is self.delegate # Unrecognized sender
    
    def stop_recording(self, sender):
        self.state_button.setText('Begin')
        self.state_button.clicked.disconnect()
        self.state_button.clicked.connect(lambda: self.begin_recording(sender=self))
        self.save_button.setEnabled(True)
        
        if self.delegate is not None: self.delegate.enable_tabs(True)
        
        if sender is self:
            if self.delegate is not None: self.delegate.stop_recording(sender=self)
        else:
            assert sender is self.delegate # Unrecognized sender
    
    def save_recording(self):
        if self.delegate is not None:
            self.delegate.save_recording()
    
    def disable_save_recording(self):
        self.save_button.setEnabled(False)
    
    def set_events_data(self, data):
        self.data_source.data = data
        self.table.update_data()
