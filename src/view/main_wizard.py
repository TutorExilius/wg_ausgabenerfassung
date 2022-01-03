import asyncio
from datetime import datetime
from enum import auto, Enum
from pathlib import Path
from typing import List

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QWizard
from src import globals
from src.logic.database import add_amount, get_oldest_year, get_total_amount_in_cents
from src.logic.helper import amount_in_cents_to_str, print_log, sync_database
from src.view.input_page import InputPage
from src.view.start_page import StartPage


class PageNumber(Enum):
    START_PAGE = auto()
    INPUT_PAGE = auto()


class MainWizard(QWizard):
    def __init__(self, parent: QWidget = None, desktop_size: QtCore.QSize = None, user_names: List[str] = None):
        super().__init__(parent)

        self.user_names = user_names
        self._pages = {}

        self.setButtonLayout([])

        self._pages[PageNumber.START_PAGE] = self.addPage(StartPage(self, user_names))
        self._pages[PageNumber.INPUT_PAGE] = self.addPage(InputPage(self))

        start_page = self.page(self._pages[PageNumber.START_PAGE])
        start_page.pushButton_name_1.setText(self.user_names[0])
        start_page.pushButton_name_2.setText(self.user_names[1])

        self.update_year_label(datetime.utcnow().year)

        self.setModal(False)

        if desktop_size is not None:
            self.setFixedSize(desktop_size)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.setWindowState(self.windowState() | QtCore.Qt.WindowFullScreen)

        # connections
        self.page(self._pages[PageNumber.START_PAGE]).leave_start_page.connect(self.leave_start_page)
        self.page(self._pages[PageNumber.INPUT_PAGE]).leave_input_page.connect(self.leave_input_page)

    def update_year_label(self, year: int) -> None:
        start_page = self.page(self._pages[PageNumber.START_PAGE])
        start_page.label_year.setText(str(year))
        self.update_amounts()

    def update_amounts(self):
        start_page = self.page(self._pages[PageNumber.START_PAGE])
        selected_year = int(start_page.label_year.text())

        user_1_total_cents = get_total_amount_in_cents(
            user_name=self.user_names[0],
            year=selected_year
        )
        user_2_total_cents = get_total_amount_in_cents(
            user_name=self.user_names[1],
            year=selected_year
        )

        oldest_year = get_oldest_year()

        total_user_1 = 0
        total_user_2 = 0

        for year in range(oldest_year, selected_year):
            user_1_year_amount_in_cents = get_total_amount_in_cents(self.user_names[0], year)
            user_2_year_amount_in_cents = get_total_amount_in_cents(self.user_names[1], year)

            total_user_1 += user_1_year_amount_in_cents
            total_user_2 += user_2_year_amount_in_cents

        minimum_amount = min(total_user_1, total_user_2)
        total_user_1 -= minimum_amount
        total_user_2 -= minimum_amount

        user_1_total_cents += total_user_1
        user_2_total_cents += total_user_2

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
            src_database = Path(__file__).parent.parent.parent / globals.DATABASE_FILE
            target_database = Path(globals.SYNC_NAS_DIR)
            loop = asyncio.get_event_loop()
            loop.create_task(sync_database(src_database, target_database))

    def back(self, user_name: str) -> None:
        super(MainWizard, self).back()

    def _reset_input_page(self):
        input_page = self.page(self._pages[PageNumber.INPUT_PAGE])
        input_page.delete_input()
        input_page.delete_entries()
