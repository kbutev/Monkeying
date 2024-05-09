from typing import Protocol
from Presenter.Presenter import Presenter
from MainView.ShowScriptsWidget import ShowScriptsWidgetProtocol
from Service.SettingsManager import SettingsManagerField
from Service import SettingsManager
from Utilities import Path as PathUtils
from Utilities.Path import Path


class ShowScriptsWidgetRouter(Protocol):
    def open_script(self, parent, item): pass

class ShowScriptsPresenter(Presenter):
    widget: ShowScriptsWidgetProtocol = None
    router: ShowScriptsWidgetRouter = None
    
    working_dir: Path
    file_format: str
    
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
        files_list = PathUtils.directory_file_list(self.working_dir, self.file_format)
        
        print(f'command files found in working directory \'{self.working_dir}\':')
        for file in files_list:
            print(file)
        
        self.widget.set_data(files_list)
    
    def can_open_script(self, item) -> bool:
        return True
    
    def open_script(self, item):
        self.router.open_script(self.widget, item)
