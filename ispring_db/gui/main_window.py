from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ispring_db.gui.customers.customer_list import CustomerListWindow
from ispring_db.gui.customers.customer_form import CustomerFormDisplay
from ispring_db.gui.devices.device_list import DeviceListWindow
from ispring_db.gui.devices.device_list import DeviceListDisplay
from ispring_db.gui.gateways.gateway_list import GatewayListWindow
from ispring_db.gui.gateways.gateway_list import GatewayListDisplay
from ispring_db.gui.calibrations.calibration_list import CalibrationListWindow
from ispring_db.gui.errors.error_list import ErrorListWindow
from ispring_db.gui.device_calibrations.device_calibration_list import (
    DeviceCalibrationListWindow,
    DeviceCalibrationListDisplay,
)
from ispring_db.gui.device_errors.device_error_list import (
    DeviceErrorListWindow,
    DeviceErrorListDisplay,
)
from ispring_db.gui.logbooks.logbook_list import LogbookListWindow


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("i-spring Database")
        self.resize(1600, 950)

        self.init_ui()
        self.create_pages()
        self.connect_signals()

        self.nav_list.setCurrentRow(0)
        self.on_page_changed(0)

    def init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # ---------- LOGO OBEN ----------
        self.logo_label = QLabel()
        self.logo_label.setContentsMargins(10, 10, 10, 10)
        self.logo_label.setAlignment(Qt.AlignLeft)

        logo_path = Path(__file__).resolve().parents[2] / "ispring_db" / "data" / "logo.png"

        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.setText("ispring Logo")

        main_layout.addWidget(self.logo_label)

        # ---------- HAUPTBEREICH ----------
        content_layout = QHBoxLayout()

        # Navigation links
        self.nav_list = QListWidget()
        self.nav_list.setMinimumWidth(220)

        # rechter Bereich
        right_layout = QVBoxLayout()

        # Suche
        search_layout = QHBoxLayout()

        self.search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search text...")

        self.search_button = QPushButton("Search")
        self.reset_button = QPushButton("Reset")

        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.reset_button)
        search_layout.setContentsMargins(10, 0, 10, 10)

        # Splitter oben/unten
        self.vertical_splitter = QSplitter(Qt.Vertical)

        self.stack = QStackedWidget()

        # Unterer Bereich
        self.bottom_splitter = QSplitter(Qt.Horizontal)

        self.customer_form = CustomerFormDisplay()

        self.customer_tabs = QTabWidget()

        self.customer_device_list = DeviceListDisplay()
        self.customer_gateway_list = GatewayListDisplay()
        self.customer_device_calibration_list = DeviceCalibrationListDisplay()
        self.customer_device_error_list = DeviceErrorListDisplay()

        self.customer_tabs.addTab(self.customer_device_list, "Devices")
        self.customer_tabs.addTab(self.customer_gateway_list, "Gateways")
        self.customer_tabs.addTab(
            self.customer_device_calibration_list,
            "Device Calibrations",
        )
        self.customer_tabs.addTab(
            self.customer_device_error_list,
            "Device Errors",
        )

        self.bottom_splitter.addWidget(self.customer_form)
        self.bottom_splitter.addWidget(self.customer_tabs)

        self.vertical_splitter.addWidget(self.stack)
        self.vertical_splitter.addWidget(self.bottom_splitter)
        self.vertical_splitter.setSizes([700, 250])

        right_layout.addLayout(search_layout)
        right_layout.addWidget(self.vertical_splitter)

        content_layout.addWidget(self.nav_list, 1)
        content_layout.addLayout(right_layout, 8)

        main_layout.addLayout(content_layout)

    def create_pages(self) -> None:
        self.nav_list.clear()

        while self.stack.count():
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)

        self.customer_list_page = CustomerListWindow()
        self.device_list_page = DeviceListWindow()
        self.log_list_page = LogbookListWindow()
        self.gateway_list_page = GatewayListWindow()
        self.calibration_list_page = CalibrationListWindow()
        self.error_list_page = ErrorListWindow()
        self.device_calibration_list_page = DeviceCalibrationListWindow()
        self.device_error_list_page = DeviceErrorListWindow()

        self.pages = [
            ("Customers", self.customer_list_page),
            ("Devices", self.device_list_page),
            ("Device Calibrations", self.device_calibration_list_page),
            ("Device Errors", self.device_error_list_page),
            ("Device Log", self.log_list_page),
            ("Gateways", self.gateway_list_page),
            ("Calibrations", self.calibration_list_page),
            ("Errors", self.error_list_page),
        ]

        for title, page in self.pages:
            item = QListWidgetItem(title)

            if title == "Customers":
                font = item.font()
                font.setBold(True)
                item.setFont(font)

            self.nav_list.addItem(item)
            self.stack.addWidget(page)

    def connect_signals(self) -> None:
        self.nav_list.currentRowChanged.connect(self.on_page_changed)

        self.search_button.clicked.connect(self.perform_search)
        self.reset_button.clicked.connect(self.reset_search)
        self.search_input.returnPressed.connect(self.perform_search)

        self.customer_list_page.customer_selected.connect(self.load_customer_details)

    def current_page(self) -> QWidget | None:
        return self.stack.currentWidget()

    def on_page_changed(self, index: int) -> None:
        if index < 0 or index >= self.stack.count():
            return

        self.stack.setCurrentIndex(index)
        page = self.current_page()
        self.reset_search()

        if page and hasattr(page, "refresh_data"):
            page.refresh_data()

    def perform_search(self) -> None:
        text = self.search_input.text().strip()
        page = self.current_page()

        if page is None:
            return

        if hasattr(page, "apply_filter"):
            page.apply_filter(text)
        else:
            QMessageBox.information(
                self,
                "Search",
                "Search is not supported on this page.",
            )

    def reset_search(self) -> None:
        self.search_input.clear()

        page = self.current_page()

        if page is None:
            return

        if hasattr(page, "apply_filter"):
            page.apply_filter("")
        elif hasattr(page, "refresh_data"):
            page.refresh_data()

    def load_customer_details(self, customer_no: int) -> None:
        if hasattr(self.customer_form, "load_customer_by_id"):
            self.customer_form.load_customer_by_id(customer_no)

        if hasattr(self.customer_device_list, "load_for_customer"):
            self.customer_device_list.load_for_customer(customer_no)

        if hasattr(self.customer_gateway_list, "load_for_customer"):
            self.customer_gateway_list.load_for_customer(customer_no)

        if hasattr(self.customer_device_calibration_list, "load_for_customer"):
            self.customer_device_calibration_list.load_for_customer(customer_no)

        if hasattr(self.customer_device_error_list, "load_for_customer"):
            self.customer_device_error_list.load_for_customer(customer_no)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())