import json
from typing import Protocol
from kink import di, inject
from Model.ScriptActions import ScriptActions
from Parser.ScriptActionParser import ScriptActionParserProtocol


class ScriptActionsParserProtocol(Protocol):
    def parse_to_json(self, actions: ScriptActions) -> str: pass
    def parse_to_list(self, actions: ScriptActions) -> list: pass
    def parse_to_actions(self, json) -> ScriptActions: pass


@inject(use_factory=True, alias=ScriptActionsParserProtocol)
class ScriptActionsParser(ScriptActionsParserProtocol):
    
    def __init__(self):
        self.inner_parser = di[ScriptActionParserProtocol]
    
    def parse_to_json(self, actions: ScriptActions) -> str:
        actions = self.parse_to_list(actions)
        return json.dumps(actions)
    
    def parse_to_list(self, actions: ScriptActions) -> list:
        return list(map(lambda action: self.inner_parser.parse_to_json(action), actions.data.copy()))
    
    def parse_to_actions(self, data) -> ScriptActions:
        if isinstance(data, str):
            data = json.loads(data)
        
        assert isinstance(data, list)
        
        result = []
        
        for item in data:
            result.append(self.inner_parser.parse_to_action(item))
        
        return ScriptActions(result)
