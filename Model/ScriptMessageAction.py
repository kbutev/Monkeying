from Model.InputEvent import InputEvent
from Model.ScriptAction import ScriptAction
from Model.ScriptActionType import ScriptActionType

FLOAT_ROUND_DECIMALS = 3


class ScriptMessageAction(ScriptAction):
    
    # - Init
    
    def __init__(self, message_string: str, notification, time=0):
        super(ScriptMessageAction, self).__init__()
        self.timestamp = time
        self.message_string = message_string
        self.notification = notification
    
    def copy(self):
        result = ScriptMessageAction(self.message_string, self.notification, self.time())
        return result
    
    # - Properties
    
    def time(self):
        return self.timestamp
    
    def set_time(self, value):
        self.timestamp = round(value, FLOAT_ROUND_DECIMALS)
    
    def notifications_enabled(self) -> bool:
        return self.notification
    
    def set_notifications_enabled(self, value):
        self.notification = value
    
    def message(self) -> str:
        return self.message_string
    
    def set_message(self, value):
        self.message_string = value
    
    def action_type(self) -> ScriptActionType:
        return ScriptActionType.MESSAGE
    
    def value_as_string(self) -> str:
        return f'{self.message_string}'
