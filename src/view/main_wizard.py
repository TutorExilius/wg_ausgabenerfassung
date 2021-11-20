from enum import auto, Enum

from logic.helper import print_log
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWizard

from .input_page import InputPage
from .start_page import StartPage


class PageNumber(Enum):
    START_PAGE = auto()
    INPUT_PAGE = auto()


class MainWizard(QWizard):
    def __init__(self, parent=None, desktop_size=None):
        super().__init__(parent)  # , QtCore.Qt.Tool)

        self._pages = {}
        self.setButtonLayout([])

        self._pages[PageNumber.START_PAGE] = self.addPage(StartPage(self))
        self._pages[PageNumber.INPUT_PAGE] = self.addPage(InputPage(self))

        self.setModal(False)

        if desktop_size is not None:
            self.setFixedSize(desktop_size)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.setWindowState(self.windowState() | QtCore.Qt.WindowFullScreen)

        # connections
        self.page(self._pages[PageNumber.START_PAGE]).leave_start_page.connect(self.leave_start_page)
        self.page(self._pages[PageNumber.INPUT_PAGE]).leave_input_page.connect(self.leave_input_page)

    @QtCore.pyqtSlot(str)
    def leave_start_page(self, user_name):
        print_log(
            page_name="StartPage",
            user_name=user_name,
            action=f"is entering the InputPage"
        )
        self.next(user_name)

    @QtCore.pyqtSlot(str, str)
    def leave_input_page(self, user_name: str, amount: str):
        if amount:
            print_log(
                page_name="InputPage",
                user_name=user_name,
                action=f"is leaving the InputPage. Save {amount}"
            )
            self.back_and_save(user_name, amount)
        else:
            print_log(
                page_name="InputPage",
                user_name=user_name,
                action="is leaving the InputPage without saving"
            )
            self.back(user_name)

        self._reset_input_page()

    def next(self, user_name: str) -> None:
        super(MainWizard, self).next()
        input_page = self.page(self._pages[PageNumber.INPUT_PAGE])
        input_page.label_name.setText(user_name)

    def back_and_save(self, user_name: str, amount: str) -> None:
        amount = amount.removesuffix("€").strip()
        amount = amount.replace(",", "")

        super(MainWizard, self).back()

    def back(self, user_name: str) -> None:
        super(MainWizard, self).back()

    def _reset_input_page(self):
        input_page = self.page(self._pages[PageNumber.INPUT_PAGE])
        input_page.delete_input()
        input_page.delete_entries()
