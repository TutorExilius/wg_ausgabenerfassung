import asyncio
from datetime import datetime
from enum import auto, Enum
from typing import List
from pathlib import Path

from logic.helper import amount_in_cents_to_str, print_log, sync_database
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QWizard
from src.logic.database import add_amount, get_total_amount_in_cents

from .input_page import InputPage
from .start_page import StartPage
from src.globals import DATABASE_FILE, SYNC_NAS_DIR

class PageNumber(Enum):
    START_PAGE = auto()
    INPUT_PAGE = auto()


class MainWizard(QWizard):
    def __init__(self, parent: QWidget = None, desktop_size: QtCore.QSize = None, users: List[str] = None):
        super().__init__(parent)

        self.users = users
        self._pages = {}

        self.setButtonLayout([])

        self._pages[PageNumber.START_PAGE] = self.addPage(StartPage(self))
        self._pages[PageNumber.INPUT_PAGE] = self.addPage(InputPage(self))

        start_page = self.page(self._pages[PageNumber.START_PAGE])
        start_page.pushButton_name_1.setText(self.users[0])
        start_page.pushButton_name_2.setText(self.users[1])

        self.update_amounts()

        self.setModal(False)

        if desktop_size is not None:
            self.setFixedSize(desktop_size)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.setWindowState(self.windowState() | QtCore.Qt.WindowFullScreen)

        # connections
        self.page(self._pages[PageNumber.START_PAGE]).leave_start_page.connect(self.leave_start_page)
        self.page(self._pages[PageNumber.INPUT_PAGE]).leave_input_page.connect(self.leave_input_page)

    def update_amounts(self):
        start_page = self.page(self._pages[PageNumber.START_PAGE])

        user_1_total_cents = get_total_amount_in_cents(
            user_name=self.users[0],
            year=datetime.year
        )
        user_2_total_cents = get_total_amount_in_cents(
            user_name=self.users[1],
            year=datetime.year
        )
        start_page.label_amount_1.setText(amount_in_cents_to_str(user_1_total_cents))
        start_page.label_amount_2.setText(amount_in_cents_to_str(user_2_total_cents))

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
        amount = amount.replace("€", "").strip()
        amount = int(amount.replace(",", ""))  # remove comma to interpret as cent

        super(MainWizard, self).back()

        if amount > 0:
            add_amount(
                user_name=user_name,
                amount_in_cents=amount,
            )
            self.update_amounts()

            print("Try syncing database...")
            src_database = Path(__file__).parent.parent.parent / DATABASE_FILE
            target_database = Path(SYNC_NAS_DIR)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(sync_database(src_database, target_database))

    def back(self, user_name: str) -> None:
        super(MainWizard, self).back()

    def _reset_input_page(self):
        input_page = self.page(self._pages[PageNumber.INPUT_PAGE])
        input_page.delete_input()
        input_page.delete_entries()
