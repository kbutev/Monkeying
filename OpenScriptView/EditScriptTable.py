from kink import inject, di

from MainView.RecordScriptTable import RecordScriptTableDataSource, RecordScriptTable


@inject(use_factory=True)
class EditScriptTableDataSource(RecordScriptTableDataSource):
    pass


class EditScriptTable(RecordScriptTable):
    def __init__(self, parent=None):
        super(EditScriptTable, self).__init__(parent)
        self.data_source = di[EditScriptTableDataSource]

