
from os import listdir
from os.path import isfile, join
from typing import Protocol

from Presenter.Presenter import Presenter
from MainView.ShowScriptsWidget import ShowScriptsWidgetProtocol


class ShowScriptsWidgetRouter(Protocol):
    def open_script(self, item): pass

class ShowScriptsPresenter(Presenter):
    widget: ShowScriptsWidgetProtocol = None
    router: ShowScriptsWidgetRouter = None
    
    working_dir = 'scripts'
    file_format = 'json'
    
    def __init__(self):
        super(ShowScriptsPresenter, self).__init__()
    
    def start(self):
        assert self.widget is not None
        
        print('start presenter')
        self.setup()
    
    def setup(self):
        files_list = [f for f in listdir(self.working_dir) if isfile(join(self.working_dir, f))]
        files_list = list(filter(lambda name: len(name) > len(self.file_format)+1 and name.endswith(f'.{self.file_format}'), files_list))
        
        print(f'command files found in working directory \'{self.working_dir}\':')
        for file in files_list:
            print(file)
        
        self.widget.set_data(files_list)
    
    def can_open_script(self, item) -> bool:
        return True
    
    def open_script(self, item):
        self.router.open_script(self.widget, item)
