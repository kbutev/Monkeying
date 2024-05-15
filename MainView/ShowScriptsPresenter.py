from typing import Protocol
from kink import di
from Presenter.Presenter import Presenter
from MainView.ShowScriptsWidget import ShowScriptsWidgetProtocol
from Service.ScriptStorage import ScriptStorage
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from Utilities import Path as PathUtils
from Utilities.Logger import LoggerProtocol


class ShowScriptsWidgetRouter(Protocol):
    def open_script(self, parent, script_name, script_path): pass


class ShowScriptsPresenter(Presenter):
    
    # - Init
    
    def __init__(self):
        super(ShowScriptsPresenter, self).__init__()
        settings = di[SettingsManagerProtocol]
        self.widget = None
        self.router = None
        self.working_dir = settings.field_value(SettingsManagerField.SCRIPTS_PATH)
        self.file_format = settings.field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT)
        self.script_files = []
        self.script_names = []
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
    
    # Script actions
    
    def can_open_script(self, item) -> bool: return True
    
    def open_script(self, index):
        assert index >= 0 and index < len(self.script_files)
        name = self.script_names[index]
        script_path = self.script_files[index]
        self.router.open_script(self.widget, name, script_path)
