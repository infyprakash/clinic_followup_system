# ui/doctors.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox
)
from database.doctor_db import DoctorDB
from database.setting_db import SpecializationDB

from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSizePolicy


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
        main_layout = QVBoxLayout()

        # --- Top Half: Form and Buttons ---
        top_layout = QHBoxLayout()

        # 🎯 Font for inputs and buttons
        input_font = QFont()
        input_font.setPointSize(12)

        # 📋 Left side: Form
        form_layout = QVBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Doctor Name")
        self.name_input.setFont(input_font)

        self.spec_input = QComboBox()
        self.spec_input.setFont(input_font)
        self.refresh_specialization_dropdown()

        # Labels and fields vertically
        for label_text, widget in [
            ("Name", self.name_input),
            ("Specialization", self.spec_input)
        ]:
            lbl = QLabel(label_text)
            lbl.setFont(input_font)
            form_layout.addWidget(lbl)
            form_layout.addWidget(widget)

        top_layout.addLayout(form_layout, 2)

        # 🔘 Right side: Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(12)

        button_font = QFont()
        button_font.setPointSize(11)

        def styled_button(text, color):
            btn = QPushButton(text)
            btn.setFont(button_font)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                }}
            """)
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            return btn

        add_btn = styled_button("Add", "#28a745")         # Green
        update_btn = styled_button("Update", "#007bff")   # Blue
        delete_btn = styled_button("Delete", "#dc3545")   # Red
        clear_btn = styled_button("Clear", "#6c757d")     # Gray

        add_btn.clicked.connect(self.add_doctor)
        update_btn.clicked.connect(self.update_doctor)
        delete_btn.clicked.connect(self.delete_doctor)
        clear_btn.clicked.connect(self.clear_form)

        for btn in [add_btn, update_btn, delete_btn, clear_btn]:
            button_layout.addWidget(btn)

        top_layout.addLayout(button_layout, 1)
        main_layout.addLayout(top_layout)

        # --- Spacer ---
        main_layout.addSpacing(30)

        # 🔍 (Optional) Search Field — if you want to filter doctors
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search doctors...")
        self.search_input.setFont(input_font)
        self.search_input.textChanged.connect(self.refresh_table)
        main_layout.addWidget(self.search_input)

        # 📊 Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Specialization"])
        self.table.setFont(QFont("Arial", 11))
        self.table.cellClicked.connect(self.table_clicked)

        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

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
