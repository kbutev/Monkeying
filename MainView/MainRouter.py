from typing import Protocol
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from kink import di
from ChooseKeyboardKey.ChooseKeyboardKeyPresenter import ChooseKeyboardKeyPresenter
from ChooseKeyboardKey.ChooseKeyboardKeyWidget import ChooseKeyboardKeyWidget
from ConfigureScript.ConfigureScriptRouter import ConfigureScriptRouter
from MainView.MainWidget import MainWidget
from MainView.SettingsPresenter import SettingsPresenter
from Model.ScriptData import ScriptData
from OpenScriptView.OpenScriptRouter import OpenScriptRouter
from MainView.ShowScriptsPresenter import ShowScriptsPresenter
from MainView.RecordScriptPresenter import RecordScriptPresenter
from Provider.ScriptDataProvider import ScriptDataProvider
from Service.PickFileBrowser import PickFileBrowser
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from Utilities.Path import Path


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
        
        window = QDialog(parent)
        window.setWindowTitle(f'Run {script_data.info.name}')
        window.setWindowFlags(window.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        layout = QVBoxLayout()
        
        router = OpenScriptRouter(window, script_data)
        router.observer = self
        router.setup()
        
        window.closeEvent = router.widget.closeEvent
        layout.addWidget(router.widget)
        window.setLayout(layout)
        window.exec()
        
    def on_script_closed(self):
        self.show_scripts_presenter.reload_data()
    
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
            assert False
    
    def pick_save_file(self, directory) -> Path:
        return self.pick_file_browser.pick_file(self.widget, "Save File", self.file_format, directory)
    
    def configure_script(self, parent, script):
        router = ConfigureScriptRouter(script, True)
        router.setup(parent)
        router.widget.exec()
    
    def prompt_choose_key_dialog(self, sender):
        dialog = QDialog(self.widget)
        dialog.setWindowTitle(f'Choose key')
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        dialog.resize(320, 320)
        dialog.setMinimumSize(320, 320)
        dialog.setMaximumSize(320, 320)
        
        layout = QVBoxLayout()
        widget = ChooseKeyboardKeyWidget()
        presenter = ChooseKeyboardKeyPresenter(lambda result: self.on_key_chosen(sender, dialog, result))
        widget.set_delegate(presenter)
        layout.addWidget(widget)
        presenter.start()
        dialog.setLayout(layout)
        
        dialog.exec()
    
    def on_key_chosen(self, sender, dialog, result):
        dialog.close()
        self.settings_presenter.on_key_chosen(sender, result)
