from typing import Protocol
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from EditScriptAction.EditScriptActionRouter import EditScriptActionRouter
from OpenScriptView.EditScriptPresenter import EditScriptPresenter
from OpenScriptView.OpenScriptWidget import OpenScriptWidget
from OpenScriptView.RunScriptPresenter import RunScriptPresenter


class OpenScriptRouter(Protocol):
    widget: OpenScriptWidget = None
    edit_script_presenter: EditScriptPresenter
    run_script_presenter: RunScriptPresenter
    
    current_dialog: QDialog = None
    
    def __init__(self, script):
        self.edit_script_presenter = EditScriptPresenter(script)
        self.run_script_presenter = RunScriptPresenter(script)
    
    def setup(self):
        self.widget = OpenScriptWidget()
        self.widget.delegate = self
        
        self.widget.run_widget.delegate = self.run_script_presenter
        self.run_script_presenter.widget = self.widget.run_widget
        self.run_script_presenter.router = self
        
        self.widget.edit_widget.delegate = self.edit_script_presenter
        self.edit_script_presenter.widget = self.widget.edit_widget
        self.edit_script_presenter.router = self
        
        self.run_script_presenter.start()
        self.edit_script_presenter.start()
    
    def enable_tabs(self, enabled):
        self.widget.tabBar().setEnabled(enabled)
    
    def open_script(self, parent, item):
        assert parent is not None
        assert item is not None
        
        current_dialog = QDialog(parent)
        current_dialog.setWindowTitle(f'Run {item}')
        layout = QVBoxLayout()
        
        script_widget = OpenScriptWidget()
        script_widget.run_widget.delegate = self.run_script_presenter
        self.run_script_presenter.widget = script_widget.run_widget
        
        layout.addWidget(script_widget)
        current_dialog.setLayout(layout)
        
        self.current_dialog = current_dialog
        current_dialog.exec()
    
    def insert_script_action(self, parent, input_event):
        router = EditScriptActionRouter(True, 0, input_event, self.edit_script_presenter)
        router.setup(parent)
        router.widget.exec()
    
    def edit_script_action(self, parent, event_index, input_event):
        router = EditScriptActionRouter(False, event_index, input_event, self.edit_script_presenter)
        router.setup(parent)
        router.widget.exec()
    
    def on_close(self):
        # When window closes: stop services
        self.run_script_presenter.stop()
    
    def on_current_tab_changed(self, index):
        if index == 0:
            self.run_script_presenter.start()
        else:
            self.run_script_presenter.stop()
