from typing import Protocol, runtime_checkable
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel, QPushButton
from Utilities.Rect import Rect


def build_info_dialog(parent, title, body, desired_size: Rect = Rect(480, 320)):
    dialog = Dialog(parent, desired_size=desired_size)
    dialog.set_title(title)
    
    layout = QVBoxLayout()
    label = QLabel(body)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
    ok_button = QPushButton("Ok")
    layout.addWidget(label)
    layout.addWidget(ok_button)
    ok_button.clicked.connect(dialog.close)
    
    dialog.set_layout(layout)
    return dialog


def build_error_dialog(parent, title, body, desired_size: Rect=Rect(480, 320)):
    dialog = Dialog(parent, desired_size=desired_size)
    dialog.set_title(title)
    
    layout = QVBoxLayout()
    label = QLabel(body)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
    ok_button = QPushButton("Ok")
    layout.addWidget(label)
    layout.addWidget(ok_button)
    ok_button.clicked.connect(dialog.close)
    
    dialog.set_layout(layout)
    return dialog


@runtime_checkable
class DialogRouter(Protocol):
    def on_dialog_appear(self, sender): pass
    def on_dialog_disappear(self, sender): pass
    def on_dialog_close(self, sender): pass


class DummyWidgetDialog:
    
    def __init__(self, widget: DialogRouter):
        self.widget = widget
    
    def get_delegate(self) -> DialogRouter: return self.widget


class Dialog(QDialog):
    
    def __init__(self, parent, desired_size: Rect=None):
        super(Dialog, self).__init__(parent)
        self.delegate = None
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.on_close = None
        
        if desired_size is not None:
            self.set_size(desired_size)
            self.set_min_size(desired_size)
            self.set_max_size(desired_size)
    
    def get_delegate(self) -> DialogRouter: return self.delegate
    def set_delegate(self, delegate: DialogRouter): self.delegate = delegate
    def set_layout(self, value): self.setLayout(value)
    def set_size(self, size: Rect): self.resize(size.width, size.height)
    def set_min_size(self, size: Rect): self.setMinimumSize(size.width, size.height)
    def set_max_size(self, size: Rect): self.setMaximumSize(size.width, size.height)
    def set_title(self, title: str): self.setWindowTitle(title)
    
    def setup_text_body(self, description: str):
        label = QLabel(description)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.set_layout(layout)
    
    def parent_dialog(self):
        parent = self.parent()
        
        while parent is not None:
            if isinstance(parent, Dialog):
                return parent
            elif isinstance(parent, QWidget):
                parent_parent = parent.parent()
                
                if parent_parent is None and isinstance(parent, DialogRouter):
                    return DummyWidgetDialog(parent)
                
                parent = parent_parent
            else:
                break
        
        return None
    
    def present(self):
        parent = self.parent_dialog()
        
        if parent is not None and parent.get_delegate() is not None:
            parent.get_delegate().on_dialog_disappear(parent)
        
        if self.delegate is not None:
            self.delegate.on_dialog_appear(self)
        
        self.exec()
    
    def close(self):
        parent = self.parent_dialog()
        
        super(Dialog, self).close()
        
        self.handle_close(parent)
    
    def closeEvent(self, a0):
        self.handle_close(self.parent_dialog())
    
    def handle_close(self, parent):
        if self.delegate is not None:
            self.delegate.on_dialog_close(self)
        
        if parent is not None and parent.get_delegate() is not None:
            parent.get_delegate().on_dialog_appear(parent)
        
        self.delegate = None
