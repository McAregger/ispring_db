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

from sqlmodel import select

from ispring_db.core.database import get_session
from ispring_db.models import Gateway, Customer


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

        with get_session() as session:
            customers = session.exec(select(Customer)).all()

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

    def save_gateway(self):

        serial_no = self.serial_input.text().strip()

        if not serial_no:
            QMessageBox.warning(self, "Validation", "Serial No is required.")
            return

        try:

            with get_session() as session:

                if self.gateway:

                    if serial_no != self.gateway.serial_no:
                        QMessageBox.warning(
                            self,
                            "Invalid Change",
                            "The Serial No is the primary key and cannot be changed.",
                        )
                        return

                    gateway = session.get(Gateway, self.gateway.serial_no)

                else:

                    existing = session.get(Gateway, serial_no)

                    if existing:
                        QMessageBox.warning(
                            self,
                            "Duplicate Serial No",
                            "A gateway with this Serial No already exists.",
                        )
                        return

                    gateway = Gateway(serial_no=serial_no)

                customer_label = self.customer_input.currentText()
                gateway.customer_no = self.customer_map.get(customer_label)

                sim_text = self.sim_input.currentText()
                if sim_text == "True":
                    gateway.sim = True
                elif sim_text == "False":
                    gateway.sim = False
                else:
                    gateway.sim = None

                gateway.system = self.system_input.text()

                if not self.gateway:
                    session.add(gateway)

                session.commit()

            QMessageBox.information(self, "Success", "Gateway saved.")
            self.close()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save gateway:\n{e}",
            )


if __name__ == "__main__":

    import sys
    from PySide6.QtWidgets import QApplication
    from ispring_db.core.database import create_db_and_tables

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = GatewayFormWindow()
    window.show()

    sys.exit(app.exec())