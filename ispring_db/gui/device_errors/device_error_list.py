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
from ispring_db.models import DeviceError, Device, Error
from ispring_db.gui.device_errors.device_error_form import DeviceErrorFormWindow


class DeviceErrorListWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Device Errors")
        self.resize(1400, 600)

        self.table = QTableWidget()

        self.table.setColumnCount(7)
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

        self.new_button = QPushButton("New")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        self.new_button.clicked.connect(self.new_device_error)
        self.edit_button.clicked.connect(self.edit_device_error)
        self.delete_button.clicked.connect(self.delete_device_error)
        self.refresh_button.clicked.connect(self.load_device_errors)

        buttons = QHBoxLayout()
        buttons.addWidget(self.new_button)
        buttons.addWidget(self.edit_button)
        buttons.addWidget(self.delete_button)
        buttons.addWidget(self.refresh_button)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(buttons)

        self.setLayout(layout)

        self.load_device_errors()

    def load_device_errors(self):

        with get_session() as session:
            statement = (
                select(DeviceError, Device, Error)
                .join(Device, DeviceError.mac == Device.mac)
                .join(Error, DeviceError.error_id == Error.error_id)
            )
            results = session.exec(statement).all()

        self.table.setRowCount(len(results))

        for row, (device_error, device, error) in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(str(device_error.device_error_id)))
            self.table.setItem(row, 1, QTableWidgetItem(device.mac))
            self.table.setItem(row, 2, QTableWidgetItem(str(error.error_id)))
            self.table.setItem(row, 3, QTableWidgetItem(error.component or ""))
            self.table.setItem(row, 4, QTableWidgetItem(error.error_cause or ""))
            self.table.setItem(row, 5, QTableWidgetItem(str(device_error.device_error_date or "")))
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

        with get_session() as session:
            device_error = session.get(DeviceError, device_error_id)

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

        with get_session() as session:
            device_error = session.get(DeviceError, device_error_id)

            if device_error:
                session.delete(device_error)
                session.commit()

        self.load_device_errors()


if __name__ == "__main__":

    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = DeviceErrorListWindow()
    window.show()

    sys.exit(app.exec())