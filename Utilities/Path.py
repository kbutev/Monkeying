import pathlib
from dataclasses import dataclass
from os import listdir
from os.path import isfile, join


@dataclass
class Path:
    absolute: str
    
    def copy(self):
        return Path(self.absolute)
    
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
    
    def stem(self) -> str:
        if len(self.absolute) == 0:
            return ''
        
        return pathlib.Path(self.absolute).stem
    
    def base_path(self) -> str:
        parts = self.components()
        
        if len(parts) <= 1:
            return ''
        
        parts.pop()
        
        result = ''
        
        for part in parts:
            result += part
        
        return result
    
    def append_to_end(self, value):
        assert system_file_separator() not in value
        self.absolute += value


def system_file_separator() -> str:
    return "/"


def combine_paths(first, second):
    if isinstance(first, Path): first = first.absolute
    if isinstance(second, Path): second = second.absolute
    if len(first) == 0: return Path(second)
    if len(second) == 0: return Path(first)
    
    return Path(first + system_file_separator() + second)


def filter_file_format(name, file_format) -> bool:
    return len(name) > len(file_format) + 1 and name.endswith(f'.{file_format}')


def directory_file_list(directory, file_format = None) -> []:
    if isinstance(directory, Path): directory = directory.absolute
    
    file_names = [f for f in listdir(directory) if isfile(join(directory, f))]
    
    # File format filter
    if file_format is not None:
        file_names = list(filter(lambda name: filter_file_format(name, file_format), file_names))
        
    result = []
    
    for file in file_names:
        result.append(combine_paths(directory, file))
    
    return result
