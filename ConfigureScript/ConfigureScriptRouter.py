from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from ConfigureScript.ConfigureScriptPresenter import ConfigureScriptPresenter
from ConfigureScript.ConfigureScriptWidget import ConfigureScriptWidget
from Model.ScriptData import ScriptData


class ConfigureScriptRouterObserver:
    def on_exit_config_script(self, result: ScriptData): pass


class ConfigureScriptRouter:
    
    # - Init
    
    def __init__(self, script_data: ScriptData, save_on_close):
        self.observer = None
        self.widget = None
        self.presenter = ConfigureScriptPresenter(script_data)
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
    
    def close(self, result: ScriptData):
        self.widget.close()
        
        if self.observer is not None:
            self.observer.on_exit_config_script(result)
            self.observer = None
