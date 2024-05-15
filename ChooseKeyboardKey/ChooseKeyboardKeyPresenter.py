from typing import Protocol

from kink import di

from Service.EventMonitor import KeyboardEventMonitor


class ChooseKeyboardKeyPresenterProtocol(Protocol):
    pass


class ChooseKeyboardKeyPresenter(ChooseKeyboardKeyPresenterProtocol):
    
    # - Init
    
    def __init__(self, completion):
        self.keyboard_monitor = di[KeyboardEventMonitor]
        self.completion = completion
        self.captured_event = None
    
    # - Setup
    
    def start(self):
        self.keyboard_monitor.setup(self.noop_on_key_press, self.on_key_press)
        self.keyboard_monitor.start()
    
    # - Actions
    
    def noop_on_key_press(self, key):
        pass
    
    def on_key_press(self, event):
        assert self.completion is not None
        
        self.captured_event = event
        self.keyboard_monitor.stop()
        self.completion(event)
        self.completion = None
