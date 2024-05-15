from typing import Protocol
from PyQt5.QtCore import QThread, QObject
from kink import inject, di
from plyer import notification

from Utilities.Logger import LoggerProtocol

DURATION = 5 # 5 sec


class OSNotification(QThread):
    
    def __init__(self, title: str, message: str):
        super(OSNotification, self).__init__()
        self.title = title
        self.message = message
        
    def run(self):
        notification.notify(title=self.title, message=self.message, timeout=DURATION)


class OSNotificationCenterProtocol(Protocol):
    def show(self, title, message): assert False


@inject(alias=OSNotificationCenterProtocol)
class OSNotificationCenter(QObject):
    
    def __init__(self):
        super(OSNotificationCenter, self).__init__()
        self.logger = di[LoggerProtocol]
    
    def show(self, title, message):
        self.logger.info(f'OSNotificationCenter: show notification {title} - {message}')
        n = OSNotification(title, message)
        n.start()

