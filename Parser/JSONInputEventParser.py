from typing import Protocol
from kink import inject
from Model.JSONInputEvent import JSONInputEvent


class JSONInputEventParserProtocol(Protocol):
    def build_entry(self, time, event_type) -> JSONInputEvent: return None


@inject(use_factory=True, alias=JSONInputEventParserProtocol)
class JSONInputEventParser(JSONInputEventParserProtocol):
    INDENT = 2
    
    def build_entry(self, time, event_type) -> JSONInputEvent:
        entry = JSONInputEvent()
        entry.set_time(time)
        entry.set_type(event_type)
        return entry
