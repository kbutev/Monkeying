from typing import Protocol
from PyQt5.QtWidgets import QVBoxLayout
from kink import di
from ChooseKeyboardKey.ChooseKeyboardKeyPresenter import ChooseKeyboardKeyPresenter
from ChooseKeyboardKey.ChooseKeyboardKeyWidget import ChooseKeyboardKeyWidget
from ConfigureScript.ConfigureScriptPresenter import ConfigureScriptPresenter
from ConfigureScript.ConfigureScriptRouter import ConfigureScriptRouter
from Dialog.Dialog import Dialog, DialogRouter
from MainView.MainWidget import MainWidget
from MainView.SettingsPresenter import SettingsPresenter
from Model.ScriptData import ScriptData
from OpenScriptView.OpenScriptRouter import OpenScriptRouter
from MainView.ShowScriptsPresenter import ShowScriptsPresenter
from MainView.RecordScriptPresenter import RecordScriptPresenter
from Service.PickFileBrowser import PickFileBrowser
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from Utilities.Path import Path
from Utilities.Rect import Rect


class MainRouter(Protocol):
    
    # - Init
    
    def __init__(self):
        settings = di[SettingsManagerProtocol]
        self.widget = None
        self.pick_file_browser = di[PickFileBrowser]
        self.file_format = settings.field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT)
        self.show_scripts_presenter = ShowScriptsPresenter()
        self.rec_presenter = RecordScriptPresenter()
        self.settings_presenter = SettingsPresenter()
    
    # - Properties
    
    def get_widget(self) -> MainWidget: return self.widget
    def get_router(self) -> DialogRouter: return self
    
    # - Setup
    
    def setup(self):
        self.widget = MainWidget()
        self.widget.scripts_widget.set_delegate(self.show_scripts_presenter)
        self.widget.rec_widget.set_delegate(self.rec_presenter)
        self.widget.settings_widget.set_delegate(self.settings_presenter)
        self.widget.set_delegate(self)
        
        self.show_scripts_presenter.set_widget(self.widget.scripts_widget)
        self.show_scripts_presenter.set_router(self)
        
        self.rec_presenter.set_widget(self.widget.rec_widget)
        self.rec_presenter.set_router(self)
        
        self.settings_presenter.set_widget(self.widget.settings_widget)
        self.settings_presenter.set_router(self)
        
        self.show_scripts_presenter.start()
    
    # - Actions
    
    def enable_tabs(self, enabled):
        self.widget.tabBar().setEnabled(enabled)
    
    def open_script(self, parent, script_data: ScriptData):
        assert parent is not None
        assert script_data is not None
        
        script_data = script_data.copy()
        
        dialog = Dialog(parent)
        
        router = OpenScriptRouter(dialog, script_data)
        router.setup()
        
        layout = QVBoxLayout()
        layout.addWidget(router.widget)
        dialog.set_layout(layout)
        dialog.set_title(f'Run {script_data.get_info().name}')
        dialog.set_delegate(router)
        dialog.present()
    
    def on_current_tab_changed(self, index):
        if index == 0:
            self.rec_presenter.stop()
            self.settings_presenter.stop()
            self.show_scripts_presenter.start()
        elif index == 1:
            self.show_scripts_presenter.stop()
            self.settings_presenter.stop()
            self.rec_presenter.start()
        elif index == 2:
            self.rec_presenter.stop()
            self.show_scripts_presenter.stop()
            self.settings_presenter.start()
        else:
            assert False # Invalid tab selected
    
    def pick_save_file(self, directory) -> Path:
        return self.pick_file_browser.pick_file(self.widget, "Save File", self.file_format, directory)
    
    def configure_script(self, parent, script: ScriptData):
        presenter = ConfigureScriptPresenter(script)
        router = ConfigureScriptRouter(presenter)
        router.setup(parent)
        router.set_delegate(self)
        router.dialog.present()
    
    def prompt_choose_key_dialog(self, sender):
        dialog = Dialog(self.widget, desired_size=Rect(320, 320))
        
        layout = QVBoxLayout()
        widget = ChooseKeyboardKeyWidget()
        presenter = ChooseKeyboardKeyPresenter(lambda result: self.on_key_chosen(sender, dialog, result))
        widget.set_delegate(presenter)
        layout.addWidget(widget)
        presenter.start()
        
        dialog.set_title(f'Choose key')
        dialog.set_layout(layout)
        dialog.set_delegate(self)
        dialog.present()
    
    def on_key_chosen(self, sender, dialog, result):
        dialog.close()
        self.settings_presenter.on_key_chosen(sender, result)
    
    # - DialogRouter
    
    def on_dialog_appear(self, sender):
        self.show_scripts_presenter.reload_data()
    
    def on_dialog_disappear(self, sender): pass
    def on_dialog_close(self, sender): pass
    
    # - ConfigureScriptRouterDelegate
    
    def on_save_script_configuration(self, script: ScriptData):
        self.rec_presenter.update_script_configuration(script)
