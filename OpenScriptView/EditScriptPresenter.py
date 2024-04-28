from typing import Protocol

from OpenScriptView.EditScriptWidget import EditScriptWidgetProtocol
from Parser.EventActionParser import EventActionToStringParserProtocol, EventActionToStringParser
from Presenter.Presenter import Presenter
from Service.EventStorage import EventStorage
from Utilities import Path


class EditScriptPresenterRouter(Protocol):
    def enable_tabs(self, enabled): pass
    def edit_script_action(self, parent, index): pass

class EditScriptPresenter(Presenter):
    widget: EditScriptWidgetProtocol = None
    router: EditScriptPresenterRouter = None
    
    working_dir = 'scripts'
    file_format = 'json'
    
    storage_data = []
    script: str
    
    event_parser: EventActionToStringParserProtocol = EventActionToStringParser()
    
    def __init__(self, script):
        super(EditScriptPresenter, self).__init__()
        
        storage = EventStorage()
        storage.read_from_file(Path.combine(self.working_dir, script))
        self.storage_data = storage.data
        self.script = script
    
    def start(self):
        self.update_events()
    
    def stop(self):
        pass
    
    def update_events(self):
        events = list(map(lambda event: self.event_parser.parse(event), self.storage_data))
        self.widget.set_events_data(events)
    
    def edit_script_action(self, index):
        self.router.edit_script_action(self.widget, index)
