from typing import Protocol
from Model.InputEvent import InputEvent


class EventExecutionBuilderProtocol(Protocol):
    def build(self, event: InputEvent, print_callback=None): pass
