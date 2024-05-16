from typing import Protocol
from kink import inject, di
from plyer import notification

from Utilities.Logger import LoggerProtocol

DURATION = 5 # 5 sec


class OSNotificationCenterProtocol(Protocol):
    def show(self, title, message): assert False


@inject(alias=OSNotificationCenterProtocol)
class OSNotificationCenter(OSNotificationCenterProtocol):
    
    def __init__(self):
        super(OSNotificationCenter, self).__init__()
        self.logger = di[LoggerProtocol]
    
    def show(self, title, message):
        self.logger.info(f'OSNotificationCenter: show notification {title} - {message}')
        notification.notify(title=title, message=message, timeout=DURATION)

