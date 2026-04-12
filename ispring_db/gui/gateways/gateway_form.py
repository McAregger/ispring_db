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


from ispring_db.models import Gateway
from ispring_db.repositories.gateway_repository import save_gateway, get_gateway_by_serial_no
from ispring_db.repositories.customer_repository import get_all_customers
from ispring_db.gui.utils.db_error_handler import handle_db_error

class GatewayFormWindow(QWidget):

    def __init__(self, gateway: Gateway | None = None, parent=None):
        super().__init__(parent)

        self.gateway = gateway

        self.setWindowTitle("Gateway Form")
        self.resize(300, 200)

        self.serial_input = QLineEdit()

        self.customer_input = QComboBox()
        self.load_customers()

        self.sim_input = QComboBox()
        self.sim_input.addItems([
            "",
            "True",
            "False",
        ])

        self.system_input = QLineEdit()

        form = QFormLayout()
        form.addRow("Serial No", self.serial_input)
        form.addRow("Customer", self.customer_input)
        form.addRow("SIM", self.sim_input)
        form.addRow("System", self.system_input)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_gateway)
        self.cancel_button.clicked.connect(self.close)

        buttons = QHBoxLayout()
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(buttons)

        self.setLayout(layout)

        if self.gateway:
            self.load_gateway()
            self.serial_input.setReadOnly(True)

    def load_customers(self):

        customers = get_all_customers()

        self.customer_input.clear()
        self.customer_input.addItem("")
        self.customer_map = {"": None}

        for c in customers:
            label = f"{c.customer_no} - {c.company}"
            self.customer_input.addItem(label)
            self.customer_map[label] = c.customer_no

        if self.gateway is None:
            self.customer_input.setCurrentIndex(0)

    def load_gateway(self):
        self.serial_input.setText(self.gateway.serial_no or "")

        if self.gateway.customer_no:
            for i in range(self.customer_input.count()):
                label = self.customer_input.itemText(i)
                if self.customer_map.get(label) == self.gateway.customer_no:
                    self.customer_input.setCurrentIndex(i)
                    break

        if self.gateway.sim is True:
            self.sim_input.setCurrentText("True")
        elif self.gateway.sim is False:
            self.sim_input.setCurrentText("False")
        else:
            self.sim_input.setCurrentText("")

        self.system_input.setText(self.gateway.system or "")

    def save_gateway(self) -> None:
        serial_no = self.serial_input.text().strip()

        if not serial_no:
            QMessageBox.warning(self, "Validation", "Serial No is required.")
            return

        try:
            sim_text = self.sim_input.currentText()
            if sim_text == "True":
                sim = True
            elif sim_text == "False":
                sim = False
            else:
                sim = None

            system = self.system_input.text().strip() or None

            customer_label = self.customer_input.currentText()
            customer_no = self.customer_map.get(customer_label)

            # Schutz gegen doppelte serial_no beim Neuanlegen
            existing_gateway = get_gateway_by_serial_no(serial_no)
            if self.gateway is None and existing_gateway is not None:
                QMessageBox.warning(
                    self,
                    "Validation",
                    f"A gateway with Serial No '{serial_no}' already exists.",
                )
                return

            gateway = Gateway(
                serial_no=serial_no,
                customer_no=customer_no,
                sim=sim,
                system=system,
            )

            save_gateway(gateway)

            QMessageBox.information(self, "Success", "Gateway saved.")
            self.close()

        except Exception as e:

            handle_db_error(self, e)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from ispring_db.core.database import create_db_and_tables

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = GatewayFormWindow()
    window.show()

    sys.exit(app.exec())