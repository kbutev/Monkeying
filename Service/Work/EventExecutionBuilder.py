from typing import Protocol
from kink import di, inject
from Model.InputEvent import InputEvent
from Model.MessageInputEvent import MessageInputEvent
from Model.ScriptInputEvent import ScriptInputEvent
from Parser.EventActionParser import EventActionParserProtocol
from Service.ScriptStorage import ScriptStorage
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from Service.Work.EventExecutionCluster import EventMessageExecution, ScriptExecution, EventKeyExecution


class EventExecutionBuilderProtocol(Protocol):
    def build(self, event: InputEvent): pass


@inject(use_factory=True, alias=EventExecutionBuilderProtocol)
class EventExecutionBuilder:
    
    def __init__(self):
        settings = di[SettingsManagerProtocol]
        self.working_dir = settings.field_value(SettingsManagerField.SCRIPTS_PATH)
        self.event_parser = di[EventActionParserProtocol]
    
    def build(self, input_event: InputEvent):
        event_type = input_event.event_type()
        
        if event_type.is_keyboard() or event_type.is_mouse():
            result = EventKeyExecution(input_event)
        elif isinstance(input_event, MessageInputEvent):
            result = EventMessageExecution(input_event)
        elif isinstance(input_event, ScriptInputEvent):
            storage = ScriptStorage()
            script_file_path = input_event.path
            storage.read_from_file(script_file_path)
            events = list(map(lambda event: self.event_parser.parse_json(event), storage.data.copy()))
            result = ScriptExecution(script_file_path, events, self)
        else:
            assert False
        
        return result
