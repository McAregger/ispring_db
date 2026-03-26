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
from ispring_db.gui.errors.error_form import ErrorFormWindow
from ispring_db.services.error_repository import get_all_errors, get_error_by_error_id, delete_error_by_error_id


class ErrorListWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Errors")
        self.resize(1000, 500)

        self.table = QTableWidget()
        self.table.setColumnCount(5)

        self.table.setSortingEnabled(True)
        self.table.setHorizontalHeaderLabels(
            [
                "Error ID",
                "Component",
                "Error Cause",
                "Error Severity",
                "Repairability",
            ]
        )
        self.table.setSortingEnabled(True)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.new_button = QPushButton("New")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        self.new_button.clicked.connect(self.new_error)
        self.edit_button.clicked.connect(self.edit_error)
        self.delete_button.clicked.connect(self.delete_error)
        self.refresh_button.clicked.connect(self.load_errors)

        buttons = QHBoxLayout()
        buttons.addWidget(self.new_button)
        buttons.addWidget(self.edit_button)
        buttons.addWidget(self.delete_button)
        buttons.addWidget(self.refresh_button)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(buttons)

        self.setLayout(layout)

        self.load_errors()

    def severity_to_text(self, value: int) -> str:
        severity_map = {
            1: "low",
            2: "medium",
            3: "high",
            4: "critical",
        }
        return severity_map.get(value, str(value))

    def load_errors(self):


        results = get_all_errors()

        self.table.setRowCount(len(results))

        for row, error in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(str(error.error_id)))
            self.table.setItem(row, 1, QTableWidgetItem(error.component or ""))
            self.table.setItem(row, 2, QTableWidgetItem(error.error_cause or ""))
            self.table.setItem(row, 3, QTableWidgetItem(self.severity_to_text(error.error_severity)))
            self.table.setItem(row, 4, QTableWidgetItem("Yes" if error.repairability else "No"))

    def get_selected_error_id(self):

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Selection", "Select an error first")
            return None

        return int(self.table.item(row, 0).text())

    def new_error(self):

        self.form = ErrorFormWindow()
        self.form.show()

    def edit_error(self):

        error_id = self.get_selected_error_id()

        if error_id is None:
            return


        error = get_error_by_error_id(error_id)

        self.form = ErrorFormWindow(error)
        self.form.show()

    def delete_error(self):

        error_id = self.get_selected_error_id()

        if error_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete Error",
            f"Delete error {error_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        error = delete_error_by_error_id(error_id)

        self.load_errors()


if __name__ == "__main__":

    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = ErrorListWindow()
    window.show()

    sys.exit(app.exec())