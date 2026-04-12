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
from ispring_db.gui.license.license_form import LicenseFormWindow
from ispring_db.repositories.license_repository import (
    get_license_by_id,
    get_all_licenses,
    delete_license_by_id,
)


class LicenseListBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setSortingEnabled(True)

        self.table.setHorizontalHeaderLabels(
            [
                "License ID",
                "License Name",
                "License Release",
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

        min_widths = [120, 200, 180]

        for col, min_w in enumerate(min_widths):
            if self.table.columnWidth(col) < min_w:
                self.table.setColumnWidth(col, min_w)

    def refresh_data(self) -> None:
        licenses = get_all_licenses()
        self.load_licenses(licenses)
        QTimer.singleShot(0, self.apply_resize)

    def load_licenses(self, licenses: list) -> None:
        self.table.setRowCount(len(licenses))

        for row, license_obj in enumerate(licenses):
            self.table.setItem(row, 0, QTableWidgetItem(str(license_obj.license_id)))
            self.table.setItem(row, 1, QTableWidgetItem(license_obj.license_name or ""))
            self.table.setItem(row, 2, QTableWidgetItem(license_obj.license_release or ""))

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

    def get_selected_license_id(self, show_message: bool = True) -> int | None:
        row = self.table.currentRow()

        if row < 0:
            if show_message:
                QMessageBox.warning(self, "Selection", "Please select a license.")
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
                QMessageBox.warning(self, "Selection", "License ID is invalid.")
            return None


class LicenseListWindow(LicenseListBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Licenses")
        self.resize(700, 450)

        self.form = None

        self.new_button = QPushButton("New")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        self.new_button.clicked.connect(self.new_license)
        self.edit_button.clicked.connect(self.edit_license)
        self.delete_button.clicked.connect(self.delete_license)
        self.refresh_button.clicked.connect(self.refresh_data)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)

        self.main_layout.addLayout(button_layout)

        self.refresh_data()

    def new_license(self) -> None:
        self.form = LicenseFormWindow()
        self.form.show()
        self.form.destroyed.connect(self.refresh_data)

    def edit_license(self) -> None:
        license_id = self.get_selected_license_id()
        if license_id is None:
            return

        license_obj = get_license_by_id(license_id)

        if license_obj is None:
            QMessageBox.warning(self, "Error", "License not found.")
            self.refresh_data()
            return

        self.form = LicenseFormWindow(license_obj)
        self.form.show()
        self.form.destroyed.connect(self.refresh_data)

    def delete_license(self) -> None:
        license_id = self.get_selected_license_id()
        if license_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete License",
            f"Delete license '{license_id}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        try:
            deleted = delete_license_by_id(license_id)

            if not deleted:
                QMessageBox.warning(self, "Error", "License not found.")
                self.refresh_data()
                return

            self.refresh_data()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not delete license:\n{e}",
            )


if __name__ == "__main__":
    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)
    window = LicenseListWindow()
    window.show()
    sys.exit(app.exec())