from typing import Protocol
from Presenter.Presenter import Presenter
from MainView.ShowScriptsWidget import ShowScriptsWidgetProtocol
from Service.ScriptStorage import ScriptStorage
from Service.SettingsManager import SettingsManagerField
from Service import SettingsManager
from Utilities import Path as PathUtils
from Utilities.Path import Path


class ShowScriptsWidgetRouter(Protocol):
    def open_script(self, parent, script_name, script_path): pass

class ShowScriptsPresenter(Presenter):
    widget: ShowScriptsWidgetProtocol = None
    router: ShowScriptsWidgetRouter = None
    
    working_dir: Path
    file_format: str
    
    script_files = []
    script_names = []
    
    def __init__(self):
        super(ShowScriptsPresenter, self).__init__()
        
        settings = SettingsManager.singleton
        self.working_dir = settings.field_value(SettingsManagerField.SCRIPTS_PATH)
        self.file_format = settings.field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT)
    
    def start(self):
        assert self.widget is not None
        
        print('start presenter')
        self.setup()
    
    def setup(self):
        self.reload_data()
    
    def reload_data(self):
        file_list = PathUtils.directory_file_list(self.working_dir, self.file_format)
        
        # TODO: optimize
        script_names = []
        
        for file in file_list:
            storage = ScriptStorage(file)
            name = storage.info.name
            script_names.append(name)
        
        self.script_files = file_list
        self.script_names = script_names
        self.widget.set_data(script_names)
    
    def can_open_script(self, item) -> bool:
        return True
    
    def open_script(self, index):
        assert index >= 0 and index < len(self.script_files)
        name = self.script_names[index]
        script_path = self.script_files[index]
        self.router.open_script(self.widget, name, script_path)
