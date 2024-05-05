# Python 3
from MainView.MainWidget import MainWidget
from PyQt5.QtWidgets import QApplication
import sys
from MainView.MainRouter import MainRouter

# Primary setup
router = MainRouter()

app = QApplication(sys.argv)
app.setApplicationName('Monkeying')
router.setup()
router.widget.show()
router.widget.setMaximumSize(1024, 640)

# Exec
app.exec()
