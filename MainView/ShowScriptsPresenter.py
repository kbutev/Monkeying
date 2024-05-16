from typing import Protocol
from kink import di
from Model.ScriptData import ScriptData
from Presenter.Presenter import Presenter
from MainView.ShowScriptsWidget import ShowScriptsWidgetProtocol
from Service.ScriptStorage import ScriptStorage
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from Utilities import Path as PathUtils
from Utilities.Logger import LoggerProtocol
from Utilities.SimpleWorker import run_in_background


class ShowScriptsWidgetRouter(Protocol):
    def open_script(self, parent, script: ScriptData): pass


class ShowScriptsPresenter(Presenter):
    
    # - Init
    
    def __init__(self):
        super(ShowScriptsPresenter, self).__init__()
        settings = di[SettingsManagerProtocol]
        self.widget = None
        self.router = None
        self.working_dir = settings.field_value(SettingsManagerField.SCRIPTS_PATH)
        self.file_format = settings.field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT)
        self.scripts = []
        self.logger = di[LoggerProtocol]
    
    # - Property
    
    def get_widget(self) -> ShowScriptsWidgetProtocol: return self.widget
    def set_widget(self, widget): self.widget = widget
    def get_router(self) -> ShowScriptsWidgetRouter: return self.router
    def set_router(self, router): self.router = router
    
    # - Setup
    
    def setup(self):
        self.reload_data()
    
    # - Actions
    
    def start(self):
        assert self.widget is not None
        
        self.logger.info('start presenter')
        self.setup()
    
    def reload_data(self):
        self.logger.info('reloading data...')
        
        run_in_background(self._load_script_data_in_background, self._finish_loading_script_data)
    
    def _load_script_data_in_background(self):
        result = []
        
        file_list = PathUtils.directory_file_list(self.working_dir, self.file_format)
        
        script_names = []
        
        for file_path in file_list:
            storage = ScriptStorage(file_path)
            script = storage.read_from_file()
            name = script.info.name
            script_names.append(name)
            result.append(script)
        
        return result
    
    def _finish_loading_script_data(self, result):
        self.logger.info(f'finished loading script data, found {len(result)} scripts in work directory')
        
        self.scripts = result
        
        script_names = []
        
        for script in self.scripts:
            script_names.append(script.get_info().name)
        
        self.widget.set_data(script_names)
    
    # Script actions
    
    def can_open_script(self, item) -> bool: return True
    
    def open_script(self, index):
        assert index >= 0 and index < len(self.scripts)
        script = self.scripts[index]
        self.router.open_script(self.widget, script)
