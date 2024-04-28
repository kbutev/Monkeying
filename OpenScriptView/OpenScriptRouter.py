from typing import Protocol

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout

from EditScriptAction.EditScriptActionPresenter import EditScriptActionPresenter
from EditScriptAction.EditScriptActionWidget import EditScriptActionWidget
from OpenScriptView.EditScriptPresenter import EditScriptPresenter
from OpenScriptView.OpenScriptWidget import OpenScriptWidget
from OpenScriptView.RunScriptPresenter import RunScriptPresenter

class OpenScriptRouter(Protocol):
    widget: OpenScriptWidget
    edit_script_presenter: EditScriptPresenter
    run_script_presenter: RunScriptPresenter
    
    def __init__(self, script):
        self.edit_script_presenter = EditScriptPresenter(script)
        self.run_script_presenter = RunScriptPresenter(script)
    
    def setup(self, widget):
        self.widget = widget
        self.widget.delegate = self
        
        self.widget.run_widget.delegate = self.run_script_presenter
        self.run_script_presenter.widget = widget.run_widget
        self.run_script_presenter.router = self
        
        self.widget.edit_widget.delegate = self.edit_script_presenter
        self.edit_script_presenter.widget = widget.edit_widget
        self.edit_script_presenter.router = self
        
        self.run_script_presenter.start()
        self.edit_script_presenter.start()
    
    def enable_tabs(self, enabled):
        self.widget.tabBar().setEnabled(enabled)
    
    def open_script(self, parent, item):
        assert parent is not None
        assert item is not None
        
        window = QDialog(parent)
        window.setWindowTitle(f'Run {item}')
        layout = QVBoxLayout()
        
        script_widget = OpenScriptWidget()
        script_widget.run_widget.delegate = self.run_script_presenter
        self.run_script_presenter.widget = script_widget.run_widget
        
        layout.addWidget(script_widget)
        window.setLayout(layout)
        window.exec()
    
    def edit_script_action(self, parent, index):
        window = QDialog(parent)
        window.setWindowTitle(f'Edit action')
        window.setWindowFlags(window.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        window.resize(640, 640)
        window.setMinimumSize(640, 640)
        window.setMaximumSize(640, 640)
        layout = QVBoxLayout()
        widget = EditScriptActionWidget()
        presenter = EditScriptActionPresenter()
        widget.delegate = presenter
        presenter.widget = widget
        layout.addWidget(widget)
        presenter.start()
        window.setLayout(layout)
        window.exec()
    
    def on_close(self):
        # When window closes: stop services
        self.run_script_presenter.stop()
    
    def on_current_tab_changed(self, index):
        if index == 0:
            self.run_script_presenter.start()
        else:
            self.run_script_presenter.stop()
