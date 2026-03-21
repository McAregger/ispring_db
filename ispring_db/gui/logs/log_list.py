from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
)

from sqlmodel import select

from ispring_db.core.database import create_db_and_tables, get_session
from ispring_db.models import Logbook, Device, Customer
from ispring_db.gui.logs.log_form import LogFormWindow


class LogListBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            [
                "Log ID",
                "Device MAC",
                "Customer",
                "Date",
                "Author",
                "Log"
            ]
        )

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.ElideRight)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.table)
        self.setLayout(self.main_layout)

    def refresh_data(self) -> None:
        with get_session() as session:
            logs = session.exec(select(Logbook)).all()

        self._fill_table(logs)

    def _fill_table(self, logs: list[Logbook]) -> None:
        self.table.setRowCount(len(logs))

        with get_session() as session:
            for row, log in enumerate(logs):

                # Device holen
                device = None
                customer_text = ""

                if log.mac:
                    device = session.get(Device, log.mac)

                # Customer bestimmen
                if device and device.customer_no:
                    customer = session.get(Customer, device.customer_no)
                    if customer:
                        customer_text = customer.company
                elif device:
                    customer_text = device.mac

                # Tabelle füllen
                self.table.setItem(row, 0, QTableWidgetItem(str(log.log_id or "")))
                self.table.setItem(row, 1, QTableWidgetItem(str(log.mac or "")))
                self.table.setItem(row, 2, QTableWidgetItem(customer_text))
                self.table.setItem(row, 3, QTableWidgetItem(str(log.log_date or "")))
                self.table.setItem(row, 4, QTableWidgetItem(str(log.log_author or "")))
                self.table.setItem(row, 5, QTableWidgetItem(str(log.log_text or "")))

                self.table.setRowHeight(row, 24)

        self.table.clearSelection()

    def get_selected_log_id(self, show_message: bool = True) -> int | None:
        row = self.table.currentRow()

        if row < 0:
            if show_message:
                QMessageBox.warning(self, "Selection", "Please select a log entry.")
            return None

        item = self.table.item(row, 0)
        if item is None:
            return None

        try:
            return int(item.text())
        except ValueError:
            return None


class LogListWindow(LogListBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Logbook")
        self.resize(900, 500)

        self.new_button = QPushButton("New")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        self.new_button.clicked.connect(self.new_log)
        self.edit_button.clicked.connect(self.edit_log)
        self.delete_button.clicked.connect(self.delete_log)
        self.refresh_button.clicked.connect(self.refresh_data)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)

        self.main_layout.addLayout(button_layout)

        self.refresh_data()

    def new_log(self) -> None:
        self.form = LogFormWindow()
        self.form.show()
        self.form.destroyed.connect(self.refresh_data)

    def edit_log(self) -> None:
        log_id = self.get_selected_log_id()
        if log_id is None:
            return

        with get_session() as session:
            log = session.get(Logbook, log_id)

        if not log:
            QMessageBox.warning(self, "Error", "Log entry not found.")
            return

        self.form = LogFormWindow(log)
        self.form.show()
        self.form.destroyed.connect(self.refresh_data)

    def delete_log(self) -> None:
        log_id = self.get_selected_log_id()
        if log_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete",
            f"Delete log entry {log_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        try:
            with get_session() as session:
                log = session.get(Logbook, log_id)

                if not log:
                    QMessageBox.warning(self, "Error", "Log entry not found.")
                    return

                session.delete(log)
                session.commit()

            self.refresh_data()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class LogListDisplay(LogListBase):
    def __init__(self, parent=None):
        super().__init__(parent)

    def load_for_device(self, mac: str) -> None:
        with get_session() as session:
            logs = session.exec(
                select(Logbook).where(Logbook.mac == mac)
            ).all()

        self._fill_table(logs)

    def clear_data(self) -> None:
        self.table.setRowCount(0)


if __name__ == "__main__":
    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)
    window = LogListWindow()  # ✅ korrekt
    window.show()
    sys.exit(app.exec())