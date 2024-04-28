from PyQt5.QtWidgets import *
from typing import Protocol

from OpenScriptView.RunScriptTable import RunScriptTable, RunScriptTableDataSource


class RunScriptWidgetProtocol(Protocol):
    def run_script(self, sender): pass
    def stop_script(self, sender): pass
    def set_events_data(self, data): pass
    def update_progress(self, index, percentage: int): pass

class RunScriptWidgetDelegate(Protocol):
    def is_script_active(self) -> bool: return False
    def can_run_script(self) -> bool: return False
    def run_script(self, sender): pass
    def stop_script(self, sender): pass
    def enable_tabs(self, value): pass

class RunScriptWidget(QWidget):
    delegate: RunScriptWidgetDelegate = None
    
    table: RunScriptTable
    data_source = RunScriptTableDataSource()
    
    progress_bar: QProgressBar
    state_button: QPushButton
    
    def __init__(self, parent=None):
        super(RunScriptWidget, self).__init__(parent)
        self.setup()
    
    def setup(self):
        layout = QVBoxLayout()
        
        self.table = RunScriptTable()
        self.table.data_source = self.data_source
        layout.addWidget(self.table)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(200, 80, 250, 20)
        layout.addWidget(self.progress_bar)
        
        self.state_button = QPushButton('Run')
        layout.addWidget(self.state_button)
        self.state_button.clicked.connect(lambda: self.run_script(sender=self))
        
        self.setLayout(layout)
    
    def run_script(self, sender):
        self.state_button.setText('Stop')
        self.state_button.clicked.disconnect()
        self.state_button.clicked.connect(lambda: self.stop_script(sender=self))
        self.progress_bar.setValue(0)
        
        if self.delegate is not None: self.delegate.enable_tabs(False)
        
        if sender is self:
            if self.delegate is not None: self.delegate.run_script(sender=self)
        else:
            assert sender is self.delegate # Unrecognized sender
    
    def stop_script(self, sender):
        self.state_button.setText('Run')
        self.state_button.clicked.disconnect()
        self.state_button.clicked.connect(lambda: self.run_script(sender=self))
        
        if self.delegate is not None: self.delegate.enable_tabs(True)
        
        if sender is self:
            if self.delegate is not None: self.delegate.stop_script(sender=self)
        else:
            assert sender is self.delegate  # Unrecognized sender
    
    def set_events_data(self, data):
        self.data_source.data = data
        self.table.update_data()
    
    def update_progress(self, index, percentage: int):
        self.table.selectRow(index)
        self.progress_bar.setValue(percentage)
