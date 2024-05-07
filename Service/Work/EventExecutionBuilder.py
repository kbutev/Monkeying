from typing import Protocol

from Model.InputEvent import InputEvent
from Service.Work.EventExecution import EventKeyExecution

class EventExecutionBuilderProtocol(Protocol):
    def build(self, event: InputEvent, print_callback=None): pass

class EventExecutionBuilder:
    def build(self, event: InputEvent, print_callback = None):
        if event.event_type().is_keyboard() or event.event_type().is_mouse():
            result = EventKeyExecution(event, print_callback)
        else:
            assert False
        
        return result
