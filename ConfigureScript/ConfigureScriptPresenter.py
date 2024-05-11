from typing import Protocol

from ConfigureScript.ConfigureScriptWidget import ConfigureScriptWidgetProtocol
from Service.ScriptStorage import ScriptStorage

class ConfigureScriptPresenterRouter(Protocol):
    def close(self): pass

class ConfigureScriptPresenterProtocol(Protocol):
    def on_repeat_count_changed(self, value): pass
    def on_repeat_forever_changed(self, value): pass
    def on_notify_on_start_changed(self, value): pass
    def on_notify_on_end_changed(self, value): pass

class ConfigureScriptPresenter:
    widget: ConfigureScriptWidgetProtocol
    router: ConfigureScriptPresenterRouter = None
    storage: ScriptStorage
    
    def __init__(self, storage):
        self.storage = storage
    
    def start(self):
        assert self.widget is not None
        assert self.router is not None
        self.widget.set_repeat_count(self.storage.configuration.repeat_count)
        self.widget.set_repeat_forever(self.storage.configuration.repeat_forever)
        self.widget.set_notify_start_check(self.storage.configuration.notify_on_start)
        self.widget.set_notify_end_check(self.storage.configuration.notify_on_end)
    
    def on_repeat_count_changed(self, value):
        self.storage.configuration.repeat_count = int(value)
    
    def on_repeat_forever_changed(self, value):
        self.storage.configuration.repeat_forever = bool(value)
    
    def on_notify_on_start_changed(self, value):
        self.storage.configuration.notify_on_start = value
    
    def on_notify_on_end_changed(self, value):
        self.storage.configuration.notify_on_end = value
    
    def on_save(self):
        self.storage.write_to_file(self.storage.file_path)
        self.router.close()
