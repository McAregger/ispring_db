from __future__ import annotations
from datetime import date
from PySide6.QtCore import Qt, QTimer, QDate
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
from ispring_db.models import Device
from ispring_db.gui.devices.device_form import DeviceFormWindow
from ispring_db.services.device_repository import (
    get_all_devices,
    get_devices_by_customer_no,
    delete_device_by_mac,
    get_device_by_mac,
    get_device_dependencies_count,
)
from ispring_db.services.customer_repository import get_customer_by_customer_no


class DeviceListBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setSortingEnabled(True)

        self.table.setHorizontalHeaderLabels(
            [
                "MAC",
                "Customer",
                "Manufacturing Date",
                "DMS",
                "BLE Antenna",
                "Circuit Diagram No",
                "Revision",
                "Assembly Plan",
                "Bridge Layout",
                "Batch No",
                "Description",
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

        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

        self.table.resizeColumnsToContents()

        min_widths = [150, 180, 140, 130, 120, 150, 90, 130, 130, 100, 200]

        for col, min_w in enumerate(min_widths):
            if self.table.columnWidth(col) < min_w:
                self.table.setColumnWidth(col, min_w)

    def refresh_data(self) -> None:

        devices = get_all_devices()
        self.load_devices(devices)
        QTimer.singleShot(0, self.apply_resize)

    def load_devices(self, devices: list[Device]) -> None:
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(devices))

        for row, device in enumerate(devices):
            customer_text = ""
            date_string = ""
            if getattr(device, "customer_no", None) is not None:
                customer = get_customer_by_customer_no(device.customer_no)
                if customer:
                    customer_text = customer.company or str(customer.customer_no)
                else:
                    customer_text = str(device.customer_no)

                # Datum Konfigurieren
                value = getattr(device, "manufacturing_date", None)
                if value:
                    if isinstance(value, str):
                        qdate = QDate.fromString(value, "yyyy-MM-dd")
                        date_string = qdate.toString("dd.MM.yyyy") if qdate.isValid() else value
                    elif isinstance(value, date):
                        date_string = value.strftime("%d.%m.%Y")
                    else:
                        text = str(value)
                        date_string = value
                else:
                    date_string = ""


            self.table.setItem(row, 0, QTableWidgetItem(str(getattr(device, "mac", "") or "")))
            self.table.setItem(row, 1, QTableWidgetItem(customer_text))
            self.table.setItem(row, 2, QTableWidgetItem(date_string))
            self.table.setItem(row, 3, QTableWidgetItem(str(getattr(device, "dms", "") or "")))
            self.table.setItem(row, 4, QTableWidgetItem(str(getattr(device, "ble_antenna", "") or "")))
            self.table.setItem(row, 5, QTableWidgetItem(str(getattr(device, "circuit_diagram_no", "") or "")))
            self.table.setItem(row, 6, QTableWidgetItem(str(getattr(device, "revision", "") or "")))
            self.table.setItem(row, 7, QTableWidgetItem(str(getattr(device, "assembly_plan", "") or "")))
            self.table.setItem(row, 8, QTableWidgetItem(str(getattr(device, "bridge_layout", "") or "")))
            self.table.setItem(row, 9, QTableWidgetItem(str(getattr(device, "batch_no", "") or "")))
            self.table.setItem(row, 10, QTableWidgetItem(str(getattr(device, "description", "") or "")))

        self.table.clearSelection()
        self.table.setSortingEnabled(True)

        QTimer.singleShot(0, self.apply_resize)

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

        self.form = None

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

        device = get_device_by_mac(mac)

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

        dependencies = get_device_dependencies_count(mac)

        warning_lines = []

        if dependencies["logbooks"] > 0:
            count = dependencies["logbooks"]
            warning_lines.append(
                f"- {count} Logbook-Eintrag{'e' if count != 1 else ''}"
            )

        if dependencies["device_calibrations"] > 0:
            count = dependencies["device_calibrations"]
            warning_lines.append(
                f"- {count} Device-Calibration-Eintrag{'e' if count != 1 else ''}"
            )

        if dependencies["device_errors"] > 0:
            count = dependencies["device_errors"]
            warning_lines.append(
                f"- {count} Device-Error-Eintrag{'e' if count != 1 else ''}"
            )

        if warning_lines:
            message = (
                f"Device '{mac}' wird gelöscht.\n\n"
                "Dabei werden auch folgende verknüpfte Einträge gelöscht:\n"
                f"{chr(10).join(warning_lines)}\n\n"
                "Möchtest du fortfahren?"
            )
        else:
            message = f"Device '{mac}' löschen?"

        reply = QMessageBox.question(
            self,
            "Device löschen",
            message,
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        try:
            success = delete_device_by_mac(mac)

            if not success:
                QMessageBox.warning(self, "Error", "Device not found.")
                self.refresh_data()
                return

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

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, self.apply_resize)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.apply_resize)

    def apply_resize(self) -> None:
        header = self.table.horizontalHeader()

        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

        self.table.resizeColumnsToContents()

        # nur Description strecken, wenn gewünscht
        header.setSectionResizeMode(10, QHeaderView.Stretch)

        min_widths = [150, 140, 140, 130, 120, 150, 90, 130, 130, 100, 180]

        for col, min_w in enumerate(min_widths):
            if self.table.columnWidth(col) < min_w:
                self.table.setColumnWidth(col, min_w)

    def load_for_customer(self, customer_no: int) -> None:
        devices = get_devices_by_customer_no(customer_no)
        self.load_devices(devices)
        QTimer.singleShot(50, self.apply_resize)

    def clear_data(self) -> None:
        self.table.setRowCount(0)
        self.table.clearContents()
        self.table.clearSelection()
        QTimer.singleShot(50, self.apply_resize)


if __name__ == "__main__":
    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)
    window = DeviceListWindow()
    window.show()
    sys.exit(app.exec())