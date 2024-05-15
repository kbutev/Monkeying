from kink import inject, di

from MainView.RecordScriptTable import RecordScriptTableDataSource, RecordScriptTable


@inject(use_factory=True)
class RunScriptTableDataSource(RecordScriptTableDataSource):
    pass


class RunScriptTable(RecordScriptTable):
    def __init__(self, parent=None):
        super(RunScriptTable, self).__init__(parent)
        self.data_source = di[RunScriptTableDataSource]

