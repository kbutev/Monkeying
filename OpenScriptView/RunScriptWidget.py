from PyQt5.QtWidgets import *
from typing import Protocol

from kink import di

from OpenScriptView.RunScriptTable import RunScriptTable, RunScriptTableDataSource
from Utilities.Logger import LoggerProtocol


class RunScriptWidgetProtocol(Protocol):
    def run_script(self, sender): pass
    def resume_script(self, sender): pass
    def pause_script(self, sender): pass
    def stop_script(self, sender): pass
    def set_events_data(self, data): pass
    def update_progress(self, index, percentage: int): pass


class RunScriptWidgetDelegate(Protocol):
    def is_script_active(self) -> bool: return False
    def can_run_script(self) -> bool: return False
    def run_script(self, sender): pass
    def stop_script(self, sender): pass
    def pause_script(self, sender): pass
    def resume_script(self, sender): pass
    def configure_script(self): pass
    def enable_tabs(self, value): pass


class RunScriptWidget(QWidget):
    
    # - Init
    
    def __init__(self, parent=None):
        super(RunScriptWidget, self).__init__(parent)
        
        self.delegate = None
        
        layout = QVBoxLayout()
        
        self.table = RunScriptTable()
        layout.addWidget(self.table)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(200, 80, 250, 20)
        layout.addWidget(self.progress_bar)
        
        self.state_button = QPushButton('Run')
        layout.addWidget(self.state_button)
        self.state_button.clicked.connect(lambda: self.run_script(sender=self))
        
        self.pause_button = QPushButton('Pause')
        layout.addWidget(self.pause_button)
        self.pause_button.setEnabled(False)
        
        self.config_button = QPushButton('Configuration')
        layout.addWidget(self.config_button)
        self.config_button.clicked.connect(self.configure_script)
        
        self.setLayout(layout)
        
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def get_delegate(self) -> RunScriptWidgetDelegate: return self.delegate
    def set_delegate(self, delegate): self.delegate = delegate
    def get_data_source(self) -> RunScriptTableDataSource: return self.table.data_source
    def set_data_source(self, data_source): self.table.data_source = data_source
    
    # - Actions
    
    def run_script(self, sender):
        self.state_button.setText('Stop')
        self.state_button.clicked.disconnect()
        self.state_button.clicked.connect(lambda: self.stop_script(sender=self))
        self.progress_bar.setValue(0)
        
        self.setup_pause_script()
        self.pause_button.setEnabled(True)
        self.config_button.setEnabled(False)
        
        if self.delegate is not None: self.delegate.enable_tabs(False)
        
        if sender is self:
            if self.delegate is not None: self.delegate.run_script(sender=self)
        else:
            assert sender is self.delegate # Unrecognized sender
    
    def stop_script(self, sender):
        self.state_button.setText('Run')
        self.state_button.clicked.disconnect()
        self.state_button.clicked.connect(lambda: self.run_script(sender=self))
        
        self.setup_pause_script()
        self.pause_button.setEnabled(False)
        self.config_button.setEnabled(True)
        
        if self.delegate is not None: self.delegate.enable_tabs(True)
        
        if sender is self:
            if self.delegate is not None: self.delegate.stop_script(sender=self)
        else:
            assert sender is self.delegate  # Unrecognized sender
    
    def pause_script(self, sender):
        self.setup_resume_script()
        
        if sender is self:
            if self.delegate is not None: self.delegate.pause_script(sender=self)
        else:
            assert sender is self.delegate  # Unrecognized sender
    
    def resume_script(self, sender):
        self.setup_pause_script()
        
        if sender is self:
            if self.delegate is not None: self.delegate.resume_script(sender=self)
        else:
            assert sender is self.delegate  # Unrecognized sender
    
    def configure_script(self):
        self.delegate.configure_script()
    
    def setup_pause_script(self):
        self.pause_button.setText('Pause')
        self.pause_button.disconnect()
        self.pause_button.clicked.connect(lambda: self.pause_script(sender=self))
    
    def setup_resume_script(self):
        self.pause_button.setText('Resume')
        self.pause_button.disconnect()
        self.pause_button.clicked.connect(lambda: self.resume_script(sender=self))
    
    def set_events_data(self, data):
        data_source = self.get_data_source()
        data_source.data = data
        self.table.update_data()
        
        self.state_button.setEnabled(len(data_source.data) > 0)
    
    def update_progress(self, index, percentage: int):
        count = len(self.get_data_source().data)
        
        #self.logger.debug(f'update_events index={index}/{count} progress={percentage}/100')
        
        if index >= count:
            index = count-1
        
        self.table.selectRow(index)
        self.progress_bar.setValue(percentage)
