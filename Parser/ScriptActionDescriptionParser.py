from dataclasses import dataclass
from typing import Protocol
from kink import inject, di
from Model.InputEvent import InputEventDescription, InputEvent
from Model.InputEventType import InputEventType
from Parser.ScriptActionParser import ScriptActionParser


@dataclass
class Grouping:
    type: InputEventType
    
    def match_event(self, event):
        return event.event_type() == self.type


class ScriptActionDescriptionParserProtocol(Protocol):
    def parse(self, event) -> InputEventDescription: pass
    def parse_list(self, events, group_options: Grouping = None) -> [InputEventDescription]: pass


@inject(use_factory=True, alias=ScriptActionDescriptionParserProtocol)
class ScriptActionDescriptionParser(ScriptActionDescriptionParserProtocol):
    
    def __init__(self):
        pass
    
    def parse(self, event) -> InputEventDescription:
        if not isinstance(event, InputEvent):
            event = self.inner_parser.parse_to_json(event)
            
        assert isinstance(event, InputEvent)
        
        timestamp = "{:.3f}".format(event.time())
        type = event.event_type().name
        value = event.value_as_string()
        result = InputEventDescription(timestamp, type, value)
        return result
    
    def parse_list(self, events, group_options: Grouping = None) -> [InputEventDescription]:
        result = []
        previous_events = []
        group_enabled = group_options is not None
        
        for event in events:
            
            # Group logic
            if group_enabled:
                if group_options.match_event(event) and len(previous_events) >= 2:
                    if group_options.match_event(previous_events[0]) and group_options.match_event(previous_events[1]):
                        result.pop()
            
            if len(previous_events) >= 2:
                previous_events.pop(0)
            
            result.append(self.parse(event))
            previous_events.append(event)
        
        return result

