from typing import Protocol
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QDoubleValidator, QRegularExpressionValidator
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QComboBox, QPushButton, QCheckBox
from Utilities.Point import Point


class EditScriptActionFieldDelegate(Protocol):
    def get_value(self): pass
    def set_value(self, value): pass


class EditScriptActionField(QWidget):
    
    # - Init
    
    def __init__(self, parent=None):
        super(EditScriptActionField, self).__init__(parent)
        self.delegate: EditScriptActionFieldDelegate = None
        self.name = ''
        self.value = None
    
    # - Properties
    
    def get_delegate(self) -> EditScriptActionFieldDelegate: return self.delegate
    def set_delegate(self, delegate): self.delegate = delegate
    def set_value(self, value): assert False
    def enable_connection(self): assert False
    def disable_connection(self): assert False
    
    # - Actions
    
    def on_value_changed(self): assert False


class EditScriptActionFieldDropDown(EditScriptActionField):
    
    # - Init
    
    def __init__(self, name: str, items, parent=None):
        super(EditScriptActionFieldDropDown, self).__init__(parent)
        self.items = []
        
        self.name = name
        
        layout = QHBoxLayout()
        
        label = QLabel(name)
        layout.addWidget(label)
        
        self.combo_box = QComboBox(parent=self)
        
        self.set_items(items)
        
        layout.addWidget(self.combo_box)
        
        self.setLayout(layout)
    
    # - Properties
    
    def set_value(self, value):
        self.select_value(value)
    
    def set_items(self, items):
        self.items = items
        self.value = items[0]
        
        self.combo_box.clear()
        
        for item in items:
            self.combo_box.addItem(item)
    
    def selected_index(self):
        return self.combo_box.currentIndex()
    
    def select_index(self, index):
        self.combo_box.setCurrentIndex(index)
    
    def select_value(self, value):
        self.combo_box.setCurrentIndex(self.items.index(value))
    
    # Setup
    
    def enable_connection(self):
        self.combo_box.currentIndexChanged.connect(self.on_value_changed)
    
    def disable_connection(self):
        self.combo_box.currentIndexChanged.disconnect()
    
    # Actions
    
    def on_value_changed(self):
        self.value = self.combo_box.itemText(self.selected_index())
        self.delegate.set_value(self.value)


class EditScriptActionFieldBool(EditScriptActionField):
    
    # - Init
    
    def __init__(self, name: str, parent=None):
        super(EditScriptActionFieldBool, self).__init__(parent)
        self.name = name
        
        layout = QHBoxLayout()
        
        label = QLabel(name)
        layout.addWidget(label)
        self.button = QCheckBox()
        layout.addWidget(self.button)
        
        self.setLayout(layout)
    
    # - Properties
    
    def set_value(self, value):
        self.button.setChecked(value)
    
    def enable_connection(self):
        self.button.clicked.connect(self.on_value_changed)
    
    def disable_connection(self):
        self.button.clicked.disconnect()
    
    # Actions
    
    def on_value_changed(self):
        self.value = self.button.isChecked()
        self.delegate.set_value(self.value)


class EditScriptActionFieldString(EditScriptActionField):
    
    # - Init
    
    def __init__(self, name: str, parent=None):
        super(EditScriptActionFieldString, self).__init__(parent)
        
        self.name = name
        
        validator = QRegularExpressionValidator()
        validator.setRegularExpression(QRegularExpression("^[^'\"]*$"))
        
        layout = QHBoxLayout()
        
        label = QLabel(name)
        layout.addWidget(label)
        self.field = QLineEdit()
        self.field.setValidator(validator)
        layout.addWidget(self.field)
        
        self.setLayout(layout)
    
    # - Properties
    
    def set_value(self, value):
        self.set_text(value)
    
    def set_text(self, text):
        self.value = text
        
        self.field.setText(str(text))
    
    def enable_connection(self):
        self.field.textChanged.connect(self.on_value_changed)
    
    def disable_connection(self):
        self.field.textChanged.disconnect()
    
    # Actions
    
    def on_value_changed(self):
        self.value = self.field.text()
        self.delegate.set_value(self.value)


class EditScriptActionFieldFloat(EditScriptActionField):
    
    # - Init
    
    def __init__(self, name: str, min, decimals, max=None, parent=None):
        super(EditScriptActionFieldFloat, self).__init__(parent)
        
        self.name = name
        
        layout = QHBoxLayout()
        
        validator = QDoubleValidator()
        validator.setBottom(min)
        validator.setDecimals(decimals)
        validator.setTop(max) if max is not None else None
        
        label = QLabel(name)
        layout.addWidget(label)
        self.field = QLineEdit()
        self.field.setValidator(validator)
        layout.addWidget(self.field)
        
        self.setLayout(layout)
    
    # - Properties
    
    def set_value(self, value):
        self.set_text(value)
    
    def set_text(self, text):
        self.value = text
        
        self.field.setText(str(text))
    
    def enable_connection(self):
        self.field.textChanged.connect(self.on_value_changed)
    
    def disable_connection(self):
        self.field.textChanged.disconnect()
    
    # Actions
    
    def on_value_changed(self):
        self.value = float(self.field.text())
        self.delegate.set_value(self.value)


class EditScriptActionFieldKeyboardChar(EditScriptActionField):
    
    # - Init
    
    def __init__(self, name: str, parent=None):
        super(EditScriptActionFieldKeyboardChar, self).__init__(parent)
        
        self.on_click = None
        self.name = name
        
        layout = QHBoxLayout()
        
        label = QLabel(name)
        layout.addWidget(label)
        self.button = QPushButton('x')
        layout.addWidget(self.button)
        
        self.setLayout(layout)
    
    # - Properties
    
    def set_value(self, value):
        self.set_text(value)
    
    def set_text(self, text):
        self.value = text
        self.button.setText(text)
        
    def setup_on_click(self, on_click):
        self.on_click = on_click
    
    def enable_connection(self):
        self.button.clicked.connect(self.on_click)
    
    def disable_connection(self):
        self.button.clicked.disconnect()


class EditScriptActionFieldPoint(EditScriptActionField):
    
    # - Init
    
    def __init__(self, name: str, parent=None):
        super(EditScriptActionFieldPoint, self).__init__(parent)
        self.name = name
        
        layout = QHBoxLayout()
        
        validator = QDoubleValidator()
        validator.setBottom(0)
        validator.setDecimals(0)
        
        label = QLabel(name)
        layout.addWidget(label)
        
        self.x_field = QLineEdit()
        self.x_field.resize(280, 40)
        self.x_field.setValidator(validator)
        layout.addWidget(self.x_field)
        
        self.y_field = QLineEdit()
        self.y_field.resize(280, 40)
        self.y_field.setValidator(validator)
        layout.addWidget(self.y_field)
        
        self.setLayout(layout)
    
    # - Properties
    
    def set_value(self, point):
        self.value = point
        
        self.x_field.setText(str(point.x))
        self.y_field.setText(str(point.y))
    
    def enable_connection(self):
        self.x_field.textChanged.connect(self.on_value_changed)
        self.y_field.textChanged.connect(self.on_value_changed)
    
    def disable_connection(self):
        self.x_field.textChanged.disconnect()
        self.y_field.textChanged.disconnect()
    
    # - Actions
    
    def on_value_changed(self):
        self.value = Point(float(self.x_field.text()), float(self.y_field.text()))
        self.delegate.set_value(self.value)
