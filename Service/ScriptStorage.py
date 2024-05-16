from kink import di
from Model.ScriptData import ScriptData
from Parser.ScriptDataParser import ScriptDataParserProtocol
from Utilities.Logger import LoggerProtocol
from Utilities.Path import Path


class ScriptStorage:
    
    # - Init
    
    def __init__(self, path: Path):
        self.file_path = path
        self.script_data_parser = di[ScriptDataParserProtocol]
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def get_file_path(self) -> Path: return self.file_path
    def set_file_path(self, path): self.file_path = path
    
    # - Actions
    
    def write_to_file(self, script: ScriptData, permissions='w', encoding="utf-8"):
        path = self.file_path.absolute
        
        self.logger.info(f"write data to \'{path}\'")
        
        file = open(path, permissions, encoding=encoding)
        result = self.script_data_parser.parse_to_json(script)
        file.write(result)
        file.close()
        
        self.logger.info(f"data written {path}")
    
    def read_from_file(self, permissions='r', encoding="utf-8") -> ScriptData:
        path = self.file_path.absolute
        
        self.logger.info(f"read data from \'{path}\'")
        
        file = open(path, permissions, encoding=encoding)
        file_contents = file.read()
        result = self.script_data_parser.parse_to_script(file_contents)
        result.set_file_path(self.file_path)
        file.close()
        
        self.logger.info("data read successfully")
        
        return result
