from typing import Protocol
from Model.InputEvent import InputEvent
from Service.EventSimulator import MouseEventSimulator, KeyboardEventSimulator


class EventExecution(Protocol):
    def is_running(self) -> bool: return False
    
    def execute(self): pass
    
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
    
    def execute(self):
        self.mouse_simulator.print_callback = self.print_callback
        self.keyboard_simulator.print_callback = self.print_callback
        
        event = self.event
        
        self.print(f'simulate {event.event_type().name} : {event.value_as_string()}')
        
        if event.event_type().is_keyboard():
            self.keyboard_simulator.simulate(event)
        else:
            self.mouse_simulator.simulate(event)
    
    def update(self):
        return self.is_running()
    
    def print(self, message):
        if self.print_callback is not None:
            self.print_callback(message)
