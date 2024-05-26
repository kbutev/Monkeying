from typing import Protocol, Any
from kink import di, inject
from Model.ScriptAction import ScriptAction
from Model.ScriptInputEventAction import ScriptInputEventAction
from Model.ScriptMessageAction import ScriptMessageAction
from Model.ScriptRunAction import ScriptRunAction, NOOPScriptRunAction
from Model.ScriptSnapshotAction import ScriptSnapshotAction
from Service.ScriptStorage import ScriptStorage
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from Service.Work.ScriptActionExecutionCluster import ScriptActionMessageExecution, ScriptActionScriptExecution, \
    ScriptActionKeyExecution, ScriptSnapshotExecution, ScriptNOOPExecution


class ScriptActionExecutionBuilderProtocol(Protocol):
    def build(self, action: ScriptAction) -> Any: return None


@inject(use_factory=True, alias=ScriptActionExecutionBuilderProtocol)
class ScriptActionExecutionBuilder(ScriptActionExecutionBuilderProtocol):
    
    def __init__(self):
        settings = di[SettingsManagerProtocol]
        self.working_dir = settings.field_value(SettingsManagerField.SCRIPTS_PATH)
    
    def build(self, action: ScriptAction) -> Any:
        if isinstance(action, ScriptInputEventAction):
            result = ScriptActionKeyExecution(action)
        else:
            if isinstance(action, ScriptMessageAction):
                result = ScriptActionMessageExecution(action)
            elif isinstance(action, NOOPScriptRunAction):
                result = ScriptNOOPExecution()
            elif isinstance(action, ScriptRunAction):
                script_file_path = action.path
                script_data = ScriptStorage(script_file_path).read_script_data_from_file()
                result = ScriptActionScriptExecution(script_file_path, script_data.get_actions(), self)
            elif isinstance(action, ScriptSnapshotAction):
                result = ScriptSnapshotExecution(action)
            else:
                assert False # ScriptAction implement: not implemented
        
        return result
