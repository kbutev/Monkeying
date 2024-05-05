from typing import Protocol

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout

from MainView.MainWidget import MainWidget
from OpenScriptView.OpenScriptRouter import OpenScriptRouter
from MainView.ShowScriptsPresenter import ShowScriptsPresenter
from MainView.RecordScriptPresenter import RecordScriptPresenter
from Service.PickFileBrowser import PickFileBrowserProtocol, PickFileBrowser


class MainRouter(Protocol):
    widget: MainWidget
    show_scripts_presenter = ShowScriptsPresenter()
    rec_presenter = RecordScriptPresenter()
    
    pick_file_browser: PickFileBrowserProtocol = PickFileBrowser()
    
    script_file_format = 'json'
    
    def __init__(self):
        pass
    
    def setup(self):
        self.widget = MainWidget()
        self.widget.scripts_widget.delegate = self.show_scripts_presenter
        self.widget.scripts_widget.router = self
        self.widget.rec_widget.delegate = self.rec_presenter
        self.widget.rec_widget.router = self
        self.widget.delegate = self
        self.show_scripts_presenter.widget = self.widget.scripts_widget
        self.show_scripts_presenter.router = self
        self.rec_presenter.widget = self.widget.rec_widget
        self.rec_presenter.router = self
        
        self.show_scripts_presenter.start()
    
    def enable_tabs(self, enabled):
        self.widget.tabBar().setEnabled(enabled)
    
    def open_script(self, parent, item):
        assert parent is not None
        assert item is not None
        
        window = QDialog(parent)
        window.setWindowTitle(f'Run {item}')
        window.setWindowFlags(window.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        layout = QVBoxLayout()
        
        router = OpenScriptRouter(item)
        router.setup()
        
        window.closeEvent = router.widget.closeEvent
        layout.addWidget(router.widget)
        window.setLayout(layout)
        window.exec()
    
    def on_current_tab_changed(self, index):
        if index == 0:
            self.rec_presenter.stop()
            self.show_scripts_presenter.start()
        else:
            self.rec_presenter.start()
            self.show_scripts_presenter.stop()
    
    def pick_save_file(self) -> str:
        return self.pick_file_browser.pick_file(self.widget, "Save File", self.script_file_format)
