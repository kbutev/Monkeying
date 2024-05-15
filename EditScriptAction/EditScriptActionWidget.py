from PyQt5 import sip
from PyQt5.QtWidgets import *
from typing import Protocol
from EditScriptAction.EditScriptActionField import EditScriptActionField


class EditScriptActionWidgetProtocol(Protocol):
    def reset(self): pass
    def setup_dynamic_fields(self, fields): pass
    def fill_values(self): pass
    def save_changes(self): pass
    def cancel_changes(self): pass


class EditWidgetDelegate(Protocol):
    def build_dynamic_fields(self) -> [QWidget]: pass
    def prompt_choose_key_dialog(self): pass
    def save(self): pass
    def close(self): pass


class EditScriptActionWidget(QWidget):
    
    # - Init
    
    def __init__(self, parent=None):
        super(EditScriptActionWidget, self).__init__(parent)
        self.delegate = None
        self.dynamic_fields_initiated = False
        self._setup()
    
    # - Properties
    
    def get_delegate(self) -> EditWidgetDelegate: return self.delegate
    def set_delegate(self, delegate): self.delegate = delegate
    
    # - Setup
    
    def _setup(self):
        layout = QVBoxLayout(self)
        self.layout = layout
        
        self.layout_dynamic_fields_start_index = 0
        
        self.save_button = QPushButton('Save')
        layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_changes)
        
        self.cancel_button = QPushButton('Cancel')
        layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.cancel_changes)
        
        self.enable_connections()
        self.setLayout(layout)
    
    def reset(self):
        self.dynamic_fields_initiated = False
        self.disable_connections()
        self.delete_current_layout()
        self._setup()
    
    # - Actions
    
    def enable_connections(self):
        self.enumerate_dynamic_fields(lambda field: field.enable_connection())
    
    def disable_connections(self):
        self.enumerate_dynamic_fields(lambda field: field.disable_connection())
    
    def enumerate_dynamic_fields(self, callback):
        for child in enumerate(self.children()):
            if isinstance(child, EditScriptActionField):
                callback(child)
    
    def fill_values(self):
        if not self.dynamic_fields_initiated:
            self.dynamic_fields_initiated = True
            
            fields = self.delegate.build_dynamic_fields()
            
            for field in fields:
                self.layout.insertWidget(self.layout_dynamic_fields_start_index, field)
    
    def save_changes(self):
        self.delegate.save()
    
    def cancel_changes(self):
        self.delegate.close()
    
    def delete_current_layout(self):
        if self.layout is not None:
            while self.layout.count():
                item = self.layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.deleteLayout(item.layout())
            sip.delete(self.layout)
