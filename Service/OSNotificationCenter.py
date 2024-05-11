from PyQt5.QtCore import QThread, QObject
from plyer import notification

DURATION = 5 # 5 sec


class OSNotification(QThread):
    title: str
    message: str
    
    def __init__(self, title: str, message: str):
        super(OSNotification, self).__init__()
        self.title = title
        self.message = message
        
    def run(self):
        notification.notify(title=self.title, message=self.message, timeout=DURATION)


class OSNotificationCenter(QObject):
    def show(self, title, message):
        # TODO: support Mac (maybe use pync?)
        print(f'OSNotificationCenter: show notification {title} - {message}')
        notification = OSNotification(title, message)
        notification.start()


singleton = OSNotificationCenter()
