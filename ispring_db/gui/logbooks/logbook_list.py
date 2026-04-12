from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
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

from ispring_db.core.database import create_db_and_tables
from ispring_db.gui.logbooks.logbook_form import LogbookFormWindow
from ispring_db.repositories.logbook_repository import (
    get_log_by_id,
    get_logbook_table_rows,
    get_logbook_table_rows_by_mac,
    delete_log,
)


class LogbookListBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setSortingEnabled(True)

        self.table.setHorizontalHeaderLabels(
            [
                "Log ID",
                "MAC",
                "Date",
                "Author",
                "Text",
            ]
        )

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.ElideRight)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.table)
        self.setLayout(self.main_layout)

    def apply_resize(self) -> None:
        header = self.table.horizontalHeader()

        self.table.resizeColumnsToContents()

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        min_widths = [90, 160, 120, 150, 250]

        for col, min_w in enumerate(min_widths):
            if self.table.columnWidth(col) < min_w:
                self.table.setColumnWidth(col, min_w)

    def refresh_data(self) -> None:
        rows = get_logbook_table_rows()
        self.load_logs(rows)
        QTimer.singleShot(0, self.apply_resize)

    def load_logs(self, rows) -> None:
        self.table.setRowCount(len(rows))

        for row, log in enumerate(rows):
            self.table.setItem(row, 0, QTableWidgetItem(log.log_id))
            self.table.setItem(row, 1, QTableWidgetItem(log.mac))
            self.table.setItem(row, 2, QTableWidgetItem(log.log_date))
            self.table.setItem(row, 3, QTableWidgetItem(log.log_author))
            self.table.setItem(row, 4, QTableWidgetItem(log.log_text))

        self.table.resizeRowsToContents()
        self.table.clearSelection()

    def apply_filter(self, text: str) -> None:
        text = text.strip().lower()

        for row in range(self.table.rowCount()):
            if not text:
                self.table.setRowHidden(row, False)
                continue

            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break

            self.table.setRowHidden(row, not match)

    def get_selected_log_id(self, show_message: bool = True) -> int | None:
        row = self.table.currentRow()

        if row < 0:
            if show_message:
                QMessageBox.warning(self, "Selection", "Please select a log entry.")
            return None

        item = self.table.item(row, 0)
        if item is None:
            if show_message:
                QMessageBox.warning(self, "Selection", "Selected row is invalid.")
            return None

        try:
            return int(item.text())
        except ValueError:
            if show_message:
                QMessageBox.warning(self, "Selection", "Selected Log ID is invalid.")
            return None


class LogbookListWindow(LogbookListBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Logbook")
        self.resize(1000, 500)

        self.form = None

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
        self.form = LogbookFormWindow()
        self.form.show()
        self.form.destroyed.connect(self.refresh_data)

    def edit_log(self) -> None:
        log_id = self.get_selected_log_id()
        if log_id is None:
            return

        log = get_log_by_id(log_id)

        if log is None:
            QMessageBox.warning(self, "Error", "Log entry not found.")
            self.refresh_data()
            return

        self.form = LogbookFormWindow(log)
        self.form.show()
        self.form.destroyed.connect(self.refresh_data)

    def delete_log(self) -> None:
        log_id = self.get_selected_log_id()
        if log_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete Log Entry",
            f"Delete log entry '{log_id}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        try:
            deleted = delete_log(log_id)

            if not deleted:
                QMessageBox.warning(self, "Error", "Log entry not found.")
                self.refresh_data()
                return

            self.refresh_data()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not delete log entry:\n{e}",
            )


class LogbookListDisplay(LogbookListBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Logbook")
        self.table.setRowCount(0)

    def load_for_device(self, mac: str) -> None:
        rows = get_logbook_table_rows_by_mac(mac)
        self.load_logs(rows)
        QTimer.singleShot(0, self.apply_resize)

    def clear_data(self) -> None:
        self.table.setRowCount(0)
        self.table.clearContents()
        self.table.clearSelection()
        QTimer.singleShot(0, self.apply_resize)


if __name__ == "__main__":
    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)
    window = LogbookListWindow()
    window.show()
    sys.exit(app.exec())