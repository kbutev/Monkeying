from typing import Protocol
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from ChooseKeyboardKey.ChooseKeyboardKeyPresenter import ChooseKeyboardKeyPresenter
from ChooseKeyboardKey.ChooseKeyboardKeyWidget import ChooseKeyboardKeyWidget
from EditScriptAction.EditScriptActionPresenter import EditScriptActionPresenter
from EditScriptAction.EditScriptActionWidget import EditScriptActionWidget
from Model.ScriptAction import ScriptAction
from OpenScriptView.EditScriptPresenter import EditScriptPresenter


class EditScriptActionRouter(Protocol):
    
    # - Init
    
    def __init__(self, is_insert: bool, action_index, action: ScriptAction, edit_script_presenter: EditScriptPresenter):
        self.widget = None
        self.is_insert = is_insert
        script_path = edit_script_presenter.get_script_path()
        self.edit_script_presenter = edit_script_presenter
        self.edit_action_presenter = EditScriptActionPresenter(edit_script_presenter, script_path, action_index, action)
    
    # - Properties
    
    def is_insert_action(self) -> bool: return self.is_insert
    def is_edit_action(self) -> bool: return not self.is_insert
    
    # - Setup
    
    def setup(self, parent):
        dialog = QDialog(parent)
        dialog.setWindowTitle(f'Edit action')
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        dialog.resize(640, 640)
        dialog.setMinimumSize(640, 640)
        dialog.setMaximumSize(640, 640)
        
        layout = QVBoxLayout()
        widget = EditScriptActionWidget()
        widget.set_delegate(self.edit_action_presenter)
        self.edit_action_presenter.set_router(self)
        self.edit_action_presenter.set_widget(widget)
        layout.addWidget(widget)
        self.edit_action_presenter.start()
        
        dialog.setLayout(layout)
        
        self.widget = dialog
    
    # - Actions
    
    def prompt_choose_key_dialog(self, sender):
        dialog = QDialog(self.widget)
        dialog.setWindowTitle(f'Choose key')
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        dialog.resize(320, 320)
        dialog.setMinimumSize(320, 320)
        dialog.setMaximumSize(320, 320)
        
        layout = QVBoxLayout()
        widget = ChooseKeyboardKeyWidget()
        presenter = ChooseKeyboardKeyPresenter(lambda result: self.on_key_chosen(sender, dialog, result))
        widget.set_delegate(presenter)
        layout.addWidget(widget)
        presenter.start()
        dialog.setLayout(layout)
        
        dialog.exec()
    
    def close(self):
        assert self.widget is not None
        self.widget.close()
        self.widget = None
    
    def on_key_chosen(self, sender, dialog, result_event):
        dialog.close()
        self.edit_action_presenter.on_key_chosen(sender, result_event)
    
    def on_close(self):
        # When window closes: stop services
        self.edit_action_presenter.stop()
