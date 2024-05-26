from pynput.mouse import Button as MouseKey
from Model.ScriptActionType import ScriptActionType


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
KEY_COMMAND = "command"


def default_event_as_json(type, time=0) -> dict:
    if isinstance(type, str):
        type = ScriptActionType(type)
    
    assert isinstance(type, ScriptActionType)
    
    result = dict()
    result[KEY_TYPE] = type.value
    
    if type.is_keyboard():
        result[KEY_KEYSTROKE] = 'x'
    elif type.is_mouse():
        if (type == ScriptActionType.MOUSE_PRESS or
                type == ScriptActionType.MOUSE_RELEASE or
                type == ScriptActionType.MOUSE_CLICK):
            result[KEY_KEYSTROKE] = MouseKey.left.name
        
        if (type == ScriptActionType.MOUSE_PRESS or
                type == ScriptActionType.MOUSE_RELEASE or
                type == ScriptActionType.MOUSE_MOVE or
                type == ScriptActionType.MOUSE_CLICK):
            result[KEY_POINT_X] = 0
            result[KEY_POINT_Y] = 0
        
        if type == ScriptActionType.MOUSE_SCROLL:
            result[KEY_POINT_DT_X] = 0
            result[KEY_POINT_DT_Y] = 0
    elif type == ScriptActionType.MESSAGE:
        result[KEY_MESSAGE] = ''
        result[KEY_MESSAGE_NOTIFICATION] = False
    elif type == ScriptActionType.RUN_SCRIPT:
        result[KEY_PATH] = ''
    elif type == ScriptActionType.SNAPSHOT:
        result[KEY_PATH] = 'snapshot'
    elif type == ScriptActionType.COMMAND:
        result[KEY_COMMAND] = ''
    else:
        assert False # ScriptAction implement: not implemented
    
    result[KEY_TIME] = str(time)
    return result
