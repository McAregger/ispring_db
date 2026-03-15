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
from ispring_db.models import Calibration
from ispring_db.gui.calibrations.calibration_form import CalibrationFormWindow


class CalibrationListWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calibrations")
        self.resize(1000, 500)

        self.table = QTableWidget()

        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels(
            [
                "Cal ID",
                "Calibration Type",
                "Min Temp",
                "Max Temp",
                "Cal Def Date",
                "Cal Def File",
            ]
        )
        self.table.setSortingEnabled(True)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)

        self.new_button = QPushButton("New")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        self.new_button.clicked.connect(self.new_calibration)
        self.edit_button.clicked.connect(self.edit_calibration)
        self.delete_button.clicked.connect(self.delete_calibration)
        self.refresh_button.clicked.connect(self.load_calibrations)

        buttons = QHBoxLayout()

        buttons.addWidget(self.new_button)
        buttons.addWidget(self.edit_button)
        buttons.addWidget(self.delete_button)
        buttons.addWidget(self.refresh_button)

        layout = QVBoxLayout()

        layout.addWidget(self.table)
        layout.addLayout(buttons)

        self.setLayout(layout)

        self.load_calibrations()

    def shorten_path(self, path, max_length=50):
        if len(path) <= max_length:
            return path
        return "..." + path[-max_length:]

    def load_calibrations(self):

        with get_session() as session:
            results = session.exec(select(Calibration)).all()

        self.table.setRowCount(len(results))

        for row, calibration in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(str(calibration.cal_id)))
            self.table.setItem(row, 1, QTableWidgetItem(calibration.cal_type or ""))
            self.table.setItem(row, 2, QTableWidgetItem("" if calibration.min_temp is None else str(calibration.min_temp)))
            self.table.setItem(row, 3, QTableWidgetItem("" if calibration.max_temp is None else str(calibration.max_temp)))
            self.table.setItem(row, 4, QTableWidgetItem(str(calibration.cal_def_date or "")))
            full_path = calibration.cal_def_file
            display_path = self.shorten_path(full_path, 60)

            item = QTableWidgetItem(display_path)
            item.setToolTip(full_path)  # vollständiger Pfad bei Hover
            self.table.setItem(row, 5, item)




    def get_selected_cal_id(self):

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Selection", "Select a calibration first")
            return None

        return int(self.table.item(row, 0).text())

    def new_calibration(self):

        self.form = CalibrationFormWindow()
        self.form.show()

    def edit_calibration(self):

        cal_id = self.get_selected_cal_id()

        if cal_id is None:
            return

        with get_session() as session:
            calibration = session.get(Calibration, cal_id)

        self.form = CalibrationFormWindow(calibration)
        self.form.show()

    def delete_calibration(self):

        cal_id = self.get_selected_cal_id()

        if cal_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete Calibration",
            f"Delete calibration {cal_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        with get_session() as session:

            calibration = session.get(Calibration, cal_id)

            if calibration:
                session.delete(calibration)
                session.commit()

        self.load_calibrations()


if __name__ == "__main__":

    import sys

    create_db_and_tables()

    app = QApplication(sys.argv)

    window = CalibrationListWindow()
    window.show()

    sys.exit(app.exec())