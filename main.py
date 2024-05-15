# Python 3
from PyQt5.QtWidgets import QApplication
import sys
from MainView.MainRouter import MainRouter
from Service.Dependencies import DependencyService

# DI
DependencyService.setup()

# Primary setup
router = MainRouter()

app = QApplication(sys.argv)
app.setApplicationName('Monkeying')
router.setup()
router.widget.show()
router.widget.setMaximumSize(1024, 640)

# Exec
app.exec()
