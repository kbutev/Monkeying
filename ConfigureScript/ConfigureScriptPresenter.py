from typing import Protocol
from ConfigureScript.ConfigureScriptWidget import ConfigureScriptWidgetProtocol


class ConfigureScriptPresenterRouter(Protocol):
    def close(self): pass


class ConfigureScriptPresenterProtocol(Protocol):
    def on_name_changed(self, value): pass
    def on_description_changed(self, value): pass
    def on_repeat_count_changed(self, value): pass
    def on_repeat_forever_changed(self, value): pass
    def on_notify_on_start_changed(self, value): pass
    def on_notify_on_end_changed(self, value): pass


class ConfigureScriptPresenter:
    
    # - Init
    
    def __init__(self, storage):
        self.widget = None
        self.router = None
        self.storage = storage
    
    # - Properties
    
    def get_widget(self) -> ConfigureScriptWidgetProtocol: return self.widget
    def set_widget(self, widget): self.widget = widget
    def get_router(self) -> ConfigureScriptPresenterRouter: return self.router
    def set_router(self, router): self.router = router
    
    # - Setup
    
    def start(self):
        assert self.widget is not None
        assert self.router is not None
        self.widget.set_name(self.storage.info.name)
        self.widget.set_description(self.storage.info.description)
        self.widget.set_repeat_count(self.storage.configuration.repeat_count)
        self.widget.set_repeat_forever(self.storage.configuration.repeat_forever)
        self.widget.set_notify_start_check(self.storage.configuration.notify_on_start)
        self.widget.set_notify_end_check(self.storage.configuration.notify_on_end)
    
    # - Actions
    
    def on_name_changed(self, value):
        self.storage.info.name = value
    
    def on_description_changed(self, value):
        self.storage.info.description = value
    
    def on_repeat_count_changed(self, value):
        self.storage.configuration.repeat_count = int(value)
    
    def on_repeat_forever_changed(self, value):
        self.storage.configuration.repeat_forever = bool(value)
    
    def on_notify_on_start_changed(self, value):
        self.storage.configuration.notify_on_start = value
    
    def on_notify_on_end_changed(self, value):
        self.storage.configuration.notify_on_end = value
    
    def on_save(self):
        if self.storage.file_path is not None:
            self.storage.write_to_file(self.storage.file_path)
        
        self.router.close()
