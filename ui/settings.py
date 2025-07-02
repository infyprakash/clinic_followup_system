# ui/settings.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QTabWidget
)
from database.setting_db import SpecializationDB, StatusDB


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(150, 150, 600, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        tabs = QTabWidget()

        tabs.addTab(self.specialization_tab_ui(), "Doctor Specializations")
        tabs.addTab(self.status_tab_ui(), "Appointment Statuses")

        layout.addWidget(tabs)
        self.setLayout(layout)

    # --- Doctor Specializations Tab ---
    def specialization_tab_ui(self):
        self.spec_tab = QWidget()
        layout = QVBoxLayout()

        # Input and Buttons
        form = QHBoxLayout()
        self.spec_input = QLineEdit()
        self.spec_input.setPlaceholderText("New Specialization")
        add_btn = QPushButton("Add")
        del_btn = QPushButton("Delete Selected")
        add_btn.clicked.connect(self.add_specialization)
        del_btn.clicked.connect(self.delete_specialization)
        form.addWidget(self.spec_input)
        form.addWidget(add_btn)
        form.addWidget(del_btn)

        layout.addLayout(form)

        # Table
        self.spec_table = QTableWidget()
        self.spec_table.setColumnCount(2)
        self.spec_table.setHorizontalHeaderLabels(["ID", "Specialization"])
        layout.addWidget(self.spec_table)

        self.spec_tab.setLayout(layout)
        self.refresh_spec_table()
        return self.spec_tab

    def add_specialization(self):
        name = self.spec_input.text().strip()
        if name:
            SpecializationDB().insert(name)
            self.refresh_spec_table()
            self.spec_input.clear()

    def delete_specialization(self):
        selected = self.spec_table.currentRow()
        if selected != -1:
            spec_id = int(self.spec_table.item(selected, 0).text())
            SpecializationDB().delete(spec_id)
            self.refresh_spec_table()

    def refresh_spec_table(self):
        self.spec_table.setRowCount(0)
        for row in SpecializationDB().get_all():
            row_index = self.spec_table.rowCount()
            self.spec_table.insertRow(row_index)
            for col, val in enumerate(row):
                self.spec_table.setItem(row_index, col, QTableWidgetItem(str(val)))

    # --- Appointment Statuses Tab ---
    def status_tab_ui(self):
        self.status_tab = QWidget()
        layout = QVBoxLayout()

        # Input and Buttons
        form = QHBoxLayout()
        self.status_input = QLineEdit()
        self.status_input.setPlaceholderText("New Status (e.g. Pending)")
        add_btn = QPushButton("Add")
        del_btn = QPushButton("Delete Selected")
        add_btn.clicked.connect(self.add_status)
        del_btn.clicked.connect(self.delete_status)
        form.addWidget(self.status_input)
        form.addWidget(add_btn)
        form.addWidget(del_btn)

        layout.addLayout(form)

        # Table
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(2)
        self.status_table.setHorizontalHeaderLabels(["ID", "Status"])
        layout.addWidget(self.status_table)

        self.status_tab.setLayout(layout)
        self.refresh_status_table()
        return self.status_tab

    def add_status(self):
        name = self.status_input.text().strip()
        if name:
            StatusDB().insert(name)
            self.refresh_status_table()
            self.status_input.clear()

    def delete_status(self):
        selected = self.status_table.currentRow()
        if selected != -1:
            status_id = int(self.status_table.item(selected, 0).text())
            StatusDB().delete(status_id)
            self.refresh_status_table()

    def refresh_status_table(self):
        self.status_table.setRowCount(0)
        for row in StatusDB().get_all():
            row_index = self.status_table.rowCount()
            self.status_table.insertRow(row_index)
            for col, val in enumerate(row):
                self.status_table.setItem(row_index, col, QTableWidgetItem(str(val)))
