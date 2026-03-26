from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QComboBox,
    QPlainTextEdit,
)


from ispring_db.models import Error
from ispring_db.services.error_repository import save_error


class ErrorFormWindow(QWidget):

    def __init__(self, error: Error | None = None, parent=None):
        super().__init__(parent)

        self.error = error

        self.setWindowTitle("Error Form")
        self.resize(350, 220)

        self.component_input = QComboBox()
        self.component_input.addItems([
            "DMS",
            "Bridge Resistors",
            "OpAmp",
            "MCU",
            "Antenna",
            "Other",
        ])

        self.error_cause_input = QComboBox()
        self.error_cause_input.addItems([
            "Over Temperature",
            "Under Temperature",
            "Mechanical Overload",
            "Mechanical Shock",
            "Electrical Overload",
            "Firmware Failure",
            "Other",
        ])

        self.error_severity_input = QComboBox()
        self.error_severity_input.addItems([
            "low",
            "medium",
            "high",
            "critical",
        ])

        self.repairability_input = QComboBox()
        self.repairability_input.addItems([
            "True",
            "False",
        ])

        form = QFormLayout()
        form.addRow("Component", self.component_input)
        form.addRow("Error Cause", self.error_cause_input)
        form.addRow("Error Severity", self.error_severity_input)
        form.addRow("Repairability", self.repairability_input)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_error)
        self.cancel_button.clicked.connect(self.close)

        buttons = QHBoxLayout()
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(buttons)

        self.setLayout(layout)

        if self.error:
            self.load_error()

    def load_error(self):

        component_index = self.component_input.findText(self.error.component)
        if component_index >= 0:
            self.component_input.setCurrentIndex(component_index)

        index = self.error_cause_input.findText(self.error.error_cause)
        if index >= 0:
            self.error_cause_input.setCurrentIndex(index)

        severity_map = {
            1: "low",
            2: "medium",
            3: "high",
            4: "critical",
        }

        severity_text = severity_map.get(self.error.error_severity, "low")
        self.error_severity_input.setCurrentText(severity_text)

        if self.error.repairability:
            self.repairability_input.setCurrentText("True")
        else:
            self.repairability_input.setCurrentText("False")

    def save_error(self):
        component = self.component_input.currentText().strip()
        error_cause = self.error_cause_input.currentText().strip()

        severity_map = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }

        severity_text = self.error_severity_input.currentText()
        error_severity = severity_map[severity_text]
        repairability = self.repairability_input.currentText() == "True"

        if not component:
            QMessageBox.warning(self, "Validation", "Component is required.")
            return

        if not error_cause:
            QMessageBox.warning(self, "Validation", "Error Cause is required.")
            return

        try:
            if self.error is None:
                self.error = Error(
                    component=component,
                    error_cause=error_cause,
                    error_severity=error_severity,
                    repairability=repairability,
                )
            else:
                self.error.component = component
                self.error.error_cause = error_cause
                self.error.error_severity = error_severity
                self.error.repairability = repairability

            save_error(self.error)

            QMessageBox.information(self, "Success", "Error saved.")
            self.close()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save error:\n{e}",
            )


if __name__ == "__main__":

    import sys
    from PySide6.QtWidgets import QApplication
    from ispring_db.core.database import create_db_and_tables

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = ErrorFormWindow()
    window.show()

    sys.exit(app.exec())