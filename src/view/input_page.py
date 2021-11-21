from functools import partial
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import QListWidgetItem, QWizard, QWizardPage
from src.logic.helper import max_digits_behind_comma_arrived
from src.view.input_back_and_save_dialog import InputBackAndSaveDialog
from src.view.input_back_dialog import InputBackDialog
from src.view.remove_entries_dialog import RemoveEntriesDialog


class InputPage(QWizardPage):
    leave_input_page = pyqtSignal(str, str)

    def __init__(self, parent: QWizard) -> None:
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / "ui" / "input_page.ui", self)

        # connections
        self.pushButton_back.clicked.connect(self.back_button_clicked)
        self.pushButton_save_back.clicked.connect(self.back_and_save_button_clicked)
        self.pushButton_remove_selected_items.clicked.connect(self.remove_selected_items)
        self.listWidget_inputs.itemSelectionChanged.connect(self.entries_selection_changed)
        self.listWidget_inputs.model().rowsRemoved.connect(self.entries_changed)
        self.listWidget_inputs.model().rowsInserted.connect(self.entries_changed)
        self.pushButton_0.clicked.connect(partial(self.lineEdit_input_digit, False, "0"))
        self.pushButton_1.clicked.connect(partial(self.lineEdit_input_digit, False, "1"))
        self.pushButton_2.clicked.connect(partial(self.lineEdit_input_digit, False, "2"))
        self.pushButton_3.clicked.connect(partial(self.lineEdit_input_digit, False, "3"))
        self.pushButton_4.clicked.connect(partial(self.lineEdit_input_digit, False, "4"))
        self.pushButton_5.clicked.connect(partial(self.lineEdit_input_digit, False, "5"))
        self.pushButton_6.clicked.connect(partial(self.lineEdit_input_digit, False, "6"))
        self.pushButton_7.clicked.connect(partial(self.lineEdit_input_digit, False, "7"))
        self.pushButton_8.clicked.connect(partial(self.lineEdit_input_digit, False, "8"))
        self.pushButton_9.clicked.connect(partial(self.lineEdit_input_digit, False, "9"))
        self.pushButton_comma.clicked.connect(partial(self.lineEdit_input_digit, False, ","))
        self.pushButton_del.clicked.connect(partial(self.lineEdit_input_digit, False, "DEL"))
        self.pushButton_add.clicked.connect(self.add_entry_to_list)
        self.pushButton_clear.clicked.connect(self.delete_input)

    def delete_input(self):
        text = self.lineEdit_input.text()

        for _ in range(len(text)):
            self.lineEdit_input_digit(False, "DEL")

    def delete_entries(self):
        self.listWidget_inputs.clear()
        self.label_total_amount.setText("0,00 €")
        self.pushButton_save_back.setEnabled(False)

    def add_entry_to_list(self):
        text = self._remove_leading_zeros(self.lineEdit_input.text())
        item = QListWidgetItem(text)
        self.listWidget_inputs.addItem(item)
        self.delete_input()

    def lineEdit_input_digit(self, _: bool, digit: str):
        old_text = self.lineEdit_input.text()
        if max_digits_behind_comma_arrived(old_text) and digit != "DEL":
            return

        if digit == "DEL":
            if not old_text:
                return

            deleting_digit = old_text[-1]

            if deleting_digit == ",":
                self.pushButton_comma.setEnabled(True)

            text = old_text[:-1]
        elif digit == ",":
            self.pushButton_comma.setEnabled(False)

            if old_text:
                text = old_text + digit
            else:
                text = "0" + digit
        else:
            text = old_text + digit

        self.lineEdit_input.setText(text)

        if text:
            self.pushButton_del.setEnabled(True)

            if max_digits_behind_comma_arrived(text):
                self.pushButton_add.setEnabled(True)
            else:
                self.pushButton_add.setEnabled(False)
        else:
            self.pushButton_del.setEnabled(False)
            self.pushButton_add.setEnabled(False)

    def entries_changed(self):
        print("entires changed")
        if self.listWidget_inputs.count():
            self.pushButton_save_back.setEnabled(True)
        else:
            self.pushButton_save_back.setEnabled(False)

        total_amout_cents = 0

        for i in range(self.listWidget_inputs.count()):
            item = self.listWidget_inputs.item(i).text()
            item = item.replace(",", "")
            total_amout_cents += int(item)

        if total_amout_cents == 0:
            self.label_total_amount.setText("0,00 €")
        else:
            new_text = str(total_amout_cents)
            new_text = new_text[:-2] + "," + new_text[-2:]

            if new_text.startswith(","):
                if len(new_text) == 2:
                    new_text = new_text.replace(",", "0,0")
                else:
                    new_text = new_text.replace(",", "0,")

            self.label_total_amount.setText(new_text + " €")

    def entries_selection_changed(self):
        selected_items = self.listWidget_inputs.selectedItems()

        if selected_items:
            self.pushButton_remove_selected_items.setStyleSheet("font-weight: bold;")
            self.pushButton_remove_selected_items.setEnabled(True)
        else:
            self.pushButton_remove_selected_items.setStyleSheet("font-weight: normal;")
            self.pushButton_remove_selected_items.setEnabled(False)

    def back_and_save_button_clicked(self):
        dialog = InputBackAndSaveDialog(self)
        dialog.exec()

        if InputBackAndSaveDialog.is_last_response_yes:
            QCoreApplication.processEvents()

            name = self.label_name.text()
            self.leave_input_page.emit(name, self.label_total_amount.text())

    def back_button_clicked(self):
        if self.listWidget_inputs.count() == 0:
            name = self.label_name.text()
            self.leave_input_page.emit(name, "")
            return

        dialog = InputBackDialog(self)
        dialog.exec()

        if InputBackDialog.is_last_response_yes:
            QCoreApplication.processEvents()

            name = self.label_name.text()
            self.leave_input_page.emit(name, "")

    def remove_selected_items(self):
        dialog = RemoveEntriesDialog(self)
        dialog.exec()

        if RemoveEntriesDialog.is_last_response_yes:
            selected_items = self.listWidget_inputs.selectedItems()

            for item in selected_items:
                self.listWidget_inputs.takeItem(self.listWidget_inputs.row(item))
                del item

    def _remove_leading_zeros(self, text):
        before_first_digit_of_integer_part = -4
        # ex: v              v---before_first_digit_of_integer_part
        # ......1,99..or....1234,99

        to_trailing_text = text[0:before_first_digit_of_integer_part]
        rest_text = text[before_first_digit_of_integer_part:]
        trailing_text = to_trailing_text.lstrip("0")
        return trailing_text + rest_text
