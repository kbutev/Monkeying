from EditScriptAction.EditScriptActionField import EditScriptActionFieldDelegate


class EditScriptActionFieldPresenterProtocol(EditScriptActionFieldDelegate):
    def start(self, field): pass

class EditScriptActionFieldPresenter(EditScriptActionFieldPresenterProtocol):
    getter = None
    setter = None
    value_parser = None
    
    def __init__(self, getter, setter=None):
        super(EditScriptActionFieldPresenter, self).__init__()
        self.getter = getter
        self.setter = setter
        self.value_parser = self.no_parse
    
    def start(self, field):
        assert self.getter is not None
        field.set_value(self.getter())
    
    def get_value(self):
        return self.value_parser(self.getter())
    
    def set_value(self, value):
        if self.setter is not None:
            self.setter(self.value_parser(value))
    
    def no_parse(self, value):
        return value
