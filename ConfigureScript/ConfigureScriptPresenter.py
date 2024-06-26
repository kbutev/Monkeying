from typing import Protocol
from ConfigureScript.ConfigureScriptWidget import ConfigureScriptWidgetProtocol
from Model.ScriptData import ScriptData


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
    
    def __init__(self, script_data: ScriptData):
        self.widget = None
        self.router = None
        self.script_data = script_data.copy()
    
    # - Properties
    
    def get_widget(self) -> ConfigureScriptWidgetProtocol: return self.widget
    def set_widget(self, widget): self.widget = widget
    def get_router(self) -> ConfigureScriptPresenterRouter: return self.router
    def set_router(self, router): self.router = router
    def get_script(self) -> ScriptData: return self.script_data.copy()
    
    # - Setup
    
    def start(self):
        assert self.widget is not None
        assert self.router is not None
        
        info = self.script_data.get_info()
        config = self.script_data.get_config()
        
        self.widget.set_name(info.name)
        self.widget.set_description(info.description)
        self.widget.set_repeat_count(config.repeat_count)
        self.widget.set_repeat_forever(config.repeat_forever)
        self.widget.set_notify_start_check(config.notify_on_start)
        self.widget.set_notify_end_check(config.notify_on_end)
    
    # - Actions
    
    def on_name_changed(self, value):
        self.script_data.get_info().name = value
    
    def on_description_changed(self, value):
        self.script_data.get_info().description = value
    
    def on_repeat_count_changed(self, value):
        self.script_data.get_config().repeat_count = int(value)
    
    def on_repeat_forever_changed(self, value):
        self.script_data.get_config().repeat_forever = bool(value)
    
    def on_notify_on_start_changed(self, value):
        self.script_data.get_config().notify_on_start = value
    
    def on_notify_on_end_changed(self, value):
        self.script_data.get_config().notify_on_end = value
    
    def on_save(self):
        self.router.close()
