from typing import Protocol
from kink import di

from Dialog.Dialog import Dialog, build_error_dialog
from Model.ScriptData import ScriptData
from Model.ScriptSummary import ScriptSummary
from Presenter.Presenter import Presenter
from MainView.ShowScriptsWidget import ShowScriptsWidgetProtocol
from Provider.ScriptDataProvider import ScriptDataProvider
from Service.ScriptStorage import ScriptStorage
from Service.SettingsManager import SettingsManagerField, SettingsManagerProtocol
from Service.ThreadWorkerManager import ThreadWorkerManagerProtocol
from Utilities import Path as PathUtils
from Utilities.Logger import LoggerProtocol
from Utilities.Rect import Rect
from Utilities.Threading import run_in_background_with_result


THREAD_WORKER_RELOAD_LABEL = 'reload'
THREAD_WORKER_READ_LABEL = 'read_script'


class ShowScriptsWidgetRouter(Protocol):
    def open_script(self, parent, script: ScriptData): pass


class ShowScriptsPresenter(Presenter):
    
    # - Init
    
    def __init__(self):
        super(ShowScriptsPresenter, self).__init__()
        settings = di[SettingsManagerProtocol]
        self.widget = None
        self.router = None
        self.working_dir = settings.field_value(SettingsManagerField.SCRIPTS_PATH)
        self.file_format = settings.field_value(SettingsManagerField.SCRIPTS_FILE_FORMAT)
        self.scripts = []
        self.logger = di[LoggerProtocol]
        self.thread_worker_manager = di[ThreadWorkerManagerProtocol]
    
    # - Property
    
    def get_widget(self) -> ShowScriptsWidgetProtocol: return self.widget
    def set_widget(self, widget): self.widget = widget
    def get_router(self) -> ShowScriptsWidgetRouter: return self.router
    def set_router(self, router): self.router = router
    
    # - Setup
    
    def setup(self):
        self.reload_data()
    
    # - Actions
    
    def start(self):
        assert self.widget is not None
        
        self.logger.info('start presenter')
        self.setup()
    
    def reload_data(self):
        if self.thread_worker_manager.is_running_worker(THREAD_WORKER_RELOAD_LABEL):
            return
        
        self.logger.info('reloading data...')
        
        worker = run_in_background_with_result(self._load_scripts_data_in_background,
                                               self._finish_loading_scripts_data)
        self.thread_worker_manager.add_worker(worker, THREAD_WORKER_RELOAD_LABEL)
    
    def _load_scripts_data_in_background(self):
        result = []
        
        file_list = PathUtils.directory_file_list(self.working_dir, self.file_format)
        
        script_names = []
        
        for file_path in file_list:
            storage = ScriptStorage(file_path)
            
            try:
                script_summary = storage.read_script_summary_from_file()
                name = script_summary.get_info().name
                script_names.append(name)
                result.append(script_summary)
            except Exception:
                pass
        
        return result
    
    def _finish_loading_scripts_data(self, result):
        self.thread_worker_manager.remove_worker(THREAD_WORKER_RELOAD_LABEL)
        
        self.logger.info(f'finished loading script data, found {len(result)} scripts in work directory')
        
        self.scripts = result
        
        script_names = []
        
        for script in self.scripts:
            script_names.append(script.get_info().name)
        
        self.widget.set_data(script_names)
    
    def _finish_opening_script(self, result: ScriptData):
        self.thread_worker_manager.remove_worker(THREAD_WORKER_READ_LABEL)
        self.router.open_script(self.widget, result)
    
    def _finish_opening_script_error(self, result: Exception):
        self.thread_worker_manager.remove_worker(THREAD_WORKER_READ_LABEL)
        dialog = build_error_dialog(self.widget, "Error", f"Bad script:\n{result}.")
        dialog.present()
    
    # Script actions
    
    def can_open_script(self, item) -> bool: return True
    
    def open_script(self, index):
        assert index >= 0 and index < len(self.scripts)
        
        if self.thread_worker_manager.is_running_worker(THREAD_WORKER_READ_LABEL):
            return

        script: ScriptSummary = self.scripts[index]
        
        worker = ScriptDataProvider(script.get_file_path())
        self.thread_worker_manager.add_worker(worker, THREAD_WORKER_READ_LABEL)
        worker.fetch(self._finish_opening_script, self._finish_opening_script_error)

