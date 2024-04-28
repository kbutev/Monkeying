from typing import Protocol

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from MainView.RecordScriptWidget import RecordScriptWidget
from MainView.ShowScriptsWidget import ShowScriptsWidget

class MainWidgetDelegate(Protocol):
    def on_current_tab_changed(self, index): pass

class MainWidget(QTabWidget):
    delegate: MainWidgetDelegate
    scripts_widget: ShowScriptsWidget
    rec_widget: RecordScriptWidget
    
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.setup()
    
    def setup(self):
        self.scripts_widget = ShowScriptsWidget()
        self.rec_widget = RecordScriptWidget()
        
        self.addTab(self.scripts_widget, 'Scripts')
        self.addTab(self.rec_widget, 'Record')
        
        self.tabBar().setDocumentMode(True)
        self.tabBar().setExpanding(True)
        
        self.setMinimumSize(1024, 640)
        
        self.currentChanged.connect(self.on_current_tab_changed)
    
    def on_current_tab_changed(self, index):
        if self.delegate is not None:
            self.delegate.on_current_tab_changed(index)
    
    def keyPressEvent(self, event):
        if event.key() != QtCore.Qt.Key.Key_Escape:
            super(MainWidget, self).keyPressEvent(event)
