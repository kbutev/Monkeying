from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from ConfigureScript.ConfigureScriptPresenter import ConfigureScriptPresenter
from ConfigureScript.ConfigureScriptWidget import ConfigureScriptWidget
from Service.ScriptStorage import ScriptStorage
from Utilities.Path import Path


class ConfigureScriptRouter:
    widget: QDialog = None
    
    storage: ScriptStorage
    presenter: ConfigureScriptPresenter
    
    def __init__(self, script_path: Path):
        self.storage = ScriptStorage(script_path)
        self.presenter = ConfigureScriptPresenter(self.storage)
    
    def setup(self, parent):
        dialog = QDialog(parent)
        dialog.setWindowTitle(f'Configurate script')
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        dialog.resize(640, 640)
        dialog.setMinimumSize(640, 640)
        dialog.setMaximumSize(640, 640)
        
        layout = QVBoxLayout()
        widget = ConfigureScriptWidget()
        widget.delegate = self.presenter
        self.presenter.widget = widget
        self.presenter.router = self
        layout.addWidget(widget)
        self.presenter.start()
        
        dialog.setLayout(layout)
        
        self.widget = dialog
    
    def close(self):
        self.widget.close()
