from Model.InputEventType import InputEventType
from pynput.mouse import Button as MouseKey


KEY_TIME = "t"
KEY_TYPE = "e"
KEY_KEYSTROKE = "v"
KEY_POINT_X = "x"
KEY_POINT_Y = "y"
KEY_POINT_DT_X = "dt_x"
KEY_POINT_DT_Y = "dt_y"
KEY_MESSAGE = "message"
KEY_MESSAGE_NOTIFICATION = "notification"
KEY_PATH = "path"


def default_event_as_json(type, time=0) -> dict:
    if isinstance(type, str):
        type = InputEventType(type)
    
    assert isinstance(type, InputEventType)
    
    result = dict()
    result[KEY_TYPE] = type.value
    
    if type.is_keyboard():
        result[KEY_KEYSTROKE] = 'x'
    elif type.is_mouse():
        result[KEY_KEYSTROKE] = MouseKey.right.value
    elif type == InputEventType.MESSAGE:
        result[KEY_MESSAGE] = ''
        result[KEY_MESSAGE_NOTIFICATION] = False
    elif type == InputEventType.RUN_SCRIPT:
        result[KEY_PATH] = ''
    
    result[KEY_TIME] = str(time)
    return result
