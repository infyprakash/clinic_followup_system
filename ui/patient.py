from database.clinic_db import PatientDB
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont

class PatientManagement(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subhekta - Patient Management")
        self.setGeometry(100, 100, 1000, 700)
        self.db = PatientDB()
        self.selected_id = None
        self.initUI()
    
    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # --- Top Half: Form and Buttons ---
        top_layout = QHBoxLayout()

        # 📋 Left side: Form
        form_layout = QVBoxLayout()

        font = QFont()
        font.setPointSize(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Full Name")
        self.name_input.setFont(font)

        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Others"])
        self.gender_input.setFont(font)

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Enter Patient Age")
        self.age_input.setFont(font)

        self.phone_number_input = QLineEdit()
        self.phone_number_input.setPlaceholderText("Enter Patient Phone Number")
        self.phone_number_input.setFont(font)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Enter Patient Address")
        self.address_input.setFont(font)

        for label_text, widget in [
            ("Name", self.name_input),
            ("Gender", self.gender_input),
            ("Age", self.age_input),
            ("Phone", self.phone_number_input),
            ("Address", self.address_input),
        ]:
            form_layout.addWidget(QLabel(label_text))
            form_layout.addWidget(widget)

        top_layout.addLayout(form_layout, 2)

        # 🎯 Right side: Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(12)  # Add spacing between buttons

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
                # QPushButton:hover {{
                #     background-color: darken({color}, 10%);
                # }}
            """)
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            return btn

        add_btn = styled_button("Add Patient", "#28a745")      # Green
        update_btn = styled_button("Update", "#007bff")        # Blue
        delete_btn = styled_button("Delete", "#dc3545")        # Red
        clear_btn = styled_button("Clear", "#6c757d")          # Gray

        add_btn.clicked.connect(self.add_patient)
        update_btn.clicked.connect(self.update_patient)
        delete_btn.clicked.connect(self.delete_patient)
        clear_btn.clicked.connect(self.clear_form)

        for btn in [add_btn, update_btn, delete_btn, clear_btn]:
            button_layout.addWidget(btn)

        top_layout.addLayout(button_layout, 1)
        main_layout.addLayout(top_layout)

        # --- Spacer ---
        main_layout.addSpacing(30)

        # 🔍 Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or phone number...")
        self.search_input.setFont(font)
        self.search_input.textChanged.connect(self.refresh_table)
        main_layout.addWidget(self.search_input)

        # 📊 Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Gender", "Age", "Phone", "Address", "Appointments", "Follow-Ups"
        ])
        self.table.setFont(QFont("Arial", 11))
        self.table.cellClicked.connect(self.table_clicked)

        main_layout.addWidget(self.table)

        self.setCentralWidget(main_widget)
        self.refresh_table()

    def add_patient(self):
        name = self.name_input.text()
        gender = self.gender_input.currentText()
        age = self.age_input.text()
        phone = self.phone_number_input.text()
        address = self.address_input.text()

        if name and phone:
            self.db.insert_patient(name, gender, age, phone, address)
            self.refresh_table()
            self.clear_form()
        else:
            QMessageBox.warning(self, "Missing Fields", "Name and phone number are required.")

    def update_patient(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "No Selection", "Select a patient to update.")
            return

        name = self.name_input.text()
        gender = self.gender_input.currentText()
        age = self.age_input.text()
        phone = self.phone_number_input.text()
        address = self.address_input.text()

        self.db.update_patient(self.selected_id, name, gender, age, phone, address)
        self.refresh_table()
        self.clear_form()

    def delete_patient(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "No Selection", "Select a patient to delete.")
            return

        self.db.delete_patient(self.selected_id)
        self.refresh_table()
        self.clear_form()

    def table_clicked(self, row, col):
        self.selected_id = int(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())
        self.gender_input.setCurrentText(self.table.item(row, 2).text())
        self.age_input.setText(self.table.item(row, 3).text())
        self.phone_number_input.setText(self.table.item(row, 4).text())
        self.address_input.setText(self.table.item(row, 5).text())

    def refresh_table(self):
        keyword = self.search_input.text().lower()
        self.table.setRowCount(0)
        data = self.db.get_all_with_summary()

        for row in data:
            if keyword and keyword not in row[1].lower() and keyword not in row[4]:
                continue
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            for col, val in enumerate(row):
                self.table.setItem(row_idx, col, QTableWidgetItem(str(val)))

    def clear_form(self):
        self.selected_id = None
        self.name_input.clear()
        self.gender_input.setCurrentIndex(0)
        self.age_input.clear()
        self.phone_number_input.clear()
        self.address_input.clear()
