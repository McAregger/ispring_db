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

from sqlmodel import select

from ispring_db.core.database import get_session
from ispring_db.models import DeviceCalibration, Device, Calibration


class DeviceCalibrationFormWindow(QWidget):

    def __init__(self, device_calibration: DeviceCalibration | None = None, parent=None):
        super().__init__(parent)

        self.device_calibration = device_calibration

        self.setWindowTitle("Device Calibration Form")
        self.resize(650, 320)

        self.device_input = QComboBox()
        self.load_devices()

        self.calibration_input = QComboBox()
        self.load_calibrations()

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

        if self.device_calibration:
            self.load_device_calibration()

    def load_devices(self):

        with get_session() as session:
            devices = session.exec(select(Device)).all()

        self.device_input.clear()
        self.device_map = {}

        for d in devices:
            label = d.mac
            self.device_input.addItem(label)
            self.device_map[label] = d.mac

    def load_calibrations(self):

        with get_session() as session:
            calibrations = session.exec(select(Calibration)).all()

        self.calibration_input.clear()
        self.calibration_map = {}

        for c in calibrations:
            label = f"{c.cal_id} - {c.cal_type}"
            self.calibration_input.addItem(label)
            self.calibration_map[label] = c.cal_id

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

        for i in range(self.calibration_input.count()):
            label = self.calibration_input.itemText(i)
            if self.calibration_map.get(label) == self.device_calibration.cal_id:
                self.calibration_input.setCurrentIndex(i)
                break

        for i in range(self.calibration_input.count()):
            label = self.calibration_input.itemText(i)
            if self.calibration_map.get(label) == self.device_calibration.device_cal_id:
                self.calibration_input.setCurrentIndex(i)
                break

        index = self.status_input.findText(self.device_calibration.device_cal_status)
        if index >= 0:
            self.status_input.setCurrentIndex(index)

        if self.device_calibration.device_cal_date:
            self.date_input.setDate(QDate(self.device_calibration.device_cal_date))

        self.filepath_input.setText(self.device_calibration.device_cal_filepath_tdms)
        self.total_error_input.setText(self.device_calibration.device_cal_total_error)
        self.station_input.setText(self.device_calibration.device_cal_station)
        self.active_input.setChecked(self.device_calibration.is_active)

    def save_device_calibration(self):

        if self.device_input.count() == 0:
            QMessageBox.warning(self, "Validation", "No device available.")
            return

        if self.calibration_input.count() == 0:
            QMessageBox.warning(self, "Validation", "No calibration available.")
            return

        device_label = self.device_input.currentText()
        calibration_label = self.calibration_input.currentText()

        mac = self.device_map.get(device_label)
        cal_id = self.calibration_map.get(calibration_label)

        status = self.status_input.currentText()
        calibration_date = self.date_input.date().toPython()
        filepath_tdms = self.filepath_input.text().strip()
        total_error = self.total_error_input.text().strip()
        station = self.station_input.text().strip()
        is_active = self.active_input.isChecked()

        # if not filepath_tdms:
        #     QMessageBox.warning(self, "Validation", "TDMS file is required.")
        #     return
        #
        # if not total_error:
        #     QMessageBox.warning(self, "Validation", "Total Error is required.")
        #     return
        #
        # if not station:
        #     QMessageBox.warning(self, "Validation", "Station is required.")
        #     return
        #
        # if is_active and status not in ["passed", "recalibration"]:
        #     QMessageBox.warning(
        #         self,
        #         "Validation",
        #         "Only a successful calibration can be set active.",
        #     )
        #     return

        try:

            with get_session() as session:

                if self.device_calibration:
                    dc = session.get(DeviceCalibration, self.device_calibration.device_cal_id)
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

                if is_active:
                    statement = select(DeviceCalibration).where(
                        DeviceCalibration.mac == mac,
                        DeviceCalibration.is_active == True,
                    )
                    active_rows = session.exec(statement).all()

                    for row in active_rows:
                        if self.device_calibration and row.device_cal_id == self.device_calibration.device_cal_id:
                            continue
                        row.is_active = False

                if not self.device_calibration:
                    session.add(dc)

                session.commit()

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