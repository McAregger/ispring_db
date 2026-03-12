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
from ispring_db.models import Device, Customer
from ispring_db.gui.devices.device_form import DeviceFormWindow


class DeviceListWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Devices")
        self.resize(1200, 600)

        self.table = QTableWidget()

        self.table.setColumnCount(10)

        self.table.setHorizontalHeaderLabels(
            [
                "MAC",
                "Customer",
                "Manufacturing Date",
                "DMS",
                "BLE Antenna",
                "Circuit Diagram",
                "Revision",
                "Assembly Plan",
                "Bridge Layout",
                "Batch No",
            ]
        )

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

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
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)

        self.new_button = QPushButton("New")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        self.new_button.clicked.connect(self.new_device)
        self.edit_button.clicked.connect(self.edit_device)
        self.delete_button.clicked.connect(self.delete_device)
        self.refresh_button.clicked.connect(self.load_devices)

        buttons = QHBoxLayout()

        buttons.addWidget(self.new_button)
        buttons.addWidget(self.edit_button)
        buttons.addWidget(self.delete_button)
        buttons.addWidget(self.refresh_button)

        layout = QVBoxLayout()

        layout.addWidget(self.table)
        layout.addLayout(buttons)

        self.setLayout(layout)

        self.load_devices()

    def load_devices(self):

        with get_session() as session:
            statement = (
                select(Device, Customer)
                .join(Customer, Device.customer_no == Customer.customer_no, isouter=True)
            )
            results = session.exec(statement).all()

        self.table.setRowCount(len(results))


        for row, (device, customer) in enumerate(results):

            self.table.setItem(row, 0, QTableWidgetItem(device.mac))

            if customer:
                customer_text = f"{customer.customer_no} - {customer.company}"
            else:
                customer_text = ""

            self.table.setItem(row, 1, QTableWidgetItem(customer_text))
            self.table.setItem(row, 2, QTableWidgetItem(str(device.manufacturing_date or "")))
            self.table.setItem(row, 3, QTableWidgetItem(device.dms or ""))
            self.table.setItem(row, 4, QTableWidgetItem(device.ble_antenna or ""))
            self.table.setItem(row, 5, QTableWidgetItem(device.circuit_diagram_no or ""))
            self.table.setItem(row, 6, QTableWidgetItem(device.revision or ""))
            self.table.setItem(row, 7, QTableWidgetItem(device.assembly_plan or ""))
            self.table.setItem(row, 8, QTableWidgetItem(device.bridge_layout or ""))
            self.table.setItem(row, 9, QTableWidgetItem(device.batch_no or ""))

    def get_selected_mac(self):

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Selection", "Select a device first")
            return None

        return self.table.item(row, 0).text()

    def new_device(self):

        self.form = DeviceFormWindow()
        self.form.show()

    def edit_device(self):

        mac = self.get_selected_mac()

        if not mac:
            return

        with get_session() as session:
            device = session.get(Device, mac)

        self.form = DeviceFormWindow(device)
        self.form.show()

    def delete_device(self):

        mac = self.get_selected_mac()

        if not mac:
            return

        reply = QMessageBox.question(

            self,
            "Delete Device",
            f"Delete device {mac}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        with get_session() as session:

            device = session.get(Device, mac)

            if device:
                session.delete(device)
                session.commit()

        self.load_devices()


if __name__ == "__main__":

    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = DeviceListWindow()
    window.show()

    sys.exit(app.exec())