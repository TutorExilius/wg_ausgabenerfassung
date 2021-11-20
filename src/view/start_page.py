import datetime
from pathlib import Path
from functools import partial

from PyQt5 import uic
from PyQt5.QtWidgets import QWizardPage, QWizard
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import pyqtSignal

from logic.helper import print_log

class StartPage(QWizardPage):
    leave_start_page = pyqtSignal(str)

    def __init__(self, parent: QWizard) -> None:
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / "ui" / "start_page.ui", self)

        # connections
        self.pushButton_name_1.clicked.connect(partial(self.button_clicked, False, self.pushButton_name_1.text()))
        self.pushButton_name_2.clicked.connect(partial(self.button_clicked, False, self.pushButton_name_2.text()))

    def button_clicked(self, _, name):
        self.leave_start_page.emit(name)

