from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from ispring_db.models.license import License
from ispring_db.repositories.license_repository import (
    save_license,
    get_license_by_id,
)
from ispring_db.gui.utils.db_error_handler import handle_db_error


class LicenseFormWindow(QWidget):

    def __init__(self, license: License | None = None, parent=None):
        super().__init__(parent)

        self.license = license

        self.setWindowTitle("License Form")
        self.resize(300, 180)

        self.license_name_input = QLineEdit()
        self.license_release_input = QLineEdit()

        form = QFormLayout()
        form.addRow("License Name", self.license_name_input)
        form.addRow("License Release", self.license_release_input)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_license)
        self.cancel_button.clicked.connect(self.close)

        buttons = QHBoxLayout()
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(buttons)

        self.setLayout(layout)

        if self.license:
            self.load_license()

    def load_license(self) -> None:
        self.license_name_input.setText(self.license.license_name or "")
        self.license_release_input.setText(self.license.license_release or "")

    def save_license(self) -> None:
        license_name = self.license_name_input.text().strip()
        license_release = self.license_release_input.text().strip()

        if not license_name:
            QMessageBox.warning(self, "Validation", "License Name is required.")
            return

        if not license_release:
            QMessageBox.warning(self, "Validation", "License Release is required.")
            return

        try:
            license_obj = License(
                license_id=self.license.license_id if self.license else None,
                license_name=license_name,
                license_release=license_release,
            )

            self.license = save_license(license_obj)

            QMessageBox.information(self, "Success", "License saved.")
            self.close()

        except Exception as e:
            handle_db_error(self, e)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from ispring_db.core.database import create_db_and_tables

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = LicenseFormWindow()
    window.show()

    sys.exit(app.exec())