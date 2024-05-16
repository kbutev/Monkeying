from dataclasses import dataclass

JSON_REPEAT_COUNT = 'repeat-count'
JSON_REPEAT_FOREVER = 'repeat-forever'
JSON_NOTIFY_START = 'notify-start'
JSON_NOTIFY_END = 'notify-end'


class ScriptConfiguration:
    
    def __init__(self):
        self.repeat_count = 0
        self.repeat_forever = False
        self.notify_on_start = False
        self.notify_on_end = False
    
    def copy(self):
        result = ScriptConfiguration()
        result.repeat_count = self.repeat_count
        result.repeat_forever = self.repeat_forever
        result.notify_on_start = self.notify_on_start
        result.notify_on_end = self.notify_on_end
        return result

