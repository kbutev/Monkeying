import enum

from PyQt5.QtWidgets import *
from typing import Protocol

from Service.SettingsManager import SettingsManagerField


class SettingsWidgetProtocol(Protocol):
    def setup_field(self, parameter: SettingsManagerField, value): pass

class SettingsWidgetDelegate(Protocol):
    def save_settings(self): pass
    def assign_hotkey(self, sender): pass

class SettingsWidget(QWidget):
    delegate: SettingsWidgetDelegate = None
    
    play_hotkey_button: QPushButton
    pause_hotkey_button: QPushButton
    record_hotkey_button: QPushButton
    
    def __init__(self, parent=None):
        super(SettingsWidget, self).__init__(parent)
        self.setup()
    
    def setup(self):
        layout = QVBoxLayout()

        hotkey_label = QLabel('Script Hotkeys')
        layout.addWidget(hotkey_label)
        
        play_stop_layout = QHBoxLayout()
        layout.addLayout(play_stop_layout)
        play_hotkey_label = QLabel('Play/stop')
        play_stop_layout.addWidget(play_hotkey_label)
        self.play_hotkey_button = QPushButton('x')
        play_stop_layout.addWidget(self.play_hotkey_button)
        self.play_hotkey_button.clicked.connect(self.on_play_stop_hotkey)
        
        pause_layout = QHBoxLayout()
        layout.addLayout(pause_layout)
        pause_resume_label = QLabel('Pause/resume')
        pause_layout.addWidget(pause_resume_label)
        self.pause_hotkey_button = QPushButton('x')
        pause_layout.addWidget(self.pause_hotkey_button)
        self.pause_hotkey_button.clicked.connect(self.on_resume_pause_hotkey)
        
        record_layout = QHBoxLayout()
        layout.addLayout(record_layout)
        record_label = QLabel('Record')
        record_layout.addWidget(record_label)
        self.record_hotkey_button = QPushButton('x')
        record_layout.addWidget(self.record_hotkey_button)
        self.record_hotkey_button.clicked.connect(self.on_record_hotkey)
        
        self.setLayout(layout)
    
    def setup_field(self, parameter: SettingsManagerField, value):
        match parameter:
            case SettingsManagerField.PLAY_HOTKEY:
                self.play_hotkey_button.setText(value)
            case SettingsManagerField.PAUSE_HOTKEY:
                self.pause_hotkey_button.setText(value)
            case SettingsManagerField.RECORD_HOTKEY:
                self.record_hotkey_button.setText(value)
    
    def on_play_stop_hotkey(self):
        self.delegate.assign_hotkey(SettingsManagerField.PLAY_HOTKEY)
    
    def on_resume_pause_hotkey(self):
        self.delegate.assign_hotkey(SettingsManagerField.PAUSE_HOTKEY)
    
    def on_record_hotkey(self):
        self.delegate.assign_hotkey(SettingsManagerField.RECORD_HOTKEY)
