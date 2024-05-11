
JSON_REPEAT_COUNT = 'repeat-count'
JSON_REPEAT_FOREVER = 'repeat-forever'
JSON_NOTIFY_START = 'notify-start'
JSON_NOTIFY_END = 'notify-end'

class ScriptConfiguration:
    repeat_count = 0
    repeat_forever = False
    notify_on_start = False
    notify_on_end = False
    
    def json(self):
        return {
            JSON_REPEAT_COUNT: self.repeat_count,
            JSON_REPEAT_FOREVER: self.repeat_forever,
            JSON_NOTIFY_START: self.notify_on_start,
            JSON_NOTIFY_END: self.notify_on_end
        }
    
    def read_from_json(self, json):
        self.repeat_count = json[JSON_REPEAT_COUNT]
        self.repeat_forever = json[JSON_REPEAT_FOREVER]
        self.notify_on_start = json[JSON_NOTIFY_START]
        self.notify_on_end = json[JSON_NOTIFY_END]
