from win10toast import ToastNotifier
#from pync import Notifier

# Duration before the notification is erased from history. 24 hours.
# For win10toast, only one notification may be shown at a time.
DURATION = 5 # 5 sec

singleton = ToastNotifier()

class OSNotification:
    title: str
    message: str
    
    def __init__(self, title, message):
        self.title = title
        self.message = message
    
    def show(self):
        # TODO: support Mac (maybe use pync?)
        singleton.show_toast(self.title, self.message, duration=DURATION, threaded=True)
        print(f'OSNotification: show notification {self.message}')
