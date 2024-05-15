from EditScriptAction.EditScriptActionField import EditScriptActionFieldDelegate


def no_parse(value): return value


class EditScriptActionFieldPresenterProtocol(EditScriptActionFieldDelegate):
    def start(self, field): pass


class EditScriptActionFieldPresenter(EditScriptActionFieldPresenterProtocol):
    
    # - Init
    
    def __init__(self, getter, setter=None):
        super(EditScriptActionFieldPresenter, self).__init__()
        self.getter = getter
        self.setter = setter
        self.value_parser = no_parse
    
    # - Properties
    
    def get_value(self):
        return self.value_parser(self.getter())
    
    def set_value(self, value):
        if self.setter is not None:
            self.setter(self.value_parser(value))
    
    # - Setup
    
    def start(self, field):
        assert self.getter is not None
        field.set_value(self.getter())
