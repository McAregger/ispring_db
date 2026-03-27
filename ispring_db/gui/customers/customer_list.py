from PySide6.QtCore import Qt, Signal
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


from ispring_db.core.database import create_db_and_tables
from ispring_db.gui.customers.customer_form import CustomerFormWindow
from ispring_db.services.customer_repository import (delete_customer_by_customer_no,
                                                     get_customer_by_customer_no,
                                                     get_all_customers)


class CustomerListWindow(QWidget):
    customer_selected = Signal(int)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Customers")
        self.resize(1000, 600)

        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setSortingEnabled(True)

        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Company",
                "Street",
                "No.",
                "Postcode",
                "City",
                "Country",
                "First Name",
                "Last Name",
                "Telephone",
                "Email",
            ]
        )

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.ElideRight)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)   # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)            # Company
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)   # Street
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)   # No.
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)   # Postcode
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)   # City
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)   # Country
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)   # First Name
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)   # Last Name
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)   # Telephone
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents)  # Email

        self.new_button = QPushButton("New")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        self.new_button.clicked.connect(self.new_customer)
        self.edit_button.clicked.connect(self.edit_customer)
        self.delete_button.clicked.connect(self.delete_customer)
        self.refresh_button.clicked.connect(self.load_customers)

        self.table.itemSelectionChanged.connect(self.on_selection_changed)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.load_customers()

    def load_customers(self) -> None:
        customers = get_all_customers()

        self.table.setRowCount(len(customers))

        for row, c in enumerate(customers):
            self.table.setItem(row, 0, QTableWidgetItem(str(c.customer_no)))
            self.table.setItem(row, 1, QTableWidgetItem(c.company or ""))
            self.table.setItem(row, 2, QTableWidgetItem(c.street or ""))
            self.table.setItem(row, 3, QTableWidgetItem(c.street_number or ""))
            self.table.setItem(row, 4, QTableWidgetItem(c.postcode or ""))
            self.table.setItem(row, 5, QTableWidgetItem(c.city or ""))
            self.table.setItem(row, 6, QTableWidgetItem(c.country or ""))
            self.table.setItem(row, 7, QTableWidgetItem(c.contact_first_name or ""))
            self.table.setItem(row, 8, QTableWidgetItem(c.contact_last_name or ""))
            self.table.setItem(row, 9, QTableWidgetItem(c.telephone or ""))
            self.table.setItem(row, 10, QTableWidgetItem(c.email or ""))

        self.table.resizeRowsToContents()
        self.table.clearSelection()

    def get_selected_customer_no(self) -> int | None:
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a customer.")
            return None

        item = self.table.item(row, 0)
        if item is None:
            QMessageBox.warning(self, "Selection", "Selected row is invalid.")
            return None

        return int(item.text())

    def new_customer(self) -> None:
        self.form = CustomerFormWindow()
        self.form.show()

    def edit_customer(self) -> None:
        customer_no = self.get_selected_customer_no()
        if customer_no is None:
            return

        customer = get_customer_by_customer_no(customer_no)

        if customer is None:
            QMessageBox.warning(self, "Error", "Customer not found.")
            self.load_customers()
            return

        self.form = CustomerFormWindow(customer)
        self.form.show()

    def delete_customer(self) -> None:
        customer_no = self.get_selected_customer_no()
        if customer_no is None:
            return
        row = self.table.currentRow()
        company_item = self.table.item(row, 1)
        company = company_item.text() if company_item else ""

        reply = QMessageBox.question(
            self,
            "Delete Customer",
            f"Delete '{company}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.No:
            return
        try:
            delete_customer_by_customer_no(customer_no)

            self.load_customers()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not delete customer:\n{e}",
            )

    def on_selection_changed(self):

        row = self.table.currentRow()
        if row < 0:
            return

        item = self.table.item(row, 0)
        if item is None:
            return

        customer_no = int(item.text())

        self.customer_selected.emit(customer_no)

    def apply_filter(self, text: str) -> None:
        text = text.lower().strip()

        for row in range(self.table.rowCount()):
            row_matches = False

            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    row_matches = True
                    break

            self.table.setRowHidden(row, not row_matches)



if __name__ == "__main__":
    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)
    window = CustomerListWindow()
    window.show()
    sys.exit(app.exec())