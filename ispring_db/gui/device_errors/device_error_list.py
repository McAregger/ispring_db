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
from PySide6.QtCore import QDate
from datetime import date
from ispring_db.core.database import create_db_and_tables
from ispring_db.models import DeviceError
from ispring_db.gui.device_errors.device_error_form import DeviceErrorFormWindow
from ispring_db.services.device_error_repository import (
    get_all_device_errors,
    get_device_errors_by_customer_no,
    get_device_error_by_device_error_id,
    delete_device_error_by_id,
)


class DeviceErrorListBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Device Errors")
        self.resize(1400, 600)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setSortingEnabled(True)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Device",
                "Error ID",
                "Component",
                "Error Cause",
                "Error Date",
                "Description",
            ]
        )

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self.refresh_data()

    def refresh_data(self):
        device_errors = get_all_device_errors()
        self.load_device_errors(device_errors)
        self.table.resizeRowsToContents()

    def load_device_errors(self, device_errors: list[tuple[DeviceError, object, object]]):
        self.table.setRowCount(len(device_errors))

        for row, (device_error, device, error) in enumerate(device_errors):
            self.table.setItem(row, 0, QTableWidgetItem(str(device_error.device_error_id)))
            self.table.setItem(row, 1, QTableWidgetItem(device.mac))
            self.table.setItem(row, 2, QTableWidgetItem(str(error.error_id)))
            self.table.setItem(row, 3, QTableWidgetItem(error.component or ""))
            self.table.setItem(row, 4, QTableWidgetItem(error.error_cause or ""))

            # Datum Konfigurieren
            value = getattr(device_error, "device_error_date", None)

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

            self.table.setItem(row, 5, QTableWidgetItem(date_string or ""))
            self.table.setItem(row, 6, QTableWidgetItem(device_error.device_error_description or ""))

    def get_selected_device_error_id(self):
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Selection", "Select a device error first")
            return None

        return int(self.table.item(row, 0).text())

    def new_device_error(self):
        self.form = DeviceErrorFormWindow()
        self.form.show()

    def edit_device_error(self):
        device_error_id = self.get_selected_device_error_id()

        if device_error_id is None:
            return

        device_error = get_device_error_by_device_error_id(device_error_id)

        if device_error is None:
            QMessageBox.warning(self, "Error", "Device error not found")
            return

        self.form = DeviceErrorFormWindow(device_error)
        self.form.show()

    def delete_device_error(self):
        device_error_id = self.get_selected_device_error_id()

        if device_error_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete Device Error",
            f"Delete device error {device_error_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        deleted = delete_device_error_by_id(device_error_id)

        if not deleted:
            QMessageBox.warning(self, "Error", "Device error could not be deleted")
            return

        self.refresh_data()

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


class DeviceErrorListWindow(DeviceErrorListBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.new_button = QPushButton("New")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        self.new_button.clicked.connect(self.new_device_error)
        self.edit_button.clicked.connect(self.edit_device_error)
        self.delete_button.clicked.connect(self.delete_device_error)
        self.refresh_button.clicked.connect(self.refresh_data)

        buttons = QHBoxLayout()
        buttons.addWidget(self.new_button)
        buttons.addWidget(self.edit_button)
        buttons.addWidget(self.delete_button)
        buttons.addWidget(self.refresh_button)
        self.layout.addLayout(buttons)


class DeviceErrorListDisplay(DeviceErrorListBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Device Errors")
        self.table.setRowCount(0)

    def load_for_customer(self, customer_no: int) -> None:
        device_errors = get_device_errors_by_customer_no(customer_no)
        self.load_device_errors(device_errors)




if __name__ == "__main__":
    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = DeviceErrorListWindow()
    window.show()

    sys.exit(app.exec())