from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
    QDateEdit,
    QTextEdit,
)



from ispring_db.core.database import create_db_and_tables
from ispring_db.models import Logbook
from ispring_db.services.logbook_repository import save_log
from ispring_db.services.device_repository import get_all_devices


class LogbookFormWindow(QWidget):
    def __init__(self, logbook: Logbook | None = None, parent=None):
        super().__init__(parent)

        self.logbook = logbook

        if self.logbook:
            self.setWindowTitle(f"Edit Log #{self.logbook.log_id}")
        else:
            self.setWindowTitle("New Log")

        self.resize(450, 320)

        self.device_input = QComboBox()

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd.MM.yyyy")
        self.date_input.setDate(QDate.currentDate())

        self.author_input = QLineEdit()

        self.text_input = QTextEdit()
        self.text_input.setFixedHeight(140)

        form = QFormLayout()
        form.addRow("Device", self.device_input)
        form.addRow("Log Date", self.date_input)
        form.addRow("Author", self.author_input)
        form.addRow("Log Text", self.text_input)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_logbook)
        self.cancel_button.clicked.connect(self.close)

        buttons = QHBoxLayout()
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(buttons)
        self.setLayout(layout)

        self.load_devices()

        if self.logbook:
            self.load_logbook()

    def load_devices(self) -> None:

        devices = get_all_devices()

        self.device_input.clear()
        self.device_input.addItem("", None)

        for device in devices:
            self.device_input.addItem(device.mac, device.mac)

    def load_logbook(self) -> None:
        if self.logbook.mac:
            index = self.device_input.findData(self.logbook.mac)
            if index >= 0:
                self.device_input.setCurrentIndex(index)

        if self.logbook.log_date:
            self.date_input.setDate(QDate(self.logbook.log_date))

        self.author_input.setText(self.logbook.log_author or "")
        self.text_input.setPlainText(self.logbook.log_text or "")

    def save_logbook(self) -> None:
        mac = self.device_input.currentData()
        log_author = self.author_input.text().strip()
        log_text = self.text_input.toPlainText().strip()
        log_date = self.date_input.date().toPython()

        if not mac:
            QMessageBox.warning(self, "Validation", "Please select a device.")
            return

        if not log_author:
            QMessageBox.warning(self, "Validation", "Please enter an author.")
            return

        if not log_text:
            QMessageBox.warning(self, "Validation", "Please enter log text.")
            return

        try:
            logbook = Logbook(
                log_id=self.logbook.log_id if self.logbook else None,
                mac=mac,
                log_date=log_date,
                log_author=log_author,
                log_text=log_text,
            )

            save_log(logbook)

            self.close()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save logbook entry:\n{e}",
            )


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    create_db_and_tables()

    app = QApplication(sys.argv)
    window = LogbookFormWindow()
    window.show()
    sys.exit(app.exec())