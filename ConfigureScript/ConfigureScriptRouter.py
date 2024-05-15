from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from ConfigureScript.ConfigureScriptPresenter import ConfigureScriptPresenter
from ConfigureScript.ConfigureScriptWidget import ConfigureScriptWidget
from Model.ScriptInfo import ScriptInfo
from Service.ScriptStorage import ScriptStorage


class ConfigureScriptRouterObserver:
    def on_exit_config_script(self, result: ScriptInfo): pass


class ConfigureScriptRouter:
    
    # - Init
    
    def __init__(self, storage: ScriptStorage):
        self.observer = None
        self.widget = None
        self.presenter = ConfigureScriptPresenter(storage)
        self.completion = None
    
    # - Properties
    
    def get_widget(self) -> QDialog: return self.widget
    def set_widget(self, widget): self.widget = widget
    def get_observer(self) -> ConfigureScriptRouterObserver: return self.observer
    def set_observer(self, observer): self.observer = observer
    
    # - Setup
    
    def setup(self, parent):
        dialog = QDialog(parent)
        dialog.setWindowTitle(f'Configurate script')
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        dialog.resize(640, 640)
        dialog.setMinimumSize(640, 640)
        dialog.setMaximumSize(640, 640)
        
        layout = QVBoxLayout()
        widget = ConfigureScriptWidget()
        widget.set_delegate(self.presenter)
        self.presenter.set_widget(widget)
        self.presenter.set_router(self)
        layout.addWidget(widget)
        self.presenter.start()
        
        dialog.setLayout(layout)
        
        self.widget = dialog
    
    # - Actions
    
    def close(self):
        self.widget.close()
        
        if self.observer is not None:
            self.observer.on_exit_config_script(self.presenter.storage.info)
            self.observer = None
