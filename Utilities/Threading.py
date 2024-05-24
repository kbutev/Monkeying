import threading
from Utilities.SimpleThreadWorker import SimpleThreadWorker
from Utilities.SimpleThreadWorker import run_on_main as run_on_main_internal


def current_thread_is_main(): return threading.current_thread() is threading.main_thread()


def get_current_thread_name():
    return 'main' if current_thread_is_main() else threading.get_ident()


def get_current_thread_description():
    return f'thread.{get_current_thread_name()}'


# The returned object must be kept until completion.
def run_on_main(handle) -> SimpleThreadWorker:
    return run_on_main_internal(handle)


# The returned object must be kept until completion.
def run_in_background(process_handle, completion_on_main_handle=None) -> SimpleThreadWorker:
    worker = SimpleThreadWorker(process_handle, completion_on_main_handle, completion_with_result=False)
    worker.start()
    return worker


# Process handle must return a value, which will be passed to the completion on main.
# The returned object must be kept until completion.
def run_in_background_with_result(process_handle, completion_on_main_handle, process_with_param=None) -> SimpleThreadWorker:
    worker = SimpleThreadWorker(process_handle,
                                completion_on_main_handle,
                                process_with_param=process_with_param,
                                completion_with_result=True)
    worker.start()
    return worker
