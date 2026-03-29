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
from ispring_db.gui.customer_licenses.customer_license_form import CustomerLicenseFormWindow
from ispring_db.services.customer_license_repository import (
    get_customer_license_rows,
    get_customer_license_rows_by_customer_no,
    get_customer_license_by_id,
    delete_customer_license_by_id,
)


class CustomerLicenseListBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setSortingEnabled(True)

        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Customer",
                "License",
                "Registration Date",
                "Expiration Date",
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
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        min_widths = [80, 180, 220, 140, 140]

        for col, min_w in enumerate(min_widths):
            if self.table.columnWidth(col) < min_w:
                self.table.setColumnWidth(col, min_w)

    def refresh_data(self) -> None:
        rows = get_customer_license_rows()
        self.load_customer_licenses(rows)
        QTimer.singleShot(0, self.apply_resize)

    def load_customer_licenses(self, rows) -> None:
        self.table.setRowCount(len(rows))

        for row, entry in enumerate(rows):
            self.table.setItem(
                row, 0, QTableWidgetItem(str(entry.customer_license_id))
            )
            self.table.setItem(row, 1, QTableWidgetItem(entry.customer))
            self.table.setItem(row, 2, QTableWidgetItem(entry.license))
            self.table.setItem(row, 3, QTableWidgetItem(entry.registration_date))
            self.table.setItem(row, 4, QTableWidgetItem(entry.expiration_date))

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

    def get_selected_customer_license_id(self, show_message: bool = True) -> int | None:
        row = self.table.currentRow()

        if row < 0:
            if show_message:
                QMessageBox.warning(
                    self, "Selection", "Please select a customer license."
                )
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
                QMessageBox.warning(
                    self, "Selection", "Customer license ID is invalid."
                )
            return None


class CustomerLicenseListWindow(CustomerLicenseListBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Customer Licenses")
        self.resize(950, 500)

        self.form = None

        self.new_button = QPushButton("New")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        self.new_button.clicked.connect(self.new_customer_license)
        self.edit_button.clicked.connect(self.edit_customer_license)
        self.delete_button.clicked.connect(self.delete_customer_license)
        self.refresh_button.clicked.connect(self.refresh_data)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)

        self.main_layout.addLayout(button_layout)

        self.refresh_data()

    def new_customer_license(self) -> None:
        self.form = CustomerLicenseFormWindow()
        self.form.show()
        self.form.destroyed.connect(self.refresh_data)

    def edit_customer_license(self) -> None:
        customer_license_id = self.get_selected_customer_license_id()
        if customer_license_id is None:
            return

        customer_license = get_customer_license_by_id(customer_license_id)

        if customer_license is None:
            QMessageBox.warning(self, "Error", "Customer license not found.")
            self.refresh_data()
            return

        self.form = CustomerLicenseFormWindow(customer_license)
        self.form.show()
        self.form.destroyed.connect(self.refresh_data)

    def delete_customer_license(self) -> None:
        customer_license_id = self.get_selected_customer_license_id()
        if customer_license_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete Customer License",
            f"Delete customer license '{customer_license_id}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        try:
            deleted = delete_customer_license_by_id(customer_license_id)

            if not deleted:
                QMessageBox.warning(self, "Error", "Customer license not found.")
                self.refresh_data()
                return

            self.refresh_data()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not delete customer license:\n{e}",
            )


class CustomerLicenseListDisplay(CustomerLicenseListBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customer Licenses")
        self.table.setRowCount(0)

    def load_for_customer(self, customer_no: int) -> None:
        rows = get_customer_license_rows_by_customer_no(customer_no)
        self.load_customer_licenses(rows)
        QTimer.singleShot(0, self.apply_resize)

    def clear_data(self) -> None:
        self.table.setRowCount(0)
        self.table.clearContents()
        self.table.clearSelection()
        QTimer.singleShot(0, self.apply_resize)

    def apply_filter(self, text: str) -> None:
        text = text.lower().strip()

        for row in range(self.table.rowCount()):
            row_matches = False

            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    row_matches = True
                    break

            self.table.setRowHidden(row, not row_matches)


if __name__ == "__main__":
    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)
    window = CustomerLicenseListWindow()
    window.show()
    sys.exit(app.exec())