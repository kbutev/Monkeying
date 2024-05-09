from os import listdir
from os.path import isfile, join


class Path:
    absolute: str
    
    def __init__(self, path):
        self.absolute = path
    
    def is_empty(self) -> bool:
        return len(self.absolute) == 0
    
    def components(self) -> []:
        if len(self.absolute) == 0:
            return []
        
        return self.absolute.split(system_file_separator())
    
    def last_component(self) -> str:
        parts = self.components()
        
        if len(parts) == 0:
            return ''
        
        return parts[len(parts)-1]
    
    def base_path(self) -> str:
        parts = self.components()
        
        if len(parts) <= 1:
            return ''
        
        parts.pop()
        
        result = ''
        
        for part in parts:
            result += part
        
        return result

def system_file_separator() -> str:
    return "/"

def combine_paths(first, second):
    if isinstance(first, Path): first = first.absolute
    if isinstance(second, Path): second = second.absolute
    if len(first) == 0: return Path(second)
    if len(second) == 0: return Path(first)
    
    return Path(first + system_file_separator() + second)

def directory_file_list(directory, file_format = None) -> []:
    if isinstance(directory, Path): directory = directory.absolute
    
    result = [f for f in listdir(directory) if isfile(join(directory, f))]
    
    if file_format is not None:
        result = list(filter(lambda name: len(name) > len(file_format) + 1 and name.endswith(f'.{file_format}'), result))
    
    return result
