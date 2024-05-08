from typing import Protocol
from PyQt5.QtWidgets import QWidget
from EditScriptAction.EditScriptActionField import EditScriptActionFieldFloat, EditScriptActionFieldPoint, \
    EditScriptActionFieldKeyboardChar, EditScriptActionFieldDropDown, EditScriptActionField
from EditScriptAction.EditScriptActionFieldPresenter import EditScriptActionFieldPresenter
from Model.InputEvent import InputEvent
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.MouseInputEvent import MouseMoveEvent, MouseClickEvent, MouseScrollEvent
from Model.InputEventType import InputEventType
from pynput.mouse import Button as MouseKey
from Model.ScriptInputEvent import ScriptInputEvent
from Utilities import Path

DEFAULT_BASE_DIR = 'scripts'
SCRIPT_FILE_FORMAT = 'json'

class EditScriptActionFieldBuilderContext:
    fields = []
    type_field: EditScriptActionField
    time_field: EditScriptActionField
    
    time_formatter = None
    key_formatter = None
    point_formatter = None
    
    def __init__(self, fields, type_field, time_field):
        self.fields = fields
        self.type_field = type_field
        self.time_field = time_field
    
    def build(self) -> []:
        if self.time_formatter is not None:
            self.time_formatter.delegate.value_parser = self.time_formatter
        
        for field in self.fields:
            field.enable_connection()
            
            if isinstance(field, EditScriptActionFieldKeyboardChar) and self.key_formatter is not None:
                field.delegate.value_parser = self.key_formatter
            elif isinstance(field, EditScriptActionFieldPoint) and self.key_formatter is not None:
                field.delegate.value_parser = self.point_formatter
        
        return self.fields
    
    def setup_on_type_change_callback(self, callback):
        self.type_field.delegate.setter = callback
    
    def setup_on_choose_key_callback(self, callback):
        for field in self.fields:
            if isinstance(field, EditScriptActionFieldKeyboardChar):
                field.setup_on_click(lambda: callback(field))

class EditScriptActionFieldBuilderProtocol(Protocol):
    def start(self, input_event) -> EditScriptActionFieldBuilderContext: assert False

class EditScriptActionFieldBuilder(EditScriptActionFieldBuilderProtocol):
    context_script_path: Path = None
    
    def start(self, input_event) -> EditScriptActionFieldBuilderContext:
        fields = []
        time_field = self.build_time_field(input_event)
        type_field = self.build_event_type_field(input_event)
        fields.append(time_field)
        fields.append(type_field)
        
        if isinstance(input_event, KeystrokeEvent):
            key = EditScriptActionFieldKeyboardChar('Key')
            presenter = EditScriptActionFieldPresenter(input_event.key_as_string, input_event.set_key)
            key.delegate = presenter
            presenter.start(key)
            
            fields.append(key)
        elif isinstance(input_event, MouseClickEvent):
            items = []
            for key in MouseKey: items.append(str(key.name))
            key = EditScriptActionFieldDropDown('Key', items)
            presenter = EditScriptActionFieldPresenter(input_event.key_as_string, input_event.set_key)
            key.delegate = presenter
            presenter.start(key)
            
            loc = EditScriptActionFieldPoint('Location')
            presenter = EditScriptActionFieldPresenter(input_event.get_point, input_event.set_point)
            loc.delegate = presenter
            presenter.start(loc)
            
            fields.append(key)
            fields.append(loc)
        elif isinstance(input_event, MouseMoveEvent):
            loc = EditScriptActionFieldPoint('Location')
            presenter = EditScriptActionFieldPresenter(input_event.get_point, input_event.set_point)
            loc.delegate = presenter
            presenter.start(loc)
            
            fields.append(loc)
        elif isinstance(input_event, MouseScrollEvent):
            loc = EditScriptActionFieldPoint('Location')
            presenter = EditScriptActionFieldPresenter(input_event.get_point, input_event.set_point)
            loc.delegate = presenter
            presenter.start(loc)
            
            dt = EditScriptActionFieldPoint('Scroll dt')
            presenter = EditScriptActionFieldPresenter(input_event.get_scroll_dt, input_event.set_scroll_dt)
            dt.delegate = presenter
            presenter.start(dt)
            
            fields.append(loc)
            fields.append(dt)
        elif isinstance(input_event, ScriptInputEvent):
            assert self.context_script_path is not None
            
            base_dir = DEFAULT_BASE_DIR
            items = Path.directory_file_list(base_dir, SCRIPT_FILE_FORMAT)
            context_script_file = self.context_script_path.last_component()
            
            # Do not include the context script to avoid recursion
            items.remove(context_script_file)
            
            if input_event.path.is_empty():
                input_event.set_absolute_path(Path.combine_paths(base_dir, items[0]))
            
            paths = EditScriptActionFieldDropDown('Script', items)
            presenter = EditScriptActionFieldPresenter(input_event.file_name, input_event.set_file_name)
            paths.delegate = presenter
            presenter.start(paths)
            
            fields.append(paths)
        else:
            assert False
        
        return EditScriptActionFieldBuilderContext(fields, type_field, time_field)
    
    def build_event_type_field(self, input_event: InputEvent) -> QWidget:
        type_values = self.all_event_kinds()
        field = EditScriptActionFieldDropDown('Type', type_values)
        field.select_index(type_values.index(str(input_event.event_type())))
        presenter = EditScriptActionFieldPresenter(input_event.event_type)
        field.delegate = presenter
        presenter.start(field)
        return field
    
    def build_time_field(self, input_event: InputEvent) -> QWidget:
        field = EditScriptActionFieldFloat(name='Time', min=0, decimals=3)
        presenter = EditScriptActionFieldPresenter(input_event.time, input_event.set_time)
        field.delegate = presenter
        presenter.start(field)
        return field
    
    def all_event_kinds(self):
        result = []
        
        # Keyboard/mouse
        for type in InputEventType:
            result.append(str(type))
        
        # Other
        
        return result
