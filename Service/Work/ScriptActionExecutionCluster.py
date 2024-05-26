import os
from datetime import datetime
import time
from kink import di
from Model.ScriptAction import ScriptAction
from Model.ScriptActions import ScriptActions
from Model.ScriptCommandAction import ScriptCommandAction
from Model.ScriptInputEventAction import ScriptInputEventAction
from Model.ScriptMessageAction import ScriptMessageAction
from Model.ScriptSnapshotAction import ScriptSnapshotAction
from Service.EventSimulator import MouseEventSimulator, KeyboardEventSimulator, MouseEventSimulatorProtocol, \
    KeyboardEventSimulatorProtocol
from Service.OSNotificationCenter import OSNotificationCenterProtocol
from Service.SettingsManager import SettingsManagerProtocol, SettingsManagerField
from Service.Work.ScriptActionExecution import ScriptActionExecution
from Utilities import Path
from Utilities.Logger import LoggerProtocol
from Utilities.Timer import Timer
from mss import mss


def current_short_date():
    return datetime.today().strftime('%Y.%m.%d')


def current_short_time():
    return datetime.today().strftime('%H-%M-%S')


class ScriptNOOPExecution(ScriptActionExecution):
    
    # - Init
    
    def __init__(self):
        pass
    
    # - Properties
    
    def is_running(self) -> bool:
        return False
    
    # - Actions
    
    def execute(self, parent=None):
        pass
    
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def update(self):
        return self.is_running()


class ScriptActionKeyExecution(ScriptActionExecution):
    
    # - Init
    
    def __init__(self, action: ScriptAction):
        assert isinstance(action, ScriptInputEventAction)
        self.action = action
        self.mouse_simulator = di[MouseEventSimulatorProtocol]
        self.keyboard_simulator = di[KeyboardEventSimulatorProtocol]
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def is_running(self) -> bool:
        return False
    
    # - Actions
    
    def execute(self, parent=None):
        event = self.action.get_event()
        
        if self.action.action_type().is_keyboard():
            self.keyboard_simulator.simulate(event)
        else:
            self.mouse_simulator.simulate(event)
    
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def update(self):
        return self.is_running()


class ScriptActionMessageExecution(ScriptActionExecution):
    
    # - Init
    
    def __init__(self, action: ScriptAction):
        assert isinstance(action, ScriptMessageAction)
        self.action = action
        self.notification_center = di[OSNotificationCenterProtocol]
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def is_running(self) -> bool:
        return False
    
    # - Actions
    
    def execute(self, parent=None):
        message = self.action.message()
        
        self.logger.info(f'{message}')
        
        if self.action.notifications_enabled():
            self.notification_center.show("Monkeying", message)
    
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def update(self):
        return self.is_running()


class ScriptActionScriptExecution(ScriptActionExecution):
    
    # - Init
    
    def __init__(self, script_path: Path, actions: ScriptActions, builder): # builder: ScriptActionExecutionBuilderProtocol
        assert actions.count() > 0
        self.parent = None
        self.current_execution = None
        self.script_path = script_path
        self.actions = actions.copy()
        self.start_time = 0
        self.timer = Timer()
        self.duration_time = actions.duration()
        self.builder = builder
        self.original_action_count = actions.count()
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def get_parent(self) -> ScriptActionExecution:
        return self.parent
    
    def set_parent(self, parent):
        self.parent = parent
    
    def get_current_execution(self) -> ScriptActionExecution:
        return self.current_execution
    
    def set_current_execution(self, current_execution):
        self.current_execution = current_execution
    
    def is_running(self) -> bool:
        return self.actions.count() > 0
    
    def elapsed_time(self) -> float:
        return self.timer.elapsed_time()
    
    def time_elapsed_since_start(self) -> float:
        return time.time() - self.start_time
    
    def duration(self) -> float:
        return self.duration_time
    
    def current_action_index(self) -> int:
        return self.original_action_count - self.actions.count()
    
    # - Actions
    
    def execute(self, parent=None):
        # Note that the script configuration is ignored
        # The script configuration is applied only for the root script
        current_script = parent
        
        while current_script is not None and isinstance(current_script, ScriptActionScriptExecution):
            assert current_script.script_path != self.script_path  # One script cannot call another
            current_script = current_script.parent
        
        self.parent = parent
        self.timer.start()
    
    def pause(self):
        assert self.is_running()
        
        if not self.timer.is_paused():
            self.timer.pause()
        
        if self.current_execution is not None:
            self.current_execution.pause()
    
    def resume(self):
        assert self.is_running()
        
        if self.timer.is_paused():
            self.timer.resume()
        
        if self.current_execution is not None:
            self.current_execution.resume()
    
    def update(self):
        if self.actions.count() == 0:
            return False
        
        # Update current action
        if self.current_execution is not None:
            if self.current_execution.update():
                return True
            else:
                self.go_to_next_action()
        
        # Update next action
        while self.execute_next_action():
            pass
        
        return True
    
    # - Helpers
    
    def execute_next_action(self) -> bool:
        if self.actions.count() == 0:
            return False
        
        next_action = self.actions.data[0]
        
        # If it's time, execute the action
        if next_action.time() <= self.elapsed_time():
            self.current_execution = self.builder.build(next_action)
            self.current_execution.execute(parent=self)
            
            if self.current_execution.update():
                self.timer.pause()  # The timer has to be paused while the async action is running
                return False
            else:
                self.go_to_next_action()
                return True
        else:
            self.current_execution = None
            return False
    
    def go_to_next_action(self):
        assert self.actions.count() > 0
        self.actions.data.pop(0)
        self.current_execution = None
        
        if self.actions.count() == 0:
            self.timer.stop()
        elif self.timer.is_paused():
            self.timer.resume()


class ScriptSnapshotExecution(ScriptActionExecution):
    
    FORMAT = '.png'
    FOLDER = 'snapshots'
    DATE_SPECIFIER = '{YY.MM.dd}'
    TIME_SPECIFIER = '{HH-MM-ss}'
    
    # - Init
    
    def __init__(self, action: ScriptAction):
        assert isinstance(action, ScriptSnapshotAction)
        self.action = action
        
        self.file_name = action.file_name()
        
        self.logger = di[LoggerProtocol]

        settings = di[SettingsManagerProtocol]
        self.base_path = settings.field_value(SettingsManagerField.SCRIPTS_PATH)
    
    # - Properties
    
    def is_running(self) -> bool:
        return False
    
    def formatted_path(self) -> Path:
        name = self.file_name
        
        if ScriptSnapshotExecution.DATE_SPECIFIER in name:
            date = current_short_date()
            name = name.replace(ScriptSnapshotExecution.DATE_SPECIFIER, date)
        
        if ScriptSnapshotExecution.TIME_SPECIFIER in name:
            date = current_short_time()
            name = name.replace(ScriptSnapshotExecution.TIME_SPECIFIER, date)
        
        if not name.endswith(ScriptSnapshotExecution.FORMAT):
            name = f'{name}{ScriptSnapshotExecution.FORMAT}'
        
        path = self.base_path.copy()
        
        path.append_to_end(name)
        
        return path
    
    # - Actions
    
    def execute(self, parent=None):
        with mss() as sct:
            path = self.formatted_path()
            self.logger.info(f"taking snapshot and saving it to '{path.absolute}'")
            try:
                sct.shot(output=path.absolute)
            except Exception as error:
                self.logger.error(f"snapshot failed, error: {error}")
    
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def update(self):
        return self.is_running()


class ScriptCommandExecution(ScriptActionExecution):
    
    # - Init
    
    def __init__(self, action: ScriptAction):
        assert isinstance(action, ScriptCommandAction)
        self.action = action
        self.directory = action.directory().absolute
        self.command = action.command()
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def is_running(self) -> bool:
        return False
    
    # - Actions
    
    def execute(self, parent=None):
        self.logger.info(f"run command '{self.command}' @ {self.directory}")
        os.chdir(self.directory)
        os.system(self.command) # TODO: run this in update? So it doesnt block the caller
    
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def update(self):
        return self.is_running()

