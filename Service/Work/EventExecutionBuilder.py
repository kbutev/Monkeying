from typing import Protocol, Any
from kink import di, inject
from Model.InputEvent import InputEvent
from Model.MessageInputEvent import MessageInputEvent
from Model.ScriptInputEvent import ScriptInputEvent
from Service.ScriptStorage import ScriptStorage
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from Service.Work.EventExecutionCluster import EventMessageExecution, ScriptExecution, EventKeyExecution


class EventExecutionBuilderProtocol(Protocol):
    def build(self, input_event: InputEvent) -> Any: return None


@inject(use_factory=True, alias=EventExecutionBuilderProtocol)
class EventExecutionBuilder(EventExecutionBuilderProtocol):
    
    def __init__(self):
        settings = di[SettingsManagerProtocol]
        self.working_dir = settings.field_value(SettingsManagerField.SCRIPTS_PATH)
    
    def build(self, input_event: InputEvent) -> Any:
        event_type = input_event.event_type()
        
        if event_type.is_keyboard() or event_type.is_mouse():
            result = EventKeyExecution(input_event)
        elif isinstance(input_event, MessageInputEvent):
            result = EventMessageExecution(input_event)
        elif isinstance(input_event, ScriptInputEvent):
            script_file_path = input_event.path
            script_data = ScriptStorage(script_file_path).read_from_file()
            result = ScriptExecution(script_file_path, script_data.events, self)
        else:
            assert False
        
        return result
