from typing import Protocol
from PyQt5.QtWidgets import QWidget
from EditScriptAction.EditScriptActionField import EditScriptActionField
from EditScriptAction.EditScriptActionFieldBuilder import EditScriptActionFieldBuilderProtocol, \
    EditScriptActionFieldBuilder
from EditScriptAction.EditScriptActionWidget import EditScriptActionWidgetProtocol
from Model.InputEvent import InputEvent
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.JSONInputEvent import JSONInputEvent
from Parser.EventActionParser import EventActionParserProtocol, EventActionParser
from Presenter.Presenter import Presenter


class EditScriptActionPresenterRouter(Protocol):
    def prompt_choose_key_dialog(self, sender): pass
    def close(self, sender, save_changes): pass

class EditScriptActionPresenter(Presenter):
    router: EditScriptActionPresenterRouter = None
    widget: EditScriptActionWidgetProtocol = None
    
    event_index: int
    input_event: InputEvent
    
    field_builder: EditScriptActionFieldBuilderProtocol = EditScriptActionFieldBuilder()
    action_parser: EventActionParserProtocol = EventActionParser()
    
    def __init__(self, context_script_path, event_index, input_event: InputEvent):
        super(EditScriptActionPresenter, self).__init__()
        self.event_index = event_index
        self.input_event = input_event
        self.field_builder.context_script_path = context_script_path
    
    def start(self):
        self.fill_values()
    
    def stop(self):
        pass
    
    def fill_values(self):
        self.widget.fill_values()
    
    def build_dynamic_fields(self) -> [QWidget]:
        context = self.field_builder.start(self.input_event)
        context.setup_on_type_change_callback(self.on_type_changed)
        context.setup_on_choose_key_callback(self.prompt_choose_key_dialog)
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
