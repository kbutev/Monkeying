from typing import Protocol
from kink import di, inject
from PyQt5.QtWidgets import QWidget
from EditScriptAction.EditScriptActionField import EditScriptActionFieldFloat, EditScriptActionFieldPoint, \
    EditScriptActionFieldKeyboardChar, EditScriptActionFieldDropDown, EditScriptActionField, \
    EditScriptActionFieldString, EditScriptActionFieldBool
from EditScriptAction.EditScriptActionFieldPresenter import EditScriptActionFieldPresenter
from Model.InputEvent import InputEvent
from Model.KeyboardInputEvent import KeystrokeEvent
from Model.MessageInputEvent import MessageInputEvent
from Model.MouseInputEvent import MouseMoveEvent, MouseClickEvent, MouseScrollEvent
from Model.InputEventType import InputEventType
from pynput.mouse import Button as MouseKey
from Model.ScriptInputEvent import ScriptInputEvent
from Service.SettingsManager import SettingsManagerProtocol, SettingsManagerField
from Utilities import Path as PathUtils
from Utilities.Path import Path


class EditScriptActionFieldBuilderContext:
    
    # - Init
    
    def __init__(self, fields: [], type_field: EditScriptActionField, time_field: EditScriptActionField):
        self.fields = fields
        self.type_field = type_field
        self.time_field = time_field
        self.time_formatter = None
        self.key_formatter = None
        self.point_formatter = None
    
    # - Properties
    
    def get_time_formatter(self): return self.time_formatter
    def set_time_formatter(self, formatter): self.time_formatter = formatter
    def get_key_formatter(self): return self.key_formatter
    def set_key_formatter(self, formatter): self.key_formatter = formatter
    def get_point_formatter(self): return self.point_formatter
    def set_point_formatter(self, formatter): self.point_formatter = formatter
    
    def set_on_type_change_callback(self, callback):
        self.type_field.delegate.setter = callback
    
    def set_on_choose_key_callback(self, callback):
        for field in self.fields:
            if isinstance(field, EditScriptActionFieldKeyboardChar):
                field.setup_on_click(lambda: callback(field))
    
    # - Build
    
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


class EditScriptActionFieldBuilderProtocol(Protocol):
    def start(self, input_event) -> EditScriptActionFieldBuilderContext: return None


@inject(use_factory=True, alias=EditScriptActionFieldBuilderProtocol)
class EditScriptActionFieldBuilder(EditScriptActionFieldBuilderProtocol):
    
    # - Init
    
    def __init__(self):
        self.context_script_path = None
        self.settings = di[SettingsManagerProtocol]
    
    # - Properties
    
    def context_script_path_value(self) -> Path: return self.context_script_path
    def set_context_script_path(self, value): self.context_script_path = value
    
    # - Build
    
    def start(self, input_event) -> EditScriptActionFieldBuilderContext:
        fields = []
        time_field = self.build_time_field(input_event)
        type_field = self.build_event_type_field(input_event)
        fields.append(time_field)
        fields.append(type_field)
        
        if isinstance(input_event, KeystrokeEvent):
            key = EditScriptActionFieldKeyboardChar('Key')
            presenter = EditScriptActionFieldPresenter(input_event.key_as_string, input_event.set_key)
            key.set_delegate(presenter)
            presenter.start(key)
            
            fields.append(key)
        elif isinstance(input_event, MouseClickEvent):
            items = []
            for key in MouseKey: items.append(str(key.name))
            key = EditScriptActionFieldDropDown('Key', items)
            presenter = EditScriptActionFieldPresenter(input_event.key_as_string, input_event.set_key)
            key.set_delegate(presenter)
            presenter.start(key)
            
            loc = EditScriptActionFieldPoint('Location')
            presenter = EditScriptActionFieldPresenter(input_event.get_point, input_event.set_point)
            loc.set_delegate(presenter)
            presenter.start(loc)
            
            fields.append(key)
            fields.append(loc)
        elif isinstance(input_event, MouseMoveEvent):
            loc = EditScriptActionFieldPoint('Location')
            presenter = EditScriptActionFieldPresenter(input_event.get_point, input_event.set_point)
            loc.set_delegate(presenter)
            presenter.start(loc)
            
            fields.append(loc)
        elif isinstance(input_event, MouseScrollEvent):
            loc = EditScriptActionFieldPoint('Location')
            presenter = EditScriptActionFieldPresenter(input_event.get_point, input_event.set_point)
            loc.set_delegate(presenter)
            presenter.start(loc)
            
            dt = EditScriptActionFieldPoint('Scroll dt')
            presenter = EditScriptActionFieldPresenter(input_event.get_scroll_dt, input_event.set_scroll_dt)
            dt.set_delegate(presenter)
            presenter.start(dt)
            
            fields.append(loc)
            fields.append(dt)
        elif isinstance(input_event, MessageInputEvent):
            message = EditScriptActionFieldString('Message')
            presenter = EditScriptActionFieldPresenter(input_event.message, input_event.set_message)
            message.set_delegate(presenter)
            presenter.start(message)
            
            notifications = EditScriptActionFieldBool('Notification')
            presenter = EditScriptActionFieldPresenter(input_event.notifications_enabled, input_event.set_notifications_enabled)
            notifications.set_delegate(presenter)
            presenter.start(notifications)
            
            fields.append(message)
            fields.append(notifications)
        elif isinstance(input_event, ScriptInputEvent):
            assert self.context_script_path is not None
            
            base_dir = self.settings.field_value(SettingsManagerField.SCRIPTS_PATH)
            file_format = self.settings.field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT)
            items = PathUtils.directory_file_list(base_dir, file_format)
            context_script_file = self.context_script_path().last_component()
            
            # Do not include the context script to avoid recursion
            items.remove(context_script_file)
            
            if input_event.path.is_empty():
                input_event.set_absolute_path(PathUtils.combine_paths(base_dir, items[0]))
            
            paths = EditScriptActionFieldDropDown('Script', items)
            presenter = EditScriptActionFieldPresenter(input_event.file_name, input_event.set_file_name)
            paths.set_delegate(presenter)
            presenter.start(paths)
            
            fields.append(paths)
        else:
            assert False # Event not implemented
        
        return EditScriptActionFieldBuilderContext(fields, type_field, time_field)
    
    # - Helpers
    
    def build_event_type_field(self, input_event: InputEvent) -> QWidget:
        type_values = self.all_event_kinds()
        field = EditScriptActionFieldDropDown('Type', type_values)
        field.select_index(type_values.index(str(input_event.event_type())))
        presenter = EditScriptActionFieldPresenter(input_event.event_type)
        field.set_delegate(presenter)
        presenter.start(field)
        return field
    
    def build_time_field(self, input_event: InputEvent) -> QWidget:
        field = EditScriptActionFieldFloat(name='Time', min=0, decimals=3)
        presenter = EditScriptActionFieldPresenter(input_event.time, input_event.set_time)
        field.set_delegate(presenter)
        presenter.start(field)
        return field
    
    def all_event_kinds(self):
        result = []
        
        # Keyboard/mouse
        for type in InputEventType:
            result.append(str(type))
        
        # Other
        
        return result
