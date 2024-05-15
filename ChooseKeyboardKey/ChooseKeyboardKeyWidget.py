from typing import Protocol
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout


class ChooseKeyboardKeyWidgetDelegate(Protocol):
    pass


class ChooseKeyboardKeyWidget(QWidget):
    
    # - Init
    
    def __init__(self, parent=None):
        super(ChooseKeyboardKeyWidget, self).__init__(parent)
        self.delegate = None
        self.setup()
    
    # - Properties
    
    def get_delegate(self) -> ChooseKeyboardKeyWidgetDelegate: return self.delegate
    def set_delegate(self, delegate): self.delegate = delegate
    
    # - Setup
    
    def setup(self):
        layout = QVBoxLayout(self)
        label = QLabel('Press any keyboard key')
        layout.addWidget(label)
        self.setLayout(layout)
