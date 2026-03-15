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
from ispring_db.models import Device, Customer
from ispring_db.gui.devices.device_form import DeviceFormWindow


class DeviceListBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(
            [
                "MAC",
                "Customer",
                "Manufacturing Date",
                "DMS",
                "BLE Antenna",
                "Circuit Diagram No",
                "Revision",
                "Assembly Plan"
                "Bridge Layout",
                "Batch No",
                "Description"
            ]
        )

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.ElideRight)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.Stretch)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.table)
        self.setLayout(self.main_layout)

    def refresh_data(self) -> None:
        with get_session() as session:
            devices = session.exec(select(Device)).all()

        self._fill_table(devices)

    def _fill_table(self, devices: list[Device]) -> None:
        self.table.setRowCount(len(devices))

        with get_session() as session:
            for row, d in enumerate(devices):
                customer_text = ""
                if getattr(d, "customer_no", None) is not None:
                    customer = session.get(Customer, d.customer_no)
                    if customer:
                        customer_text = customer.company or str(customer.customer_no)
                    else:
                        customer_text = str(d.customer_no)

                self.table.setItem(row, 0, QTableWidgetItem(str(getattr(d, "mac", "") or "")))
                self.table.setItem(row, 1, QTableWidgetItem(customer_text))
                self.table.setItem(row, 2, QTableWidgetItem(str(getattr(d, "manufacturing_date", "") or "")))
                self.table.setItem(row, 3, QTableWidgetItem(str(getattr(d, "dms", "") or "")))
                self.table.setItem(row, 4, QTableWidgetItem(str(getattr(d, "ble_antenna", "") or "")))
                self.table.setItem(row, 5, QTableWidgetItem(str(getattr(d, "circuit_diagram_no", "") or "")))
                self.table.setItem(row, 6, QTableWidgetItem(str(getattr(d, "revision", "") or "")))
                self.table.setItem(row, 7, QTableWidgetItem(str(getattr(d, "assembly_plan", "") or "")))
                self.table.setItem(row, 8, QTableWidgetItem(str(getattr(d, "bridge_layout", "") or "")))
                self.table.setItem(row, 9, QTableWidgetItem(str(getattr(d, "batch_no", "") or "")))
                self.table.setItem(row, 9, QTableWidgetItem(str(getattr(d, "description", "") or "")))

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

    def get_selected_device_mac(self, show_message: bool = True) -> str | None:
        row = self.table.currentRow()

        if row < 0:
            if show_message:
                QMessageBox.warning(self, "Selection", "Please select a device.")
            return None

        item = self.table.item(row, 0)
        if item is None:
            if show_message:
                QMessageBox.warning(self, "Selection", "Selected row is invalid.")
            return None

        return item.text()


class DeviceListWindow(DeviceListBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Devices")
        self.resize(1100, 600)

        self.new_button = QPushButton("New")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        self.new_button.clicked.connect(self.new_device)
        self.edit_button.clicked.connect(self.edit_device)
        self.delete_button.clicked.connect(self.delete_device)
        self.refresh_button.clicked.connect(self.refresh_data)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)

        self.main_layout.addLayout(button_layout)

        self.refresh_data()

    def new_device(self) -> None:
        self.form = DeviceFormWindow()
        self.form.show()
        self.form.destroyed.connect(self.refresh_data)

    def edit_device(self) -> None:
        mac = self.get_selected_device_mac()
        if mac is None:
            return

        with get_session() as session:
            device = session.get(Device, mac)

        if device is None:
            QMessageBox.warning(self, "Error", "Device not found.")
            self.refresh_data()
            return

        self.form = DeviceFormWindow(device)
        self.form.show()
        self.form.destroyed.connect(self.refresh_data)

    def delete_device(self) -> None:
        mac = self.get_selected_device_mac()
        if mac is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete Device",
            f"Delete device '{mac}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        try:
            with get_session() as session:
                device = session.get(Device, mac)

                if device is None:
                    QMessageBox.warning(self, "Error", "Device not found.")
                    self.refresh_data()
                    return

                session.delete(device)
                session.commit()

            self.refresh_data()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not delete device:\n{e}",
            )


class DeviceListDisplay(DeviceListBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Devices")
        self.table.setRowCount(0)

    def load_for_customer(self, customer_no: int) -> None:
        with get_session() as session:
            devices = session.exec(
                select(Device).where(Device.customer_no == customer_no)
            ).all()

        self._fill_table(devices)

    def clear_data(self) -> None:
        self.table.setRowCount(0)
        self.table.clearSelection()


if __name__ == "__main__":
    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)
    window = DeviceListWindow()
    window.show()
    sys.exit(app.exec())