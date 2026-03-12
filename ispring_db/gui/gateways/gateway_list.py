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

from sqlmodel import select

from ispring_db.core.database import get_session, create_db_and_tables
from ispring_db.models import Gateway, Customer
from ispring_db.gui.gateways.gateway_form import GatewayFormWindow


class GatewayListWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gateways")
        self.resize(900, 500)

        self.table = QTableWidget()

        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels(
            [
                "Serial No",
                "Customer",
                "SIM",
                "System",
            ]
        )

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.new_button = QPushButton("New")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        self.new_button.clicked.connect(self.new_gateway)
        self.edit_button.clicked.connect(self.edit_gateway)
        self.delete_button.clicked.connect(self.delete_gateway)
        self.refresh_button.clicked.connect(self.load_gateways)

        buttons = QHBoxLayout()

        buttons.addWidget(self.new_button)
        buttons.addWidget(self.edit_button)
        buttons.addWidget(self.delete_button)
        buttons.addWidget(self.refresh_button)

        layout = QVBoxLayout()

        layout.addWidget(self.table)
        layout.addLayout(buttons)

        self.setLayout(layout)

        self.load_gateways()

    def load_gateways(self):

        with get_session() as session:
            statement = (
                select(Gateway, Customer)
                .join(Customer, Gateway.customer_no == Customer.customer_no, isouter=True)
            )
            results = session.exec(statement).all()

        self.table.setRowCount(len(results))

        for row, (gateway, customer) in enumerate(results):

            self.table.setItem(row, 0, QTableWidgetItem(gateway.serial_no))

            if customer:
                customer_text = f"{customer.customer_no} - {customer.company}"
            else:
                customer_text = ""

            self.table.setItem(row, 1, QTableWidgetItem(customer_text))
            self.table.setItem(row, 2, QTableWidgetItem("" if gateway.sim is None else str(gateway.sim)))
            self.table.setItem(row, 3, QTableWidgetItem(gateway.system or ""))

    def get_selected_serial_no(self):

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Selection", "Select a gateway first")
            return None

        return self.table.item(row, 0).text()

    def new_gateway(self):

        self.form = GatewayFormWindow()
        self.form.show()

    def edit_gateway(self):

        serial_no = self.get_selected_serial_no()

        if not serial_no:
            return

        with get_session() as session:
            gateway = session.get(Gateway, serial_no)

        self.form = GatewayFormWindow(gateway)
        self.form.show()

    def delete_gateway(self):

        serial_no = self.get_selected_serial_no()

        if not serial_no:
            return

        reply = QMessageBox.question(
            self,
            "Delete Gateway",
            f"Delete gateway {serial_no}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        with get_session() as session:

            gateway = session.get(Gateway, serial_no)

            if gateway:
                session.delete(gateway)
                session.commit()

        self.load_gateways()


if __name__ == "__main__":

    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = GatewayListWindow()
    window.show()

    sys.exit(app.exec())