from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QDateEdit,
    QFileDialog,
    QComboBox,
)


from ispring_db.models import Calibration
from ispring_db.repositories.calibration_repository import save_calibration


class CalibrationFormWindow(QWidget):

    def __init__(self, calibration: Calibration | None = None, parent=None):
        super().__init__(parent)

        self.calibration = calibration

        self.setWindowTitle("Calibration Form")
        self.resize(500, 250)

        self.type_input = QComboBox()
        self.type_input.addItems([
            "TK-NP_Electronic",
            "TK-NP_System",
        ])

        self.min_temp_input = QLineEdit()
        self.max_temp_input = QLineEdit()

        self.cal_def_date_input = QDateEdit()
        self.cal_def_date_input.setCalendarPopup(True)
        self.cal_def_date_input.setDate(QDate.currentDate())

        self.cal_def_file_input = QLineEdit()

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.cal_def_file_input)
        file_layout.addWidget(self.browse_button)

        form = QFormLayout()
        form.addRow("Calibration Type", self.type_input)
        form.addRow("Min Temp", self.min_temp_input)
        form.addRow("Max Temp", self.max_temp_input)
        form.addRow("Cal Def Date", self.cal_def_date_input)
        form.addRow("Cal Def File", file_layout)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_calibration)
        self.cancel_button.clicked.connect(self.close)

        buttons = QHBoxLayout()
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(buttons)

        self.setLayout(layout)

        if self.calibration:
            self.load_calibration()

    def browse_file(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Calibration Definition File",
            "",
            "All Files (*.*);;Text Files (*.txt);;TDMS Files (*.tdms)"
        )

        if file_path:
            self.cal_def_file_input.setText(file_path)

    def load_calibration(self):

        index = self.type_input.findText(self.calibration.cal_type)
        if index >= 0:
            self.type_input.setCurrentIndex(index)

        self.min_temp_input.setText(str(self.calibration.min_temp))
        self.max_temp_input.setText(str(self.calibration.max_temp))
        self.cal_def_date_input.setDate(QDate(self.calibration.cal_def_date))
        self.cal_def_file_input.setText(self.calibration.cal_def_file)

    def save_calibration(self):
        calibration_type = self.type_input.currentText()

        min_temp_text = self.min_temp_input.text().strip()
        if not min_temp_text:
            QMessageBox.warning(self, "Validation", "Min Temp is required.")
            return

        max_temp_text = self.max_temp_input.text().strip()
        if not max_temp_text:
            QMessageBox.warning(self, "Validation", "Max Temp is required.")
            return

        cal_def_file = self.cal_def_file_input.text().strip()
        if not cal_def_file:
            QMessageBox.warning(self, "Validation", "Cal Def File is required.")
            return

        try:
            min_temp = float(min_temp_text)
            max_temp = float(max_temp_text)
        except ValueError:
            QMessageBox.warning(
                self,
                "Validation",
                "Min Temp and Max Temp must be numeric.",
            )
            return

        try:
            calibration = Calibration(
                cal_id=self.calibration.cal_id if self.calibration else None,
                cal_type=calibration_type,
                min_temp=min_temp,
                max_temp=max_temp,
                cal_def_date=self.cal_def_date_input.date().toPython(),
                cal_def_file=cal_def_file,
            )

            self.calibration = save_calibration(calibration)


            QMessageBox.information(self, "Success", "Calibration saved.")
            self.close()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save calibration:\n{e}",
            )

if __name__ == "__main__":

    import sys
    from PySide6.QtWidgets import QApplication
    from ispring_db.core.database import create_db_and_tables

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = CalibrationFormWindow()
    window.show()

    sys.exit(app.exec())