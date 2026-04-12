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
from ispring_db.gui.gateways.gateway_form import GatewayFormWindow
from ispring_db.repositories.gateway_repository import (
    get_gateway_by_serial_no,
    get_gateway_table_rows,
    get_gateway_table_rows_by_customer_no,
    delete_gateway_by_serial_no,
)


class GatewayListBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setSortingEnabled(True)

        self.table.setHorizontalHeaderLabels(
            [
                "Serial No",
                "Customer",
                "SIM",
                "System",
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
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        min_widths = [140, 180, 120, 180]

        for col, min_w in enumerate(min_widths):
            if self.table.columnWidth(col) < min_w:
                self.table.setColumnWidth(col, min_w)

    def refresh_data(self) -> None:
        rows = get_gateway_table_rows()
        self.load_gateways(rows)
        QTimer.singleShot(0, self.apply_resize)

    def load_gateways(self, rows) -> None:
        self.table.setRowCount(len(rows))

        for row, gateway in enumerate(rows):
            self.table.setItem(row, 0, QTableWidgetItem(gateway.serial_no))
            self.table.setItem(row, 1, QTableWidgetItem(gateway.customer))
            self.table.setItem(row, 2, QTableWidgetItem(gateway.sim))
            self.table.setItem(row, 3, QTableWidgetItem(gateway.system))

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

    def get_selected_serial_no(self, show_message: bool = True) -> str | None:
        row = self.table.currentRow()

        if row < 0:
            if show_message:
                QMessageBox.warning(self, "Selection", "Please select a gateway.")
            return None

        item = self.table.item(row, 0)
        if item is None:
            if show_message:
                QMessageBox.warning(self, "Selection", "Selected row is invalid.")
            return None

        return item.text()


class GatewayListWindow(GatewayListBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Gateways")
        self.resize(900, 500)

        self.form = None

        self.new_button = QPushButton("New")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        self.new_button.clicked.connect(self.new_gateway)
        self.edit_button.clicked.connect(self.edit_gateway)
        self.delete_button.clicked.connect(self.delete_gateway)
        self.refresh_button.clicked.connect(self.refresh_data)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)

        self.main_layout.addLayout(button_layout)

        self.refresh_data()

    def new_gateway(self) -> None:
        self.form = GatewayFormWindow()
        self.form.show()
        self.form.destroyed.connect(self.refresh_data)

    def edit_gateway(self) -> None:
        serial_no = self.get_selected_serial_no()
        if serial_no is None:
            return

        gateway = get_gateway_by_serial_no(serial_no)

        if gateway is None:
            QMessageBox.warning(self, "Error", "Gateway not found.")
            self.refresh_data()
            return

        self.form = GatewayFormWindow(gateway)
        self.form.show()
        self.form.destroyed.connect(self.refresh_data)

    def delete_gateway(self) -> None:
        serial_no = self.get_selected_serial_no()
        if serial_no is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete Gateway",
            f"Delete gateway '{serial_no}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        try:
            deleted = delete_gateway_by_serial_no(serial_no)

            if not deleted:
                QMessageBox.warning(self, "Error", "Gateway not found.")
                self.refresh_data()
                return

            self.refresh_data()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not delete gateway:\n{e}",
            )


class GatewayListDisplay(GatewayListBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gateways")
        self.table.setRowCount(0)

    def load_for_customer(self, customer_no: int) -> None:
        rows = get_gateway_table_rows_by_customer_no(customer_no)
        self.load_gateways(rows)
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
    window = GatewayListWindow()
    window.show()
    sys.exit(app.exec())