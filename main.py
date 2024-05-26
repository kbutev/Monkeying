# Python 3
import os

from PyQt5.QtWidgets import QApplication
import sys
from MainView.MainRouter import MainRouter
from Service.Dependencies import DependencyService

SCRIPTS_PATH = 'scripts'

# DI
DependencyService.setup()

# Scripts folder
if not os.path.exists(SCRIPTS_PATH):
    os.makedirs(SCRIPTS_PATH)

# Primary setup
router = MainRouter()

app = QApplication(sys.argv)
app.setApplicationName('Monkeying')
router.setup()
router.widget.show()
router.widget.setMaximumSize(1024, 640)

# Exec
app.exec()
