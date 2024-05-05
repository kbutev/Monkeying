from typing import Protocol
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout


class ChooseKeyboardKeyWidgetDelegate(Protocol):
    pass

class ChooseKeyboardKeyWidget(QWidget):
    delegate: ChooseKeyboardKeyWidgetDelegate
    
    def __init__(self, parent=None):
        super(ChooseKeyboardKeyWidget, self).__init__(parent)
        self.setup()
        
    def setup(self):
        layout = QVBoxLayout(self)
        label = QLabel('Press any keyboard key')
        layout.addWidget(label)
        self.setLayout(layout)
