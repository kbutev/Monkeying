from typing import Protocol
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout

from ChooseKeyboardKey.ChooseKeyboardKeyPresenter import ChooseKeyboardKeyPresenter
from ChooseKeyboardKey.ChooseKeyboardKeyWidget import ChooseKeyboardKeyWidget
from EditScriptAction.EditScriptActionPresenter import EditScriptActionPresenter
from EditScriptAction.EditScriptActionWidget import EditScriptActionWidget
from Model.InputEvent import InputEvent
from OpenScriptView.EditScriptPresenter import EditScriptPresenter


class EditScriptActionRouter(Protocol):
    widget: QDialog = None
    
    is_insert = False
    edit_action_presenter: EditScriptActionPresenter
    edit_script_presenter: EditScriptPresenter
    
    def __init__(self, is_insert, event_index, input_event: InputEvent, edit_script_presenter):
        self.is_insert = is_insert
        self.edit_action_presenter = EditScriptActionPresenter(event_index, input_event)
        self.edit_script_presenter = edit_script_presenter
    
    def setup(self, parent):
        dialog = QDialog(parent)
        dialog.setWindowTitle(f'Edit action')
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        dialog.resize(640, 640)
        dialog.setMinimumSize(640, 640)
        dialog.setMaximumSize(640, 640)
        
        layout = QVBoxLayout()
        widget = EditScriptActionWidget()
        widget.delegate = self.edit_action_presenter
        self.edit_action_presenter.router = self
        self.edit_action_presenter.widget = widget
        layout.addWidget(widget)
        self.edit_action_presenter.start()
        
        dialog.setLayout(layout)
        
        self.widget = dialog
    
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
        widget.delegate = presenter
        layout.addWidget(widget)
        presenter.start()
        dialog.setLayout(layout)
        
        dialog.exec()
    
    def close(self, sender, save_changes):
        assert self.widget is not None
        input_event = sender.input_event
        event_index = sender.event_index
        self.widget.close()
        self.widget = None
        
        if save_changes and isinstance(sender, EditScriptActionPresenter):
            if self.is_insert:
                self.edit_script_presenter.on_save_insert_script_action(input_event)
            else:
                self.edit_script_presenter.on_save_edit_script_action(event_index, input_event)
    
    def on_key_chosen(self, sender, dialog, result_event):
        dialog.close()
        self.edit_action_presenter.on_key_chosen(sender, result_event)
    
    def on_close(self):
        # When window closes: stop services
        self.edit_action_presenter.stop()
