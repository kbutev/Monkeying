import time
from kink import di
from Model import InputEvent
from Model.MessageInputEvent import MessageInputEvent
from Model.ScriptEvents import ScriptEvents
from Service.EventSimulator import MouseEventSimulator, KeyboardEventSimulator
from Service.OSNotificationCenter import OSNotificationCenterProtocol
from Service.Work.EventExecution import EventExecution
from Utilities import Path
from Utilities.Logger import LoggerProtocol
from Utilities.Timer import Timer


class EventKeyExecution(EventExecution):
    
    # - Init
    
    def __init__(self, event: InputEvent):
        self.event = event
        self.mouse_simulator = MouseEventSimulator()
        self.keyboard_simulator = KeyboardEventSimulator()
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def is_running(self) -> bool:
        return False
    
    # - Actions
    
    def execute(self, parent=None):
        event = self.event
        
        # self.logger.debug(f'simulate {event.event_type().name} : {event.value_as_string()}')
        
        if event.event_type().is_keyboard():
            self.keyboard_simulator.simulate(event)
        else:
            self.mouse_simulator.simulate(event)
    
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def update(self):
        return self.is_running()


class EventMessageExecution(EventExecution):
    
    # - Init
    
    def __init__(self, event: MessageInputEvent):
        self.event = event
        self.notification_center = di[OSNotificationCenterProtocol]
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def is_running(self) -> bool:
        return False
    
    # - Actions
    
    def execute(self, parent=None):
        event = self.event
        
        message = event.message()
        
        self.logger.info(f'{message}')
        
        if event.notifications_enabled():
            self.notification_center.show("Monkeying", message)
    
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def update(self):
        return self.is_running()


class ScriptExecution(EventExecution):
    
    # - Init
    
    def __init__(self, script_path: Path, events: ScriptEvents, builder): # builder: EventExecutionBuilderProtocol
        assert events.count() > 0
        self.parent = None
        self.current_execution = None
        self.script_path = script_path
        self.events = events.copy()
        self.start_time = 0
        self.timer = Timer()
        self.duration_time = events.duration()
        self.builder = builder
        self.original_event_count = events.count()
        self.logger = di[LoggerProtocol]
    
    # - Properties
    
    def get_parent(self) -> EventExecution:
        return self.parent
    
    def set_parent(self, parent):
        self.parent = parent
    
    def get_current_execution(self) -> EventExecution:
        return self.current_execution
    
    def set_current_execution(self, current_execution):
        self.current_execution = current_execution
    
    def is_running(self) -> bool:
        return self.events.count() > 0
    
    def elapsed_time(self) -> float:
        return self.timer.elapsed_time()
    
    def time_elapsed_since_start(self) -> float:
        return time.time() - self.start_time
    
    def duration(self) -> float:
        return self.duration_time
    
    def current_event_index(self) -> int:
        return self.original_event_count - self.events.count()
    
    # - Actions
    
    def execute(self, parent=None):
        # Note that the script configuration is ignored
        # The script configuration is applied only for the root script
        current_script = parent
        
        while current_script is not None and isinstance(current_script, ScriptExecution):
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
        if self.events.count() == 0:
            return False
        
        # Update current event
        if self.current_execution is not None:
            if self.current_execution.update():
                return True
            else:
                self.go_to_next_event()
        
        # Update next event
        while self.execute_next_event():
            pass
        
        return True
    
    # - Helpers
    
    def execute_next_event(self) -> bool:
        if self.events.count() == 0:
            return False
        
        next_event = self.events.data[0]
        
        # If it's time, execute event
        if next_event.time() <= self.elapsed_time():
            self.current_execution = self.builder.build(next_event)
            self.current_execution.execute(parent=self)
            
            if self.current_execution.update():
                self.timer.pause()  # The timer has to be paused while the async event is running
                return False
            else:
                self.go_to_next_event()
                return True
        else:
            self.current_execution = None
            return False
    
    def go_to_next_event(self):
        assert self.events.count() > 0
        self.events.data.pop(0)
        self.current_execution = None
        
        if self.events.count() == 0:
            self.timer.stop()
        elif self.timer.is_paused():
            self.timer.resume()
