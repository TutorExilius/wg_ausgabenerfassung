from pathlib import Path

from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QWizardPage


class InputBackDialog(QDialog):
    is_last_response_yes = False

    def __init__(self, parent: QWizardPage) -> None:
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / "ui" / "input_back_dialog.ui", self)

        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMinMaxButtonsHint, False)

        # connections
        self.pushButton_yes.clicked.connect(self.response_yes)
        self.pushButton_no.clicked.connect(self.response_no)

    def response_yes(self):
        InputBackDialog.is_last_response_yes = True
        self.close()

    def response_no(self):
        InputBackDialog.is_last_response_yes = False
        self.close()
