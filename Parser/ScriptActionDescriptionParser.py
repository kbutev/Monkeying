from dataclasses import dataclass
from typing import Protocol
from kink import inject, di
from Model.ScriptActionDescription import ScriptActionDescription
from Model.ScriptActionType import ScriptActionType
from Model.ScriptActions import ScriptActions
from Model.ScriptInputEventAction import ScriptInputEventAction
from Parser.ScriptActionParser import ScriptActionParserProtocol


@dataclass
class Grouping:
    type: ScriptActionType
    
    def match_action(self, action):
        return action.action_type() == self.type


class ScriptActionDescriptionParserProtocol(Protocol):
    def parse(self, action) -> ScriptActionDescription: pass
    def parse_actions(self, actions: ScriptActions, group_options: Grouping = None) -> [ScriptActionDescription]: pass


@inject(use_factory=True, alias=ScriptActionDescriptionParserProtocol)
class ScriptActionDescriptionParser(ScriptActionDescriptionParserProtocol):
    
    def __init__(self):
        self.inner_parser = di[ScriptActionParserProtocol]
    
    def parse(self, action) -> ScriptActionDescription:
        timestamp = "{:.3f}".format(action.time())
        type = action.action_type().name
        value = action.value_as_string()
        return ScriptActionDescription(timestamp, type, value)
    
    def parse_actions(self, actions: ScriptActions, group_options: Grouping = None) -> [ScriptActionDescription]:
        result = []
        previous_events = []
        group_enabled = group_options is not None
        
        for action in actions.data:
            
            # Group logic
            if group_enabled:
                if group_options.match_action(action) and len(previous_events) >= 2:
                    if group_options.match_action(previous_events[0]) and group_options.match_action(previous_events[1]):
                        result.pop()
            
            if len(previous_events) >= 2:
                previous_events.pop(0)
            
            result.append(self.parse(action))
            previous_events.append(action)
        
        return result

