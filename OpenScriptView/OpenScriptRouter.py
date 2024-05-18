from typing import Protocol
from PyQt5.QtWidgets import QVBoxLayout

from ConfigureScript.ConfigureScriptPresenter import ConfigureScriptPresenter
from ConfigureScript.ConfigureScriptRouter import ConfigureScriptRouter
from Dialog.Dialog import Dialog
from EditScriptAction.EditScriptActionRouter import EditScriptActionRouter
from Model.ScriptConfiguration import ScriptConfiguration
from Model.ScriptData import ScriptData
from OpenScriptView.EditScriptPresenter import EditScriptPresenter
from OpenScriptView.OpenScriptWidget import OpenScriptWidget
from OpenScriptView.RunScriptPresenter import RunScriptPresenter


class OpenScriptRouter(Protocol):
    
    # - Init
    
    def __init__(self, parent_dialog: Dialog, script_data: ScriptData):
        self.parent_dialog = parent_dialog
        self.widget = OpenScriptWidget()
        self.edit_script_presenter = EditScriptPresenter(script_data)
        self.run_script_presenter = RunScriptPresenter(script_data)
        self.config_script_presenter = None
        self.current_dialog = None
    
    # - Properties
    
    def get_script_data(self) -> ScriptData: return self.edit_script_presenter.get_script_data()
    
    # - Setup
    
    def setup(self):
        self.widget.set_delegate(self)
        
        self.widget.run_widget.set_delegate(self.run_script_presenter)
        self.run_script_presenter.set_widget(self.widget.run_widget)
        self.run_script_presenter.set_router(self)
        
        self.widget.edit_widget.set_delegate(self.edit_script_presenter)
        self.edit_script_presenter.set_widget(self.widget.edit_widget)
        self.edit_script_presenter.set_router(self)
        
        self.run_script_presenter.start()
        self.edit_script_presenter.start()
    
    # - Actions
    
    def enable_tabs(self, enabled):
        self.widget.tabBar().setEnabled(enabled)
    
    def open_script(self, parent, item):
        assert parent is not None
        assert item is not None
        
        layout = QVBoxLayout()
        
        script_widget = OpenScriptWidget()
        script_widget.run_widget.set_delegate(self.run_script_presenter)
        self.run_script_presenter.set_widget(script_widget.run_widget)
        
        layout.addWidget(script_widget)
        
        dialog = Dialog(parent)
        dialog.set_title(f'Run {item}')
        dialog.set_layout(layout)
        dialog.set_delegate(self)
        self.current_dialog = dialog
        dialog.present()
    
    def insert_script_action(self, parent, action):
        router = EditScriptActionRouter(True, 0, action, self.edit_script_presenter)
        router.setup(parent)
        router.widget.exec()
    
    def edit_script_action(self, parent, action_index, action):
        router = EditScriptActionRouter(False, action_index, action, self.edit_script_presenter)
        router.setup(parent)
        router.widget.exec()
    
    def configure_script(self, parent):
        presenter = ConfigureScriptPresenter(self.get_script_data())
        router = ConfigureScriptRouter(presenter)
        router.set_delegate(self)
        router.setup(parent)
        router.dialog.present()
    
    def on_current_tab_changed(self, index):
        if index == 0:
            self.run_script_presenter.start()
            self.edit_script_presenter.stop()
        else:
            self.run_script_presenter.stop()
            self.edit_script_presenter.start()
    
    # - DialogRouter
    
    def on_dialog_appear(self, sender): pass
    def on_dialog_disappear(self, sender): pass
    
    def on_dialog_close(self, sender):
        # When dialog closes: stop services
        self.run_script_presenter.stop()
        self.edit_script_presenter.stop()
    
    # - ConfigureScriptRouterDelegate
    
    def on_save_script_configuration(self, script: ScriptData):
        self.run_script_presenter.update_script_configuration(script)
        self.edit_script_presenter.update_script_configuration(script)
        self.parent_dialog.set_title(f'Run {script.get_info().name}')
