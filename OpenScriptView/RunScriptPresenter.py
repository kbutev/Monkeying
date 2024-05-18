import time
from kink import di
from typing import Protocol
from PyQt5.QtCore import QTimer

from Model.ScriptActions import ScriptActions
from Model.ScriptData import ScriptData
from Parser.ScriptActionDescriptionParser import ScriptActionDescriptionParserProtocol
from Presenter.Presenter import Presenter
from Provider.ScriptDataProvider import ScriptDataProviderProtocol, ScriptDataProvider
from Service.EventMonitor import KeyboardEventMonitor
from Service.ScriptStorage import ScriptStorage
from Service.EventSimulatorManager import EventSimulatorManager
from OpenScriptView.RunScriptWidget import RunScriptWidgetProtocol
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from Utilities.Logger import LoggerProtocol


class RunScriptPresenterRouter(Protocol):
    def enable_tabs(self, enabled): pass
    def configure_script(self, parent): pass

class RunScriptPresenter(Presenter):
    
    # Init
    
    def __init__(self, script_data: ScriptData):
        super(RunScriptPresenter, self).__init__()
        
        self.widget = None
        self.router = None
        self.running = False
        self.simulator = None
        self.keyboard_monitor = di[KeyboardEventMonitor]
        self.action_description_parser = di[ScriptActionDescriptionParserProtocol]
        self.settings = di[SettingsManagerProtocol]
        self.play_trigger_key = None
        self.pause_trigger_key = None
        
        # When used, the hotkey is suspended for a short period
        self.hotkey_click_time = 0
        self.hotkey_suspend_interval = 0.5
        
        self.file_format = self.settings.field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT)
        self.script_data = script_data.copy()
        self.script_provider = ScriptDataProvider(script_data.get_file_path())
        
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(False)
        self.update_timer.setInterval(100)
        self.update_timer.timeout.connect(self.update_events)
        
        self.logger = di[LoggerProtocol]
    
    # Property
    
    def get_widget(self) -> RunScriptWidgetProtocol: return self.widget
    def set_widget(self, widget): self.widget = widget
    def get_router(self) -> RunScriptPresenterRouter: return self.router
    def set_router(self, router): self.router = router
    def get_script(self) -> ScriptData: return self.script_data
    def get_script_actions(self) -> ScriptActions: return self.script_data.get_actions()
    def get_script_actions_as_strings(self) -> []: return self.action_description_parser.parse_actions(self.get_script_actions())
    
    # Setup
    
    def start(self):
        assert self.widget is not None
        assert self.router is not None
        
        self.play_trigger_key = self.settings.field_value(SettingsManagerField.PLAY_HOTKEY)
        self.pause_trigger_key = self.settings.field_value(SettingsManagerField.PAUSE_HOTKEY)
        
        self.keyboard_monitor.setup(self.noop_on_key_press, self.on_key_press)
        self.keyboard_monitor.start()
        
        self.widget.update_progress(0, 0)
        
        self.reload_data()
    
    def stop(self):
        if self.keyboard_monitor.is_running():
            self.keyboard_monitor.stop()
        
        if self.simulator is not None and self.simulator.is_running():
            self.simulator.cancel()
        
        self.running = False
        
        self.update_timer.stop()
    
    def reload_data(self, completion=None):
        assert self.widget is not None
        assert self.router is not None
        
        self.script_provider.fetch(lambda script: self.update_data(script, completion),
                                   lambda error: self.handle_error(error, completion))
    
    def update_data(self, script: ScriptData, completion=None):
        self.script_data = script
        self.widget.set_events_data(self.get_script_actions_as_strings())
        
        if completion is not None: completion()
    
    def is_script_active(self) -> bool:
        return self.running
    
    def can_run_script(self) -> bool:
        return not self.running
    
    def run_script(self, sender):
        assert self.widget is not None
        assert not self.running
        
        self.logger.info('RunScriptPresenter run script')
        
        self.running = True
        self.simulator = EventSimulatorManager(self.script_data)
        self.simulator.set_delegate(self)
        self.simulator.start()
        
        self.update_timer.start()
        
        if sender is not self.widget and self.widget is not None:
            self.widget.run_script(sender=self)
    
    def stop_script(self, sender):
        assert self.running
        
        self.logger.info('RunScriptPresenter stop script')
        self.update_events()
        
        self.running = False
        
        self.update_timer.stop()
        
        if sender is not self.simulator:
            self.simulator.cancel()
        
        if sender is not self.widget and self.widget is not None:
            # Always set sender=self, as the widget does not know about the simulator
            self.widget.stop_script(sender=self)
    
    def pause_script(self, sender):
        self.simulator.pause_script(sender)
        
        if sender is not self.widget and self.widget is not None:
            # Always set sender=self, as the widget does not know about the simulator
            self.widget.pause_script(sender=self)
        else:
            assert sender is self.widget
    
    def resume_script(self, sender):
        self.simulator.resume_script(sender)
        
        if sender is not self.widget and self.widget is not None:
            # Always set sender=self, as the widget does not know about the simulator
            self.widget.resume_script(sender=self)
        else:
            assert sender is self.widget
    
    def configure_script(self):
        self.router.configure_script(self.widget)
    
    def update_script_configuration(self, result: ScriptData):
        self.script_data = result.copy()
    
    def enable_tabs(self, value):
        self.router.enable_tabs(value)
    
    def on_key_press(self, event):
        time_since_last_usage = time.time() - self.hotkey_click_time
        
        if time_since_last_usage < self.hotkey_suspend_interval:
            self.logger.verbose_info('RunScriptPresenter hotkey pass')
            return
        
        if event.key == self.play_trigger_key:
            self.logger.verbose_info('RunScriptPresenter play hotkey triggered')
            
            if self.running:
                self.stop_script(sender=self)
            else:
                self.run_script(sender=self)
        elif event.key == self.pause_trigger_key and self.running:
            self.logger.verbose_info('RunScriptPresenter pause hotkey triggered')
            
            if self.simulator.is_paused():
                self.resume_script(sender=self)
            else:
                self.pause_script(sender=self)
        else:
            return
        
        # Update timer only when hotkey is used
        self.hotkey_click_time = time.time()
    
    def noop_on_key_press(self, key):
        pass
    
    def update_events(self):
        index = self.simulator.current_action_index()
        progress = int(self.simulator.progress_fraction() * 100.0)
        self.widget.update_progress(index, progress)
