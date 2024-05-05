from typing import Protocol
from Service.EventMonitor import KeyboardEventMonitor

class ChooseKeyboardKeyPresenterProtocol(Protocol):
    pass

class ChooseKeyboardKeyPresenter(ChooseKeyboardKeyPresenterProtocol):
    keyboard_monitor = KeyboardEventMonitor()
    completion = None
    captured_event = None
    
    def __init__(self, completion):
        self.completion = completion
    
    def start(self):
        self.keyboard_monitor.setup(self.noop_on_key_press, self.on_key_press)
        self.keyboard_monitor.start()
    
    def noop_on_key_press(self, key):
        pass
    
    def on_key_press(self, event):
        assert self.completion is not None
        
        self.captured_event = event
        self.keyboard_monitor.stop()
        self.completion(event)
        self.completion = None
