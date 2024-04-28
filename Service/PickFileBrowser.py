from typing import Protocol
from PyQt5.QtWidgets import QFileDialog


class PickFileBrowserProtocol(Protocol):
    def pick_file(self, parent, title, filter, directory) -> str: pass

class PickFileBrowser(PickFileBrowserProtocol):
    def __init__(self):
        super(PickFileBrowser, self).__init__()
    
    def pick_file(self, parent, title, filter, directory="scripts"):
        # Dumbest API ever
        selection = QFileDialog.getSaveFileName(parent, title, directory, f'{filter}(*.{filter})')
        
        if len(selection) > 0:
            return selection[0]
        else:
            return None
