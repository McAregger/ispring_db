from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
    QDateEdit,
)

from sqlmodel import select

from ispring_db.core.database import get_session
from ispring_db.models import DeviceError, Device, Error


class DeviceErrorFormWindow(QWidget):

    def __init__(self, device_error: DeviceError | None = None, parent=None):
        super().__init__(parent)

        self.device_error = device_error

        self.setWindowTitle("Device Error Form")
        self.resize(650, 250)

        self.device_input = QComboBox()
        self.load_devices()

        self.error_input = QComboBox()
        self.load_errors()

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd.MM.yyyy")
        self.date_input.setDate(QDate.currentDate())

        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(80)

        form = QFormLayout()
        form.addRow("Device", self.device_input)
        form.addRow("Error", self.error_input)
        form.addRow("Error Date", self.date_input)
        form.addRow("Description", self.description_input)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_device_error)
        self.cancel_button.clicked.connect(self.close)

        buttons = QHBoxLayout()
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(buttons)

        self.setLayout(layout)

        if self.device_error:
            self.load_device_error()

    def load_devices(self):

        with get_session() as session:
            devices = session.exec(select(Device)).all()

        self.device_input.clear()
        self.device_map = {}

        for d in devices:
            label = d.mac
            self.device_input.addItem(label)
            self.device_map[label] = d.mac

    def load_errors(self):

        with get_session() as session:
            errors = session.exec(select(Error)).all()

        self.error_input.clear()
        self.error_map = {}

        severity_map = {
            1: "low",
            2: "medium",
            3: "high",
            4: "critical",
        }

        for e in errors:
            severity_text = severity_map.get(e.error_severity, str(e.error_severity))
            label = f"{e.error_id} - {e.component} - {e.error_cause} - {severity_text}"
            self.error_input.addItem(label)
            self.error_map[label] = e.error_id

    def load_device_error(self):

        for i in range(self.device_input.count()):
            label = self.device_input.itemText(i)
            if self.device_map.get(label) == self.device_error.mac:
                self.device_input.setCurrentIndex(i)
                break

        for i in range(self.error_input.count()):
            label = self.error_input.itemText(i)
            if self.error_map.get(label) == self.device_error.error_id:
                self.error_input.setCurrentIndex(i)
                break

        if self.device_error.device_error_date:
            self.date_input.setDate(QDate(self.device_error.device_error_date))

        self.description_input.setPlainText(self.device_error.device_error_description or "")

    def save_device_error(self):

        if self.device_input.count() == 0:
            QMessageBox.warning(self, "Validation", "No device available.")
            return

        if self.error_input.count() == 0:
            QMessageBox.warning(self, "Validation", "No error available.")
            return

        device_label = self.device_input.currentText()
        error_label = self.error_input.currentText()

        mac = self.device_map.get(device_label)
        error_id = self.error_map.get(error_label)

        device_error_date = self.date_input.date().toPython()
        device_error_description = self.description_input.toPlainText().strip()

        if mac is None:
            QMessageBox.warning(self, "Validation", "Device is required.")
            return

        if error_id is None:
            QMessageBox.warning(self, "Validation", "Error is required.")
            return

        try:

            with get_session() as session:

                if self.device_error:
                    de = session.get(DeviceError, self.device_error.device_error_id)
                else:
                    de = DeviceError()

                de.mac = mac
                de.error_id = error_id
                de.device_error_date = device_error_date
                de.device_error_description = device_error_description

                if not self.device_error:
                    session.add(de)

                session.commit()

            QMessageBox.information(self, "Success", "Device error saved.")
            self.close()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save device error:\n{e}",
            )


if __name__ == "__main__":

    import sys
    from PySide6.QtWidgets import QApplication
    from ispring_db.core.database import create_db_and_tables

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = DeviceErrorFormWindow()
    window.show()

    sys.exit(app.exec())