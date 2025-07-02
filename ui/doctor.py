# ui/doctors.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox
)
from database.doctor_db import DoctorDB
from database.setting_db import SpecializationDB


class DoctorManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Doctor Management")
        self.setGeometry(100, 100, 700, 400)
        self.db = DoctorDB()
        self.spec_db = SpecializationDB()
        self.selected_id = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # --- Form Layout ---
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Doctor Name")

        self.spec_input = QComboBox()
        self.refresh_specialization_dropdown()

        form_layout.addWidget(QLabel("Name:"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("Specialization:"))
        form_layout.addWidget(self.spec_input)

        layout.addLayout(form_layout)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        update_btn = QPushButton("Update")
        delete_btn = QPushButton("Delete")
        clear_btn = QPushButton("Clear")

        add_btn.clicked.connect(self.add_doctor)
        update_btn.clicked.connect(self.update_doctor)
        delete_btn.clicked.connect(self.delete_doctor)
        clear_btn.clicked.connect(self.clear_form)

        for btn in [add_btn, update_btn, delete_btn, clear_btn]:
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Specialization"])
        self.table.cellClicked.connect(self.table_clicked)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.refresh_table()

    def refresh_specialization_dropdown(self):
        self.spec_input.clear()
        self.specializations = self.spec_db.get_all()
        for sid, name in self.specializations:
            self.spec_input.addItem(name, sid)

    def get_selected_spec_id(self):
        return self.spec_input.currentData()

    def add_doctor(self):
        name = self.name_input.text().strip()
        spec_id = self.get_selected_spec_id()
        if name and spec_id is not None:
            self.db.insert(name, spec_id)
            self.refresh_table()
            self.clear_form()
        else:
            QMessageBox.warning(self, "Missing Fields", "Both name and specialization are required.")

    def update_doctor(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "No Selection", "Please select a doctor to update.")
            return
        name = self.name_input.text().strip()
        spec_id = self.get_selected_spec_id()
        if name and spec_id is not None:
            self.db.update(self.selected_id, name, spec_id)
            self.refresh_table()
            self.clear_form()

    def delete_doctor(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "No Selection", "Please select a doctor to delete.")
            return
        self.db.delete(self.selected_id)
        self.refresh_table()
        self.clear_form()

    def table_clicked(self, row, col):
        self.selected_id = int(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())
        specialization = self.table.item(row, 2).text()
        index = self.spec_input.findText(specialization)
        if index >= 0:
            self.spec_input.setCurrentIndex(index)

    def refresh_table(self):
        self.table.setRowCount(0)
        for row in self.db.get_all():
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)
            for col, val in enumerate(row):
                self.table.setItem(row_index, col, QTableWidgetItem(str(val)))

    def clear_form(self):
        self.selected_id = None
        self.name_input.clear()
        self.spec_input.setCurrentIndex(0)
