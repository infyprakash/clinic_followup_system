import sys
from database.clinic_db import PatientDB
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import QDate

class PatientManagement(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clinic - Patient Management")
        self.setGeometry(100, 100, 900, 600)
        self.db = PatientDB()
        self.selected_id = None
        self.initUI()
    
    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # 🔍 Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or phone number...")
        self.search_input.textChanged.connect(self.refresh_table)
        main_layout.addWidget(self.search_input)

        # 🧾 Form layout 
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Full Name")

        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male","Female","Others"])

        self.date_of_birth_input = QDateEdit()
        self.date_of_birth_input.setCalendarPopup(True)
        self.date_of_birth_input.setDate(QDate.currentDate())

        self.phone_number_input = QLineEdit()
        self.phone_number_input.setPlaceholderText("Enter Patient Phone Number")

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Enter Patient address")

        form_layout.addWidget(QLabel("Name:"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("Gender:"))
        form_layout.addWidget(self.gender_input)
        form_layout.addWidget(QLabel("DOB:"))
        form_layout.addWidget(self.date_of_birth_input)
        form_layout.addWidget(QLabel("Phone:"))
        form_layout.addWidget(self.phone_number_input)
        form_layout.addWidget(QLabel("Address:"))
        form_layout.addWidget(self.address_input)

        # 🔘 Button layout 
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Patient")
        update_btn = QPushButton("Update")
        delete_btn = QPushButton("Delete")
        clear_btn = QPushButton("Clear")

        add_btn.clicked.connect(self.add_patient)
        update_btn.clicked.connect(self.update_patient)
        delete_btn.clicked.connect(self.delete_patient)
        clear_btn.clicked.connect(self.clear_form)

        for btn in [add_btn, update_btn, delete_btn, clear_btn]:
            button_layout.addWidget(btn)

        # 📊 Table setup 
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Gender", "DOB", "Phone", "Address", "Appointments", "Follow-Ups"
        ])
        self.table.cellClicked.connect(self.table_clicked)

        # 📦 Add to layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.refresh_table()

    def add_patient(self):
        name = self.name_input.text()
        gender = self.gender_input.currentText()
        dob = self.date_of_birth_input.date().toString("yyyy-MM-dd")
        phone = self.phone_number_input.text()
        address = self.address_input.text()

        if name and phone:
            self.db.insert_patient(name, gender, dob, phone, address)
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
        dob = self.date_of_birth_input.date().toString("yyyy-MM-dd")
        phone = self.phone_number_input.text()
        address = self.address_input.text()

        self.db.update_patient(self.selected_id, name, gender, dob, phone, address)
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
        self.date_of_birth_input.setDate(QDate.fromString(self.table.item(row, 3).text(), "yyyy-MM-dd"))
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
        self.date_of_birth_input.setDate(QDate.currentDate())
        self.phone_number_input.clear()
        self.address_input.clear()