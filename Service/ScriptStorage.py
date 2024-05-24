from kink import di
from Model.ScriptData import ScriptData
from Model.ScriptSummary import ScriptSummary
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
    
    def write_script_data_to_file(self, script: ScriptData, permissions='w', encoding="utf-8"):
        path = self.file_path.absolute
        
        self.logger.info(f"write data to \'{path}\'")

        result = self.script_data_parser.parse_to_json(script)
        file = open(path, permissions, encoding=encoding)
        file.write(result)
        file.close()
        
        self.logger.info(f"data written {path}")
    
    def read_script_data_from_file(self, permissions='r', encoding="utf-8", ignore_actions=False) -> ScriptData:
        path = self.file_path.absolute
        
        self.logger.info(f"read data from \'{path}\'...")
        
        file = open(path, permissions, encoding=encoding)
        file_contents = file.read()
        
        try:
            if len(file_contents) == 0:
                raise ValueError("empty file")
            
            result = self.script_data_parser.parse_to_script(file_contents, ignore_actions=ignore_actions)
        except Exception as error:
            self.logger.error(f"reading failed, error: {error}")
            file.close()
            raise error
        
        file.close()
        
        result.set_file_path(self.file_path)
        
        self.logger.info("data read successfully")
        
        return result
    
    def read_script_summary_from_file(self, permissions='r', encoding="utf-8") -> ScriptSummary:
        script = self.read_script_data_from_file(permissions=permissions, encoding=encoding, ignore_actions=True)
        return script.get_summary()
