import os
import time
from typing import Protocol
from Model.InputEvent import InputEvent
from Model.MessageInputEvent import MessageInputEvent
from Service.EventSimulator import MouseEventSimulator, KeyboardEventSimulator
from Service.OSNotification import OSNotification
from Service.Work.EventExecutionBuilderProtocol import EventExecutionBuilderProtocol
from Utilities.Path import Path
from Utilities.Timer import Timer


class EventExecution(Protocol):
    def is_running(self) -> bool: return False
    
    def execute(self, parent=None): pass
    
    def pause(self): pass
    def resume(self): pass
    
    # Returns the result of is_running().
    def update(self) -> bool: pass

class EventKeyExecution(EventExecution):
    event: InputEvent
    
    mouse_simulator = MouseEventSimulator()
    keyboard_simulator = KeyboardEventSimulator()
    
    print_callback = None
    
    def __init__(self, event: InputEvent, print_callback = None):
        self.event = event
        self.print_callback = print_callback
        self.mouse_simulator.print_callback = self.print_callback
        self.keyboard_simulator.print_callback = self.print_callback
    
    def is_running(self) -> bool:
        return False
    
    def execute(self, parent=None):
        self.mouse_simulator.print_callback = self.print_callback
        self.keyboard_simulator.print_callback = self.print_callback
        
        event = self.event
        
        self.print(f'simulate {event.event_type().name} : {event.value_as_string()}')
        
        if event.event_type().is_keyboard():
            self.keyboard_simulator.simulate(event)
        else:
            self.mouse_simulator.simulate(event)
    
    def pause(self): pass
    def resume(self): pass
    
    def update(self):
        return self.is_running()
    
    def print(self, message):
        if self.print_callback is not None:
            self.print_callback(message)


class EventMessageExecution(EventExecution):
    event: MessageInputEvent
    
    print_callback = None
    
    def __init__(self, event: MessageInputEvent, print_callback=None):
        self.event = event
        self.print_callback = print_callback
    
    def is_running(self) -> bool:
        return False
    
    def execute(self, parent=None):
        event = self.event
        
        message = event.message()
        
        self.print(f'{message}')
        
        if event.notifications_enabled():
            notification = OSNotification("Monkeying", message)
            notification.show()
    
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def update(self):
        return self.is_running()
    
    def print(self, message):
        if self.print_callback is not None:
            self.print_callback(message)

class ScriptExecution(EventExecution):
    script_path: Path
    events = []
    original_event_count = 0
    start_time = 0
    timer: Timer
    duration_time = 0
    
    parent: EventExecution = None
    current_execution: EventExecution = None
    
    builder: EventExecutionBuilderProtocol
    
    print_callback = None
    
    def __init__(self, script_path: Path, events, builder, print_callback = None):
        assert len(events) > 0
        self.script_path = script_path
        self.events = events
        self.timer = Timer()
        self.duration_time = events[len(events)-1].time() if len(events) > 0 else 0
        self.builder = builder
        self.original_event_count = len(events)
        self.print_callback = print_callback
    
    def is_running(self) -> bool:
        return len(self.events) > 0
    
    def elapsed_time(self) -> float:
        return self.timer.elapsed_time()
    
    def time_elapsed_since_start(self) -> float:
        return time.time() - self.start_time
    
    def duration(self) -> float:
        return self.duration_time
    
    def current_event_index(self) -> int:
        return self.original_event_count - len(self.events)
    
    def execute(self, parent=None):
        current_script = parent
        
        while current_script is not None and isinstance(current_script, ScriptExecution):
            assert current_script.script_path != self.script_path # One script cannot call another
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
        if len(self.events) == 0:
            return False
        
        # Update current event
        if self.current_execution is not None:
            if self.current_execution.update():
                return True
            else:
                self.go_to_next_event()
        
        # Update next event
        while len(self.events) > 0 and self.current_execution is None:
            self.execute_next_event()
        
        return True
    
    def execute_next_event(self):
        next_event = self.events[0]
        
        # If it's time, execute event
        if next_event.time() <= self.elapsed_time():
            self.current_execution = self.builder.build(next_event, self.print_callback)
            self.current_execution.execute(parent=self)
            
            if self.current_execution.update():
                self.timer.pause()  # The timer has to be paused while the async event is running
            else:
                self.go_to_next_event()
        else:
            self.current_execution = None
    
    def go_to_next_event(self):
        assert len(self.events) > 0
        self.events.pop(0)
        self.current_execution = None
        
        if len(self.events) == 0:
            self.timer.stop()
        elif self.timer.is_paused():
            self.timer.resume()
    
    def print(self, message):
        if self.print_callback is not None:
            self.print_callback(message)
