from typing import Protocol
from PyQt5.QtWidgets import QFileDialog
from kink import inject
from Utilities.Path import Path


class PickFileBrowserProtocol(Protocol):
    def pick_file(self, parent, title, filter, directory) -> Path: pass


@inject
class PickFileBrowser(PickFileBrowserProtocol):
    def __init__(self):
        super(PickFileBrowser, self).__init__()
    
    def pick_file(self, parent, title, filter, directory):
        if isinstance(directory, Path):
            directory = directory.absolute
        
        # Dumbest API ever
        selection = QFileDialog.getSaveFileName(parent, title, directory, f'{filter}(*.{filter})')
        
        if len(selection) > 0:
            return Path(selection[0])
        else:
            return None
