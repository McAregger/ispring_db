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
    QFileDialog,
    QCheckBox,
)

from ispring_db.models import DeviceCalibration
from ispring_db.services.device_repository import get_all_devices
from ispring_db.services.calibration_repository import get_all_calibrations
from ispring_db.services.device_calibration_repository import (
    get_device_calibration_with_device_cal_id,
    save_device_calibration as save_device_calibration_record,
)


class DeviceCalibrationFormWindow(QWidget):
    def __init__(self, device_calibration: DeviceCalibration | None = None, parent=None):
        super().__init__(parent)

        self.device_calibration = device_calibration

        self.setWindowTitle("Device Calibration Form")
        self.resize(650, 320)

        self.device_input = QComboBox()
        self.calibration_input = QComboBox()

        self.status_input = QComboBox()
        self.status_input.addItems([
            "pending",
            "in_progress",
            "passed",
            "failed",
            "recalibration",
        ])

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.filepath_input = QLineEdit()

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.filepath_input)
        file_layout.addWidget(self.browse_button)

        self.total_error_input = QLineEdit()
        self.station_input = QLineEdit()

        self.active_input = QCheckBox("Active calibration")

        form = QFormLayout()
        form.addRow("Device", self.device_input)
        form.addRow("Calibration", self.calibration_input)
        form.addRow("Status", self.status_input)
        form.addRow("Calibration Date", self.date_input)
        form.addRow("TDMS File", file_layout)
        form.addRow("Total Error", self.total_error_input)
        form.addRow("Station", self.station_input)
        form.addRow("", self.active_input)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_device_calibration)
        self.cancel_button.clicked.connect(self.close)

        buttons = QHBoxLayout()
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(buttons)

        self.setLayout(layout)

        self.load_devices()
        self.load_calibrations()

        if self.device_calibration:
            self.load_device_calibration()

    def load_devices(self):
        devices = get_all_devices()

        self.device_input.clear()
        self.device_input.addItem("", None)

        for device in devices:
            self.device_input.addItem(device.mac, device.mac)

    def load_calibrations(self):
        calibrations = get_all_calibrations()

        self.calibration_input.clear()
        self.calibration_input.addItem("", None)

        for calibration in calibrations:
            label = f"{calibration.cal_id} - {calibration.cal_type}"
            self.calibration_input.addItem(label, calibration.cal_id)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select TDMS File",
            "",
            "TDMS Files (*.tdms);;All Files (*.*)"
        )

        if file_path:
            self.filepath_input.setText(file_path)

    def load_device_calibration(self):
        if not self.device_calibration:
            return

        device_index = self.device_input.findData(self.device_calibration.mac)
        self.device_input.setCurrentIndex(device_index if device_index >= 0 else 0)

        calibration_index = self.calibration_input.findData(self.device_calibration.cal_id)
        self.calibration_input.setCurrentIndex(calibration_index if calibration_index >= 0 else 0)

        index = self.status_input.findText(self.device_calibration.device_cal_status or "")
        if index >= 0:
            self.status_input.setCurrentIndex(index)

        if self.device_calibration.device_cal_date:
            value = self.device_calibration.device_cal_date
            self.date_input.setDate(QDate(value.year, value.month, value.day))

        self.filepath_input.setText(self.device_calibration.device_cal_filepath_tdms or "")
        self.total_error_input.setText(str(self.device_calibration.device_cal_total_error or ""))
        self.station_input.setText(self.device_calibration.device_cal_station or "")
        self.active_input.setChecked(bool(self.device_calibration.is_active))

    def save_device_calibration(self):
        if self.device_input.count() == 0:
            QMessageBox.warning(self, "Validation", "No device available.")
            return

        if self.calibration_input.count() == 0:
            QMessageBox.warning(self, "Validation", "No calibration available.")
            return

        mac = self.device_input.currentData()
        cal_id = self.calibration_input.currentData()

        if not mac:
            QMessageBox.warning(self, "Validation", "Please select a device.")
            return

        if cal_id is None:
            QMessageBox.warning(self, "Validation", "Please select a calibration.")
            return

        status = self.status_input.currentText()
        calibration_date = self.date_input.date().toPython()
        filepath_tdms = self.filepath_input.text().strip()
        total_error = self.total_error_input.text().strip()
        station = self.station_input.text().strip()
        is_active = self.active_input.isChecked()

        try:
            if self.device_calibration:
                dc = get_device_calibration_with_device_cal_id(
                    self.device_calibration.device_cal_id
                )
                if dc is None:
                    QMessageBox.warning(
                        self,
                        "Not Found",
                        "The device calibration could not be found.",
                    )
                    return
            else:
                dc = DeviceCalibration()

            dc.mac = mac
            dc.cal_id = cal_id
            dc.device_cal_status = status
            dc.device_cal_date = calibration_date
            dc.device_cal_filepath_tdms = filepath_tdms
            dc.device_cal_total_error = total_error
            dc.device_cal_station = station
            dc.is_active = is_active

            self.device_calibration = save_device_calibration_record(dc)

            QMessageBox.information(self, "Success", "Device calibration saved.")
            self.close()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save device calibration:\n{e}",
            )


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from ispring_db.core.database import create_db_and_tables

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = DeviceCalibrationFormWindow()
    window.show()

    sys.exit(app.exec())