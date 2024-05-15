from typing import Protocol
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QDoubleValidator, QRegularExpressionValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QCheckBox

MIN_SCRIPT_NAME_LENGTH = 3
MAX_SCRIPT_NAME_LENGTH = 20
MAX_SCRIPT_DESC_LENGTH = 100

string_name_validator = QRegularExpressionValidator()
string_desc_validator = QRegularExpressionValidator()

repeat_count_validator = QDoubleValidator()
name_regex = "^.{{{min},{max}}}[^'\"]*$"
name_regex = name_regex.format(min=MIN_SCRIPT_NAME_LENGTH, max=MAX_SCRIPT_NAME_LENGTH)
desc_regex = "^.{{{min},{max}}}[^'\"]*$".format(min=0, max=MAX_SCRIPT_DESC_LENGTH)
string_name_validator.setRegularExpression(QRegularExpression(name_regex))
string_desc_validator.setRegularExpression(QRegularExpression(desc_regex))

repeat_count_validator.setBottom(0)
repeat_count_validator.setTop(99999)
repeat_count_validator.setDecimals(0)


class ConfigureScriptWidgetDelegate(Protocol):
    def on_repeat_count_changed(self, value): pass
    def on_repeat_forever_changed(self, value): pass
    def on_notify_on_start_changed(self, value): pass
    def on_notify_on_end_changed(self, value): pass
    def on_save(self): pass


class ConfigureScriptWidgetProtocol(Protocol):
    def set_name(self, value): pass
    def set_description(self, value): pass
    def set_repeat_count(self, value): pass
    def set_repeat_forever(self, value): pass
    def set_notify_start_check(self, value): pass
    def set_notify_end_check(self, value): pass


class ConfigureScriptWidget(QWidget):
    
    # - Init
    
    def __init__(self, parent=None):
        super(ConfigureScriptWidget, self).__init__(parent)
        self.delegate = None
        
        layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        layout.addLayout(name_layout)
        name_label = QLabel('Name')
        name_layout.addWidget(name_label)
        name_field = QLineEdit()
        name_field.setValidator(repeat_count_validator)
        name_layout.addWidget(name_field)
        name_field.textChanged.connect(self.on_name_changed)
        name_field.setValidator(string_name_validator)
        self.name_field = name_field
        
        description_layout = QHBoxLayout()
        layout.addLayout(description_layout)
        description_label = QLabel('Description')
        description_layout.addWidget(description_label)
        description_field = QLineEdit()
        description_field.setValidator(repeat_count_validator)
        description_layout.addWidget(description_field)
        description_field.textChanged.connect(self.on_description_changed)
        description_field.setValidator(string_desc_validator)
        self.description_field = description_field
        
        repeat_count_layout = QHBoxLayout()
        layout.addLayout(repeat_count_layout)
        repeat_count_label = QLabel('Repeat count')
        repeat_count_layout.addWidget(repeat_count_label)
        repeat_count_field = QLineEdit()
        repeat_count_field.setValidator(repeat_count_validator)
        repeat_count_layout.addWidget(repeat_count_field)
        repeat_count_field.textChanged.connect(self.on_repeat_count_changed)
        self.repeat_count_field = repeat_count_field
        
        repeat_forever_layout = QHBoxLayout()
        layout.addLayout(repeat_forever_layout)
        repeat_forever_label = QLabel('Repeat forever')
        repeat_forever_layout.addWidget(repeat_forever_label)
        repeat_forever_check = QCheckBox()
        repeat_forever_layout.addWidget(repeat_forever_check)
        repeat_forever_check.clicked.connect(self.on_repeat_forever_changed)
        self.repeat_forever_check = repeat_forever_check
        
        notify_start_layout = QHBoxLayout()
        layout.addLayout(notify_start_layout)
        notify_start_label = QLabel('Notify on start')
        notify_start_layout.addWidget(notify_start_label)
        notify_start_check = QCheckBox()
        notify_start_layout.addWidget(notify_start_check)
        notify_start_check.clicked.connect(self.on_notify_on_start_changed)
        self.notify_start_check = notify_start_check
        
        notify_end_layout = QHBoxLayout()
        layout.addLayout(notify_end_layout)
        notify_end_label = QLabel('Notify on end')
        notify_end_layout.addWidget(notify_end_label)
        notify_end_check = QCheckBox()
        notify_end_layout.addWidget(notify_end_check)
        notify_end_check.clicked.connect(self.on_notify_on_end_changed)
        self.notify_end_check = notify_end_check
        
        save_button = QPushButton('Save')
        layout.addWidget(save_button)
        save_button.clicked.connect(self.on_save)
        
        self.setLayout(layout)
    
    # - Properties
    
    def get_delegate(self) -> ConfigureScriptWidgetDelegate: return self.delegate
    def set_delegate(self, delegate): self.delegate = delegate
    
    def set_name(self, value): self.name_field.setText(value)
    def set_description(self, value): self.description_field.setText(value)
    def set_repeat_count(self, value): self.repeat_count_field.setText(str(value))
    def set_repeat_forever(self, value): self.repeat_forever_check.setChecked(value)
    def set_notify_start_check(self, value): self.notify_start_check.setChecked(value)
    def set_notify_end_check(self, value): self.notify_end_check.setChecked(value)
    
    # - Actions
    
    def on_name_changed(self):
        self.delegate.on_name_changed(self.name_field.text())
    
    def on_description_changed(self):
        self.delegate.on_description_changed(self.description_field.text())
    
    def on_repeat_count_changed(self):
        self.delegate.on_repeat_count_changed(int(self.repeat_count_field.text()))
    
    def on_repeat_forever_changed(self):
        self.delegate.on_repeat_forever_changed(self.repeat_forever_check.isChecked())
    
    def on_notify_on_start_changed(self):
        self.delegate.on_notify_on_start_changed(self.notify_start_check.isChecked())
    
    def on_notify_on_end_changed(self):
        self.delegate.on_notify_on_end_changed(self.notify_end_check.isChecked())
    
    def on_save(self):
        self.delegate.on_save()
