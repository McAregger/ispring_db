from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QComboBox,
    QDateEdit,
    QCheckBox,
)

from ispring_db.core.database import create_db_and_tables
from ispring_db.models import CustomerLicense
from ispring_db.services.customer_repository import get_all_customers
from ispring_db.services.license_repository import get_all_licenses
from ispring_db.services.customer_license_repository import save_customer_license
from ispring_db.gui.utils.db_error_handler import handle_db_error


class CustomerLicenseFormWindow(QWidget):
    def __init__(self, customer_license: CustomerLicense | None = None, parent=None):
        super().__init__(parent)

        self.customer_license = customer_license

        self.setWindowTitle("Customer License Form")
        self.resize(420, 220)

        self.customer_input = QComboBox()
        self.license_input = QComboBox()

        self.registration_input = QDateEdit()
        self.registration_input.setCalendarPopup(True)
        self.registration_input.setDate(QDate.currentDate())

        self.has_expiration_input = QCheckBox("Expiration date set")
        self.expiration_input = QDateEdit()
        self.expiration_input.setCalendarPopup(True)
        self.expiration_input.setDate(QDate.currentDate())
        self.expiration_input.setEnabled(False)

        self.has_expiration_input.toggled.connect(self.expiration_input.setEnabled)

        self.load_customers()
        self.load_licenses()

        form = QFormLayout()
        form.addRow("Customer", self.customer_input)
        form.addRow("License", self.license_input)
        form.addRow("Registration Date", self.registration_input)
        form.addRow(self.has_expiration_input)
        form.addRow("Expiration Date", self.expiration_input)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_customer_license)
        self.cancel_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        if self.customer_license:
            self.load_customer_license()

    def load_customers(self) -> None:
        customers = get_all_customers()

        self.customer_input.clear()
        self.customer_map: dict[str, int] = {}

        for customer in customers:
            label = f"{customer.customer_no} - {customer.company}"
            self.customer_input.addItem(label)
            self.customer_map[label] = customer.customer_no

    def load_licenses(self) -> None:
        licenses = get_all_licenses()

        self.license_input.clear()
        self.license_map: dict[str, int] = {}

        for license_obj in licenses:
            label = f"{license_obj.license_name} ({license_obj.license_release})"
            self.license_input.addItem(label)
            self.license_map[label] = license_obj.license_id

    def load_customer_license(self) -> None:
        for i in range(self.customer_input.count()):
            label = self.customer_input.itemText(i)
            if self.customer_map.get(label) == self.customer_license.customer_no:
                self.customer_input.setCurrentIndex(i)
                break

        for i in range(self.license_input.count()):
            label = self.license_input.itemText(i)
            if self.license_map.get(label) == self.customer_license.license_id:
                self.license_input.setCurrentIndex(i)
                break

        self.registration_input.setDate(
            QDate(
                self.customer_license.registration_date.year,
                self.customer_license.registration_date.month,
                self.customer_license.registration_date.day,
            )
        )

        if self.customer_license.expiration_date is not None:
            self.has_expiration_input.setChecked(True)
            self.expiration_input.setDate(
                QDate(
                    self.customer_license.expiration_date.year,
                    self.customer_license.expiration_date.month,
                    self.customer_license.expiration_date.day,
                )
            )
        else:
            self.has_expiration_input.setChecked(False)
            self.expiration_input.setEnabled(False)

    def save_customer_license(self) -> None:
        try:
            customer_label = self.customer_input.currentText()
            license_label = self.license_input.currentText()

            customer_no = self.customer_map.get(customer_label)
            license_id = self.license_map.get(license_label)

            if customer_no is None:
                QMessageBox.warning(self, "Validation", "Customer is required.")
                return

            if license_id is None:
                QMessageBox.warning(self, "Validation", "License is required.")
                return

            registration_date = self.registration_input.date().toPython()

            expiration_date = None
            if self.has_expiration_input.isChecked():
                expiration_date = self.expiration_input.date().toPython()

            customer_license = CustomerLicense(
                customer_license_id=(
                    self.customer_license.customer_license_id
                    if self.customer_license
                    else None
                ),
                customer_no=customer_no,
                license_id=license_id,
                registration_date=registration_date,
                expiration_date=expiration_date,
            )

            self.customer_license = save_customer_license(customer_license)

            QMessageBox.information(self, "Success", "Customer license saved.")
            self.close()

        except Exception as e:
            handle_db_error(self, e)


if __name__ == "__main__":
    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)
    window = CustomerLicenseFormWindow()
    window.show()
    sys.exit(app.exec())