from typing import Protocol

from PyQt5 import QtCore
from PyQt5.QtWidgets import *

from OpenScriptView.EditScriptWidget import EditScriptWidget
from OpenScriptView.RunScriptWidget import RunScriptWidget

class OpenScriptWidgetDelegate(Protocol):
    def on_close(self): pass
    def on_current_tab_changed(self, index): pass

class OpenScriptWidget(QTabWidget):
    delegate: OpenScriptWidgetDelegate
    run_widget: RunScriptWidget
    edit_widget: EditScriptWidget
    
    def __init__(self, parent=None):
        super(OpenScriptWidget, self).__init__(parent)
        self.setup()
    
    def setup(self):
        self.run_widget = RunScriptWidget()
        self.edit_widget = EditScriptWidget()
        
        self.addTab(self.run_widget, 'Run')
        self.addTab(self.edit_widget, 'Edit')
        
        self.tabBar().setDocumentMode(True)
        self.tabBar().setExpanding(True)
        
        self.setMinimumSize(1024, 640)
        
        self.currentChanged.connect(self.on_current_tab_changed)
    
    def closeEvent(self, event):
        if self.delegate is not None:
            self.delegate.on_close()
        
        event.accept()
    
    def on_current_tab_changed(self, index):
        if self.delegate is not None:
            self.delegate.on_current_tab_changed(index)
    
    def keyPressEvent(self, event):
        if event.key() != QtCore.Qt.Key.Key_Escape:
            super(OpenScriptWidget, self).keyPressEvent(event)
