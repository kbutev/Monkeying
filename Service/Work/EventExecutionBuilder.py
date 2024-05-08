from Model.InputEvent import InputEvent
from Model.ScriptInputEvent import ScriptInputEvent
from Parser.EventActionParser import EventActionParserProtocol, EventActionParser
from Service.EventStorage import EventStorage
from Service.Work.EventExecution import EventKeyExecution, ScriptExecution


class EventExecutionBuilder:
    event_parser: EventActionParserProtocol = EventActionParser()
    
    def build(self, input_event: InputEvent, print_callback = None):
        event_type = input_event.event_type()
        
        if event_type.is_keyboard() or event_type.is_mouse():
            result = EventKeyExecution(input_event, print_callback)
        elif isinstance(input_event, ScriptInputEvent):
            storage = EventStorage()
            storage.read_from_file(input_event.path)
            events = list(map(lambda event: self.event_parser.parse_json(event), storage.data.copy()))
            result = ScriptExecution(events, self)
        else:
            assert False
        
        result.print_callback = print_callback
        
        return result
