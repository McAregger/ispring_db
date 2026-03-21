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
from ispring_db.models import DeviceCalibration, Device, Calibration
from ispring_db.gui.device_calibrations.device_calibration_form import DeviceCalibrationFormWindow


class DeviceCalibrationListWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Device Calibrations")
        self.resize(1500, 600)

        self.table = QTableWidget()

        self.table.setColumnCount(9)

        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Device",
                "Calibration",
                "Status",
                "Active",
                "Calibration Date",
                "TDMS File",
                "Total Error",
                "Station",
            ]
        )

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)

        self.new_button = QPushButton("New")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        self.new_button.clicked.connect(self.new_device_calibration)
        self.edit_button.clicked.connect(self.edit_device_calibration)
        self.delete_button.clicked.connect(self.delete_device_calibration)
        self.refresh_button.clicked.connect(self.load_device_calibrations)

        buttons = QHBoxLayout()
        buttons.addWidget(self.new_button)
        buttons.addWidget(self.edit_button)
        buttons.addWidget(self.delete_button)
        buttons.addWidget(self.refresh_button)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(buttons)

        self.setLayout(layout)

        self.load_device_calibrations()

    def shorten_left(self, text: str, max_length: int = 50) -> str:
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return "..." + text[-max_length:]

    def load_device_calibrations(self):
        with get_session() as session:
            statement = (
                select(DeviceCalibration, Device, Calibration)
                .join(Device, DeviceCalibration.mac == Device.mac)
                .join(Calibration, DeviceCalibration.cal_id == Calibration.cal_id)
            )
            results = session.exec(statement).all()



        self.table.setRowCount(len(results))

        for row, (dc, device, calibration) in enumerate(results):

            calibration_text = f"{calibration.cal_id} - {calibration.cal_type}"
            filepath_display = self.shorten_left(dc.device_cal_filepath_tdms, 50)

            self.table.setItem(row, 0, QTableWidgetItem(str(dc.device_cal_id)))
            self.table.setItem(row, 1, QTableWidgetItem(device.mac))
            self.table.setItem(row, 2, QTableWidgetItem(calibration_text))
            self.table.setItem(row, 3, QTableWidgetItem(dc.device_cal_status))
            self.table.setItem(row, 4, QTableWidgetItem("Yes" if dc.is_active else "No"))
            self.table.setItem(row, 5, QTableWidgetItem(str(dc.device_cal_date)))

            file_item = QTableWidgetItem(filepath_display)
            file_item.setToolTip(dc.device_cal_filepath_tdms)
            self.table.setItem(row, 6, file_item)

            self.table.setItem(row, 7, QTableWidgetItem(dc.device_cal_total_error))
            self.table.setItem(row, 8, QTableWidgetItem(dc.device_cal_station))

    def get_selected_device_cal_id(self):

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Selection", "Select a device calibration first")
            return None

        return int(self.table.item(row, 0).text())

    def new_device_calibration(self):

        self.form = DeviceCalibrationFormWindow()
        self.form.show()

    def edit_device_calibration(self):

        device_cal_id = self.get_selected_device_cal_id()

        if device_cal_id is None:
            return

        with get_session() as session:
            device_calibration = session.get(DeviceCalibration, device_cal_id)

        self.form = DeviceCalibrationFormWindow(device_calibration)
        self.form.show()

    def delete_device_calibration(self):

        device_cal_id = self.get_selected_device_cal_id()

        if device_cal_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete Device Calibration",
            f"Delete device calibration {device_cal_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        with get_session() as session:

            device_calibration = session.get(DeviceCalibration, device_cal_id)

            if device_calibration:
                session.delete(device_calibration)
                session.commit()

        self.load_device_calibrations()

    def load_for_customer(self, customer_no: int) -> list[DeviceCalibration]:
        with get_session() as session:
            statement = (
                select(DeviceCalibration)
                .join(Device, DeviceCalibration.mac == Device.mac)
                .where(Device.customer_no == customer_no)
            )


            return list(session.exec(statement).all())




if __name__ == "__main__":

    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = DeviceCalibrationListWindow()
    window.show()

    sys.exit(app.exec())