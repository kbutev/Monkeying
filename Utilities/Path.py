

class Path:
    absolute: str
    
    def __init__(self, path):
        self.absolute = path


def system_file_separator() -> str:
    return "/"

def combine(first, second):
    if len(first) == 0:
        return second
    
    if len(second) == 0:
        return first
    
    return Path(first + system_file_separator() + second)
