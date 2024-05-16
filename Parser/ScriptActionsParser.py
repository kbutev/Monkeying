import json
from typing import Protocol
from kink import di, inject
from Model.ScriptEvents import ScriptEvents
from Parser.ScriptActionParser import ScriptActionParserProtocol


class ScriptActionsParserProtocol(Protocol):
    def parse_to_json(self, events: ScriptEvents) -> str: pass
    def parse_to_list(self, events: ScriptEvents) -> list: pass
    def parse_to_events(self, json) -> ScriptEvents: pass


@inject(use_factory=True, alias=ScriptActionsParserProtocol)
class ScriptActionsParser(ScriptActionsParserProtocol):
    
    def __init__(self):
        self.inner_parser = di[ScriptActionParserProtocol]
    
    def parse_to_json(self, events: ScriptEvents) -> str:
        events = self.parse_to_list(events)
        return json.dumps(events)
    
    def parse_to_list(self, events: ScriptEvents) -> list:
        return list(map(lambda event: self.inner_parser.parse_to_json(event).values, events.data.copy()))
    
    def parse_to_events(self, data) -> ScriptEvents:
        if isinstance(data, str):
            data = json.loads(data)
        
        assert isinstance(data, list)
        
        result = []
        
        for item in data:
            result.append(self.inner_parser.parse_to_event(item))
        
        return ScriptEvents(result)
