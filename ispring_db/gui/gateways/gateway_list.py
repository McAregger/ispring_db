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

from sqlmodel import select

from ispring_db.core.database import get_session, create_db_and_tables
from ispring_db.models import Gateway, Customer
from ispring_db.gui.gateways.gateway_form import GatewayFormWindow


class GatewayListBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
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

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)   # Serial No
        header.setSectionResizeMode(1, QHeaderView.Stretch)            # Customer
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)   # SIM
        header.setSectionResizeMode(3, QHeaderView.Stretch)            # System

        min_widths = [140, 180, 120, 180]

        for col, min_w in enumerate(min_widths):
            if self.table.columnWidth(col) < min_w:
                self.table.setColumnWidth(col, min_w)

    def refresh_data(self) -> None:
        with get_session() as session:
            gateways = session.exec(select(Gateway)).all()

        self.load_gateways(gateways)
        QTimer.singleShot(0, self.apply_resize)

    def load_gateways(self, gateways: list[Gateway]) -> None:
        self.table.setRowCount(len(gateways))

        with get_session() as session:
            for row, gateway in enumerate(gateways):
                customer_text = ""
                if getattr(gateway, "customer_no", None) is not None:
                    customer = session.get(Customer, gateway.customer_no)
                    if customer:
                        customer_text = customer.company or str(customer.customer_no)
                    else:
                        customer_text = str(gateway.customer_no)

                self.table.setItem(row, 0, QTableWidgetItem(str(getattr(gateway, "serial_no", "") or "")))
                self.table.setItem(row, 1, QTableWidgetItem(customer_text))
                self.table.setItem(row, 2, QTableWidgetItem(str(getattr(gateway, "sim", "") or "")))
                self.table.setItem(row, 3, QTableWidgetItem(str(getattr(gateway, "system", "") or "")))

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

        with get_session() as session:
            gateway = session.get(Gateway, serial_no)

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
            with get_session() as session:
                gateway = session.get(Gateway, serial_no)

                if gateway is None:
                    QMessageBox.warning(self, "Error", "Gateway not found.")
                    self.refresh_data()
                    return

                session.delete(gateway)
                session.commit()

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
        with get_session() as session:
            gateways = session.exec(
                select(Gateway).where(Gateway.customer_no == customer_no)
            ).all()

        self.load_gateways(gateways)
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
    window = GatewayListWindow()
    window.show()
    sys.exit(app.exec())