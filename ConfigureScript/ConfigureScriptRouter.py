from PyQt5.QtWidgets import QVBoxLayout
from ConfigureScript.ConfigureScriptPresenter import ConfigureScriptPresenter
from ConfigureScript.ConfigureScriptWidget import ConfigureScriptWidget
from Dialog.Dialog import Dialog
from Model.ScriptData import ScriptData
from Utilities.Rect import Rect


class ConfigureScriptRouterDelegate:
    def on_save_script_configuration(self, config: ScriptData): pass


class ConfigureScriptRouter:
    
    # - Init
    
    def __init__(self, presenter: ConfigureScriptPresenter):
        self.dialog = None
        self.presenter = presenter
        self.delegate = None
    
    # - Properties
    
    def get_delegate(self) -> ConfigureScriptRouterDelegate: return self.delegate
    def set_delegate(self, delegate): self.delegate = delegate
    
    # - Setup
    
    def setup(self, parent):
        layout = QVBoxLayout()
        widget = ConfigureScriptWidget()
        widget.set_delegate(self.presenter)
        self.presenter.set_widget(widget)
        self.presenter.set_router(self)
        layout.addWidget(widget)
        self.presenter.start()
        
        dialog = Dialog(parent, desired_size=Rect(640, 640))
        dialog.set_title(f'Configurate script')
        dialog.set_layout(layout)
        dialog.set_delegate(self)
        
        self.dialog = dialog
    
    # - Actions
    
    def close(self):
        self.delegate.on_save_script_configuration(self.presenter.get_script())
        self.dialog.close()
    
    # - DialogRouter
    
    def on_dialog_appear(self, sender): pass
    def on_dialog_disappear(self, sender): pass
    def on_dialog_close(self, sender): pass
