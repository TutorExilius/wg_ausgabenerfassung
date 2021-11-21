from functools import partial
from pathlib import Path
from typing import List

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWizard, QWizardPage


class StartPage(QWizardPage):
    leave_start_page = pyqtSignal(str)

    def __init__(self, parent: QWizard, user_names: List[str]) -> None:
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / "ui" / "start_page.ui", self)

        # connections
        self.pushButton_name_1.clicked.connect(partial(self.button_clicked, False, user_names[0]))
        self.pushButton_name_2.clicked.connect(partial(self.button_clicked, False, user_names[1]))

    def button_clicked(self, _, name):
        self.leave_start_page.emit(name)
