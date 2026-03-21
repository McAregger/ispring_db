from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
)


from ispring_db.models import Customer
from ispring_db.services.customer_repositry import save_customer, get_customer_with_customer_no


class CustomerFormBase(QWidget):
    def __init__(self, customer: Customer | None = None, parent=None):
        super().__init__(parent)

        self.customer = customer

        self.company_input = QLineEdit()
        self.street_input = QLineEdit()
        self.street_number_input = QLineEdit()
        self.postcode_input = QLineEdit()
        self.city_input = QLineEdit()

        self.country_input = QComboBox()
        self.country_input.addItems(["Switzerland", "Germany"])

        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.telephone_input = QLineEdit()
        self.email_input = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow("Company", self.company_input)
        form_layout.addRow("Street", self.street_input)
        form_layout.addRow("Street Number", self.street_number_input)
        form_layout.addRow("Postcode", self.postcode_input)
        form_layout.addRow("City", self.city_input)
        form_layout.addRow("Country", self.country_input)
        form_layout.addRow("First Name", self.first_name_input)
        form_layout.addRow("Last Name", self.last_name_input)
        form_layout.addRow("Telephone", self.telephone_input)
        form_layout.addRow("Email", self.email_input)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(form_layout)
        self.setLayout(self.main_layout)

        if self.customer:
            self.load_customer()

    def set_customer(self, customer: Customer | None) -> None:
        self.customer = customer
        self.clear_fields()

        if self.customer:
            self.load_customer()

    def load_customer(self) -> None:
        if not self.customer:
            return

        self.company_input.setText(self.customer.company or "")
        self.street_input.setText(self.customer.street or "")
        self.street_number_input.setText(self.customer.street_number or "")
        self.postcode_input.setText(self.customer.postcode or "")
        self.city_input.setText(self.customer.city or "")

        if self.customer.country:
            index = self.country_input.findText(self.customer.country)
            if index >= 0:
                self.country_input.setCurrentIndex(index)
            else:
                self.country_input.setCurrentIndex(0)
        else:
            self.country_input.setCurrentIndex(0)

        self.first_name_input.setText(self.customer.contact_first_name or "")
        self.last_name_input.setText(self.customer.contact_last_name or "")
        self.telephone_input.setText(self.customer.telephone or "")
        self.email_input.setText(self.customer.email or "")

    def load_customer_by_id(self, customer_no: int) -> None:

        customer = get_customer_with_customer_no(customer_no)

        self.set_customer(customer)

    def clear_fields(self) -> None:
        self.company_input.clear()
        self.street_input.clear()
        self.street_number_input.clear()
        self.postcode_input.clear()
        self.city_input.clear()
        self.country_input.setCurrentIndex(0)
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.telephone_input.clear()
        self.email_input.clear()


class CustomerFormWindow(CustomerFormBase):
    def __init__(self, customer: Customer | None = None, parent=None):
        super().__init__(customer=customer, parent=parent)

        self.setWindowTitle("Customer Form")
        self.resize(300, 400)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_customer)
        self.cancel_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        self.main_layout.addLayout(button_layout)

    def save_customer(self) -> None:
        company = self.company_input.text().strip()

        if not company:
            QMessageBox.warning(self, "Validation Error", "Company is required.")
            return

        try:
            customer = Customer(
                customer_no=self.customer.customer_no if self.customer else None,
                company=company,
                street=self.street_input.text().strip(),
                street_number=self.street_number_input.text().strip(),
                postcode=self.postcode_input.text().strip(),
                city=self.city_input.text().strip(),
                country=self.country_input.currentText(),
                contact_first_name=self.first_name_input.text().strip(),
                contact_last_name=self.last_name_input.text().strip(),
                telephone=self.telephone_input.text().strip(),
                email=self.email_input.text().strip(),
            )

            self.customer = save_customer(customer)

            QMessageBox.information(self, "Success", "Customer saved.")
            self.close()

        except ValueError as e:
            QMessageBox.critical(self, "Database Error", str(e))
        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save customer:\n{e}",
            )


class CustomerFormDisplay(CustomerFormBase):
    def __init__(self, customer: Customer | None = None, parent=None):
        super().__init__(customer=customer, parent=parent)

        self.setWindowTitle("Customer")

        self.company_input.setReadOnly(True)
        self.street_input.setReadOnly(True)
        self.street_number_input.setReadOnly(True)
        self.postcode_input.setReadOnly(True)
        self.city_input.setReadOnly(True)
        self.first_name_input.setReadOnly(True)
        self.last_name_input.setReadOnly(True)
        self.telephone_input.setReadOnly(True)
        self.email_input.setReadOnly(True)

        self.country_input.setEnabled(False)

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from ispring_db.core.database import create_db_and_tables

    create_db_and_tables()

    app = QApplication(sys.argv)
    window = CustomerFormWindow()
    window.show()
    sys.exit(app.exec())