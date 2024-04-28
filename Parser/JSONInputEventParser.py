from Model.JSONInputEvent import JSONInputEvent


class JSONInputEventParser:
    indent = 2
    
    def build_entry(self, time, event_type) -> JSONInputEvent:
        entry = JSONInputEvent()
        entry.set_time(time)
        entry.set_type(event_type)
        return entry
