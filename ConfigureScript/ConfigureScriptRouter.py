from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from ConfigureScript.ConfigureScriptPresenter import ConfigureScriptPresenter
from ConfigureScript.ConfigureScriptWidget import ConfigureScriptWidget
from Model.ScriptInfo import ScriptInfo
from Service.ScriptStorage import ScriptStorage

class ConfigureScriptRouterObserver:
    def on_exit_config_script(self, result: ScriptInfo): pass

class ConfigureScriptRouter:
    observer: ConfigureScriptRouterObserver = None
    
    widget: QDialog = None
    
    presenter: ConfigureScriptPresenter
    
    completion = None
    
    def __init__(self, storage: ScriptStorage):
        self.presenter = ConfigureScriptPresenter(storage)
    
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
        
        if self.observer is not None:
            self.observer.on_exit_config_script(self.presenter.storage.info)
            self.observer = None
