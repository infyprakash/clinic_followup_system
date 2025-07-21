from database.clinic_db import PatientDB
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QSizePolicy,QFormLayout,QFrame
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
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- Top Half: Form and Buttons ---
        top_layout = QHBoxLayout()

        # 📋 Left side: Form
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)

        font = QFont("Arial", 12)

        def styled_input(placeholder):
            input_widget = QLineEdit()
            input_widget.setFont(font)
            input_widget.setPlaceholderText(placeholder)
            input_widget.setMinimumHeight(40)
            input_widget.setStyleSheet("padding: 6px;")
            return input_widget

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Full Name")
        self.name_input.setFont(font)
        self.name_input.setMinimumWidth(400) 
        self.name_input.setMinimumHeight(35)


        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Others"])
        self.gender_input.setFont(font)
        self.gender_input.setMinimumWidth(400)
        self.gender_input.setMinimumHeight(35)

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Enter Patient Age")
        self.age_input.setFont(font)
        self.age_input.setMinimumWidth(400)
        self.age_input.setMinimumHeight(35)

        self.phone_number_input = QLineEdit()
        self.phone_number_input.setPlaceholderText("Enter Patient Phone Number")
        self.phone_number_input.setFont(font)
        self.phone_number_input.setMinimumWidth(400)
        self.phone_number_input.setMinimumHeight(35)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Enter Patient Address")
        self.address_input.setFont(font)
        self.address_input.setMinimumWidth(400)
        self.address_input.setMinimumHeight(35)

        form_layout.addRow("👤 Name:", self.name_input)
        form_layout.addRow("⚧️ Gender:", self.gender_input)
        form_layout.addRow("🎂 Age:", self.age_input)
        form_layout.addRow("📞 Phone:", self.phone_number_input)
        form_layout.addRow("🏠 Address:", self.address_input)

        top_layout.addLayout(form_layout, 2)

        # 🎯 Right side: Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)

        button_font = QFont("Arial", 11)

        def styled_button(text, color):
            btn = QPushButton(text)
            btn.setFont(button_font)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    padding: 10px 18px;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    opacity: 0.9;
                }}
            """)
            btn.setMinimumHeight(42)
            return btn

        add_btn = styled_button("➕ Add Patient", "#28a745")
        update_btn = styled_button("🔄 Update", "#007bff")
        delete_btn = styled_button("🗑️ Delete", "#dc3545")
        clear_btn = styled_button("🧹 Clear", "#6c757d")

        add_btn.clicked.connect(self.add_patient)
        update_btn.clicked.connect(self.update_patient)
        delete_btn.clicked.connect(self.delete_patient)
        clear_btn.clicked.connect(self.clear_form)

        for btn in [add_btn, update_btn, delete_btn, clear_btn]:
            button_layout.addWidget(btn)

        top_layout.addLayout(button_layout, 1)
        main_layout.addLayout(top_layout)

        # --- Separator ---
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # 🔍 Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by name or phone number...")
        self.search_input.setFont(font)
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("padding: 6px;")
        self.search_input.textChanged.connect(self.refresh_table)
        main_layout.addWidget(self.search_input)

        # 📊 Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setFont(QFont("Arial", 11))
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Gender", "Age", "Phone", "Address", "Appointments", "Follow-Ups"
        ])
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ccc;
                background-color: #f9f9f9;
            }
            QHeaderView::section {
                background-color: #007bff;
                color: white;
                padding: 8px;
                border: 1px solid #ddd;
            }
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
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
