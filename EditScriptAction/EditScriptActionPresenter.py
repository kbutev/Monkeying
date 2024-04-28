from typing import Protocol

from EditScriptAction.EditScriptActionWidget import EditScriptActionWidgetProtocol
from Presenter.Presenter import Presenter


class EditScriptActionPresenterRouter(Protocol):
    pass

class EditScriptActionPresenter(Presenter):
    router: EditScriptActionPresenterRouter = None
    widget: EditScriptActionWidgetProtocol = None
    
    def __init__(self):
        super(EditScriptActionPresenter, self).__init__()
    
    def start(self):
        pass
    
    def stop(self):
        pass
