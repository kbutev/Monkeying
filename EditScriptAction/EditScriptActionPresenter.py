from typing import Protocol
from PyQt5.QtWidgets import QWidget
from kink import di

from EditScriptAction.EditScriptActionField import EditScriptActionField
from EditScriptAction.EditScriptActionFieldBuilder import EditScriptActionFieldBuilder, \
    EditScriptActionFieldBuilderProtocol
from EditScriptAction.EditScriptActionWidget import EditScriptActionWidgetProtocol
from Model.InputEvent import InputEvent
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.JSONInputEvent import JSONInputEvent
from Parser.EventActionParser import EventActionParser, EventActionParserProtocol
from Presenter.Presenter import Presenter
from Utilities.Path import Path


class EditScriptActionPresenterRouter(Protocol):
    def prompt_choose_key_dialog(self, sender): pass
    def close(self, sender, save_changes): pass


class EditScriptActionPresenter(Presenter):
    
    # - Init
    
    def __init__(self, context_script_path: Path, event_index: int, input_event: InputEvent):
        super(EditScriptActionPresenter, self).__init__()
        self.router = None
        self.widget = None
        self.event_index = event_index
        self.input_event = input_event
        self.field_builder = di[EditScriptActionFieldBuilderProtocol]
        self.field_builder.context_script_path = context_script_path
        self.action_parser = di[EventActionParserProtocol]
    
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
        context = self.field_builder.start(self.input_event)
        context.set_on_type_change_callback(self.on_type_changed)
        context.set_on_choose_key_callback(self.prompt_choose_key_dialog)
        return context.build()
    
    def prompt_choose_key_dialog(self, sender):
        self.router.prompt_choose_key_dialog(sender)
    
    def save(self):
        self.router.close(self, True)
    
    def close(self):
        self.router.close(self, False)
    
    def on_type_changed(self, value):
        self.widget.reset()
        
        default_values = JSONInputEvent()
        default_values.set_defaults(value)
        default_values.set_time(self.input_event.time())
        
        self.input_event = self.action_parser.parse_json(default_values)
        
        self.widget.fill_values()
    
    def on_key_chosen(self, sender, event):
        if isinstance(sender, EditScriptActionField) and isinstance(event, KeystrokeEvent):
            sender.set_value(event.key_as_string())
            sender.delegate.set_value(event.key)
        else:
            assert False # bad logic
