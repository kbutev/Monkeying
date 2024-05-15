from PyQt5.QtWidgets import *
from typing import Protocol
from MainView.RecordScriptTable import RecordScriptTable, RecordScriptTableDataSource


class RecordScriptWidgetProtocol(Protocol):
    def begin_recording(self, sender): pass
    def stop_recording(self, sender): pass
    def disable_save_recording(self): pass
    def set_events_data(self, data): pass
    def on_script_save(self): pass


class RecordWidgetDelegate(Protocol):
    def begin_recording(self, sender): pass
    def stop_recording(self, sender): pass
    def configure_script(self): pass
    def save_recording(self): pass
    def enable_tabs(self, value): pass


class RecordScriptWidget(QWidget):
    
    # - Init
    
    def __init__(self, parent=None):
        super(RecordScriptWidget, self).__init__(parent)
        
        self.delegate = None
        
        layout = QVBoxLayout()
        
        self.table = RecordScriptTable()
        layout.addWidget(self.table)
        
        self.state_button = QPushButton('Begin')
        layout.addWidget(self.state_button)
        self.state_button.clicked.connect(lambda: self.begin_recording(sender=self))
        
        config_button = QPushButton('Configuration')
        layout.addWidget(config_button)
        config_button.clicked.connect(self.configure_script)
        config_button.setEnabled(False)
        self.config_button = config_button
        
        self.save_button = QPushButton('Save')
        layout.addWidget(self.save_button)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_recording)
        
        self.setLayout(layout)
    
    # - Properties
    
    def get_delegate(self) -> RecordWidgetDelegate: return self.delegate
    def set_delegate(self, delegate): self.delegate = delegate
    def get_data_source(self) -> RecordScriptTableDataSource: return self.table.data_source
    def set_data_source(self, data_source): self.table.data_source = data_source
    
    # - Actions
    
    def begin_recording(self, sender):
        self.state_button.setText('Stop')
        self.state_button.clicked.disconnect()
        self.state_button.clicked.connect(lambda: self.stop_recording(sender=self))
        self.config_button.setEnabled(False)
        
        if self.delegate is not None: self.delegate.enable_tabs(False)
        
        if sender is self:
            if self.delegate is not None: self.delegate.begin_recording(sender=self)
        else:
            assert sender is self.delegate # Unrecognized sender
    
    def stop_recording(self, sender):
        self.state_button.setText('Begin')
        self.state_button.clicked.disconnect()
        self.state_button.clicked.connect(lambda: self.begin_recording(sender=self))
        self.config_button.setEnabled(True)
        self.save_button.setEnabled(True)
        
        if self.delegate is not None: self.delegate.enable_tabs(True)
        
        if sender is self:
            if self.delegate is not None: self.delegate.stop_recording(sender=self)
        else:
            assert sender is self.delegate # Unrecognized sender
    
    def configure_script(self):
        if self.delegate is not None:
            self.delegate.configure_script()
    
    def save_recording(self):
        if self.delegate is not None:
            self.delegate.save_recording()
    
    def disable_save_recording(self):
        self.save_button.setEnabled(False)
    
    def set_events_data(self, data):
        self.get_data_source().data = data
        self.table.update_data()
    
    def on_script_save(self):
        self.config_button.setEnabled(False)
