from typing import Protocol
from PyQt5.QtWidgets import QWidget
from kink import di

from EditScriptAction.EditScriptActionField import EditScriptActionField
from EditScriptAction.EditScriptActionFieldBuilder import EditScriptActionFieldBuilderProtocol
from EditScriptAction.EditScriptActionWidget import EditScriptActionWidgetProtocol
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.ScriptAction import ScriptAction
from OpenScriptView.EditScriptPresenter import EditScriptPresenter
from Parser.ScriptActionParser import ScriptActionParserProtocol, default_event_as_json
from Presenter.Presenter import Presenter
from Utilities.Path import Path


class EditScriptActionPresenterRouter(Protocol):
    def is_insert_action(self) -> bool: return False
    def is_edit_action(self) -> bool: return False
    def prompt_choose_key_dialog(self, sender): pass
    def close(self): pass


class EditScriptActionPresenter(Presenter):
    
    # - Init
    
    def __init__(self, edit_script_presenter: EditScriptPresenter, context_script_path: Path, action_index: int, action: ScriptAction):
        super(EditScriptActionPresenter, self).__init__()
        self.router = None
        self.widget = None
        self.edit_script_presenter = edit_script_presenter
        self.action_index = action_index
        self.action = action
        self.field_builder = di[EditScriptActionFieldBuilderProtocol]
        self.field_builder.context_script_path = context_script_path
        self.action_parser = di[ScriptActionParserProtocol]
    
    # - Properties
    
    def get_router(self) -> EditScriptActionPresenterRouter: return self.router
    def set_router(self, router): self.router = router
    def get_widget(self) -> EditScriptActionWidgetProtocol: return self.widget
    def set_widget(self, widget): self.widget = widget
    
    # - Setup
    
    def start(self):
        self.fill_values()
    
    def stop(self):
        pass
    
    # - Actions
    
    def fill_values(self):
        self.widget.fill_values()
    
    def build_dynamic_fields(self) -> [QWidget]:
        context = self.field_builder.start(self.action)
        context.set_on_type_change_callback(self.on_type_changed)
        context.set_on_choose_key_callback(self.prompt_choose_key_dialog)
        return context.build()
    
    def prompt_choose_key_dialog(self, sender):
        self.router.prompt_choose_key_dialog(sender)
    
    def save(self):
        self.save_action()
        self.router.close()
    
    def close(self):
        self.router.close()
    
    def save_action(self):
        is_insert = self.router.is_insert_action()
        
        if is_insert:
            self.edit_script_presenter.on_save_insert_script_action(self.action)
        else:
            self.edit_script_presenter.on_save_edit_script_action(self.action_index, self.action)
    
    def on_type_changed(self, value: str):
        self.widget.reset()
        
        default_values = default_event_as_json(value, time=self.action.time())
        self.action = self.action_parser.parse_to_action(default_values)
        
        self.widget.fill_values()
    
    def on_key_chosen(self, sender, event):
        if isinstance(sender, EditScriptActionField) and isinstance(event, KeystrokeEvent):
            sender.set_value(event.key_as_string())
            sender.delegate.set_value(event.key)
        else:
            assert False # bad logic
