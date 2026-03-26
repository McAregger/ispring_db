import re
from datetime import date

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
    QApplication,
)

from ispring_db.core.database import create_db_and_tables
from ispring_db.models import Device
from ispring_db.services.customer_repository import get_all_customers
from ispring_db.services.device_repository import get_device_by_mac, save_device


class DeviceFormWindow(QWidget):
    def __init__(self, device: Device | None = None, parent=None):
        super().__init__(parent)

        self.device = device

        self.setWindowTitle("Device Form")
        self.resize(300, 400)

        self.mac_input = QLineEdit()
        self.mac_input.textChanged.connect(self.on_mac_changed)

        self.customer_input = QComboBox()

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.dms_input = QComboBox()
        self.dms_input.addItems([
            "",
            "FRAB-5-350-11",
            "GFLAB-3-350-70",
            "GFLAB-6-350-50",
        ])

        self.ble_ant_input = QComboBox()
        self.ble_ant_input.addItems([
            "",
            "internal",
            "external",
        ])

        self.diagram_input = QLineEdit()
        self.revision_input = QLineEdit()
        self.assembly_plan_input = QLineEdit()

        self.bridge_layout_input = QComboBox()
        self.bridge_layout_input.addItems([
            "Quarter Bridge",
            "Half Bridge",
            "Full Bridge",
        ])

        self.batch_input = QLineEdit()

        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(80)

        form = QFormLayout()
        form.addRow("MAC", self.mac_input)
        form.addRow("Customer", self.customer_input)
        form.addRow("Manufacturing Date", self.date_input)
        form.addRow("DMS", self.dms_input)
        form.addRow("BLE Antenna", self.ble_ant_input)
        form.addRow("Circuit Diagram No", self.diagram_input)
        form.addRow("Revision", self.revision_input)
        form.addRow("Assembly Plan", self.assembly_plan_input)
        form.addRow("Bridge Layout", self.bridge_layout_input)
        form.addRow("Batch No", self.batch_input)
        form.addRow("Description", self.description_input)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_device)
        self.cancel_button.clicked.connect(self.close)

        buttons = QHBoxLayout()
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(buttons)
        self.setLayout(layout)

        self.load_customers()

        if self.device:
            self.load_device()
            self.mac_input.setReadOnly(True)

    def load_customers(self):
        customers = get_all_customers()
        self.customer_input.clear()

        self.customer_input.addItem("", None)

        for customer in customers:
            label = f"{customer.customer_no} - {customer.company}"
            self.customer_input.addItem(label, customer.customer_no)

        if self.device is None:
            self.customer_input.setCurrentIndex(0)
        else:
            index = self.customer_input.findData(self.device.customer_no)
            self.customer_input.setCurrentIndex(index if index >= 0 else 0)

    def load_device(self):
        if not self.device:
            return

        self.mac_input.setText(self.device.mac or "")

        if self.device.manufacturing_date:
            value = self.device.manufacturing_date

            if isinstance(value, str):
                qdate = QDate.fromString(value, "yyyy-MM-dd")
            elif isinstance(value, date):
                qdate = QDate(value.year, value.month, value.day)
            else:
                qdate = QDate()

            if qdate.isValid():
                self.date_input.setDate(qdate)

        if self.device.dms:
            index = self.dms_input.findText(self.device.dms)
            if index >= 0:
                self.dms_input.setCurrentIndex(index)

        if self.device.ble_antenna:
            index = self.ble_ant_input.findText(self.device.ble_antenna)
            if index >= 0:
                self.ble_ant_input.setCurrentIndex(index)

        if self.device.bridge_layout:
            index = self.bridge_layout_input.findText(self.device.bridge_layout)
            if index >= 0:
                self.bridge_layout_input.setCurrentIndex(index)

        self.diagram_input.setText(self.device.circuit_diagram_no or "")
        self.revision_input.setText(self.device.revision or "")
        self.assembly_plan_input.setText(self.device.assembly_plan or "")
        self.batch_input.setText(self.device.batch_no or "")
        self.description_input.setPlainText(self.device.description or "")

    def format_mac(self, text: str) -> str:
        text = text.upper().replace(":", "").replace("-", "")

        if len(text) > 12:
            text = text[:12]

        return ":".join(text[i:i + 2] for i in range(0, len(text), 2))

    def on_mac_changed(self, text):
        formatted = self.format_mac(text)

        if formatted != text:
            self.mac_input.blockSignals(True)
            self.mac_input.setText(formatted)
            self.mac_input.blockSignals(False)

    def save_device(self):
        mac = self.mac_input.text().strip()

        if not mac:
            QMessageBox.warning(self, "Validation", "MAC is required.")
            return

        mac_pattern = r"^([0-9A-F]{2}:){5}[0-9A-F]{2}$"

        if not re.match(mac_pattern, mac):
            QMessageBox.warning(
                self,
                "Invalid MAC",
                "MAC address must be in format AA:BB:CC:DD:EE:FF",
            )
            return

        try:
            if self.device:
                if mac != self.device.mac:
                    QMessageBox.warning(
                        self,
                        "Invalid Change",
                        "The MAC address is the primary key and cannot be changed.",
                    )
                    return

                device = Device(
                    mac=self.device.mac,
                    customer_no=self.customer_input.currentData(),
                    manufacturing_date=self.date_input.date().toPython(),
                    dms=self.dms_input.currentText(),
                    ble_antenna=self.ble_ant_input.currentText(),
                    circuit_diagram_no=self.diagram_input.text().strip(),
                    revision=self.revision_input.text().strip(),
                    assembly_plan=self.assembly_plan_input.text().strip(),
                    bridge_layout=self.bridge_layout_input.currentText(),
                    batch_no=self.batch_input.text().strip(),
                    description=self.description_input.toPlainText().strip(),
                )
            else:
                existing = get_device_by_mac(mac)
                if existing:
                    QMessageBox.warning(
                        self,
                        "Duplicate MAC",
                        "A device with this MAC address already exists.",
                    )
                    return

                device = Device(
                    mac=mac,
                    customer_no=self.customer_input.currentData(),
                    manufacturing_date=self.date_input.date().toPython(),
                    dms=self.dms_input.currentText(),
                    ble_antenna=self.ble_ant_input.currentText(),
                    circuit_diagram_no=self.diagram_input.text().strip(),
                    revision=self.revision_input.text().strip(),
                    assembly_plan=self.assembly_plan_input.text().strip(),
                    bridge_layout=self.bridge_layout_input.currentText(),
                    batch_no=self.batch_input.text().strip(),
                    description=self.description_input.toPlainText().strip(),
                )

            save_device(device)

            QMessageBox.information(self, "Success", "Device saved.")
            self.close()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save device:\n{e}",
            )


if __name__ == "__main__":
    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = DeviceFormWindow()
    window.show()

    sys.exit(app.exec())