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

from ispring_db.core.database import get_session
from ispring_db.models import Customer
from sqlmodel import select

class CustomerFormWindow(QWidget):

    def __init__(self, customer: Customer | None = None, parent=None):
        super().__init__(parent)

        self.customer = customer
        self.setWindowTitle("Customer Form")
        self.resize(500, 400)

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

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_customer)
        self.cancel_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        if self.customer:
            self.load_customer()

    def load_customer(self):

        self.company_input.setText(self.customer.company or "")
        self.street_input.setText(self.customer.street or "")
        self.street_number_input.setText(self.customer.street_number or "")
        self.postcode_input.setText(self.customer.postcode or "")
        self.city_input.setText(self.customer.city or "")

        if self.customer.country:
            index = self.country_input.findText(self.customer.country)
            if index >= 0:
                self.country_input.setCurrentIndex(index)

        self.first_name_input.setText(self.customer.contact_first_name or "")
        self.last_name_input.setText(self.customer.contact_last_name or "")
        self.telephone_input.setText(self.customer.telephone or "")
        self.email_input.setText(self.customer.email or "")

    def save_customer(self):

        company = self.company_input.text().strip()

        if not company:
            QMessageBox.warning(self, "Validation Error", "Company is required.")
            return

        try:
            with get_session() as session:
                if self.customer:
                    customer = session.get(Customer, self.customer.customer_no)
                else:
                    customer = Customer()

                    # prüfen ob Tabelle leer ist
                    result = session.exec(select(Customer).order_by(Customer.customer_no)).first()

                    if result is None:
                        customer.customer_no = 1111

                customer.company = company
                customer.street = self.street_input.text()
                customer.street_number = self.street_number_input.text()
                customer.postcode = self.postcode_input.text()
                customer.city = self.city_input.text()
                customer.country = self.country_input.currentText()
                customer.contact_first_name = self.first_name_input.text()
                customer.contact_last_name = self.last_name_input.text()
                customer.telephone = self.telephone_input.text()
                customer.email = self.email_input.text()

                if not self.customer:
                    session.add(customer)

                session.commit()

            QMessageBox.information(self, "Success", "Customer saved.")
            self.close()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save customer:\n{e}",
            )


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from ispring_db.core.database import create_db_and_tables

    create_db_and_tables()

    app = QApplication(sys.argv)
    window = CustomerFormWindow()
    window.show()
    sys.exit(app.exec())