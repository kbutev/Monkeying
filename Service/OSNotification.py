from win10toast import ToastNotifier
#from pync import Notifier

DURATION = 60 * 60 * 24 # Duration before the notification is erased from history. 24 hours.

class OSNotification:
    title: str
    message: str
    toast = ToastNotifier()
    
    def __init__(self, title, message):
        self.title = title
        self.message = message
    
    def show(self):
        # TODO: support Mac (maybe use pync?)
        self.toast.show_toast(self.title, self.message, duration=DURATION, threaded=True)
