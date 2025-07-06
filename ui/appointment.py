from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QTimeEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QListWidget, QListWidgetItem, QSizePolicy
)
from PyQt6.QtCore import QDate, QTime, QDateTime, Qt

from database.appointment_db import AppointmentDB
from database.clinic_db import PatientDB
from database.doctor_db import DoctorDB
from database.setting_db import StatusDB

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont,QColor


class AppointmentBooking(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Appointment Booking")
        self.setGeometry(100, 100, 900, 500)
        self.db = AppointmentDB()
        self.patient_db = PatientDB()
        self.selected_id = None
        self.selected_patient_id = None  # For searchable patient selection
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()

        # --- Left side: Form stacked vertically ---
        form_layout = QVBoxLayout()



        # Patient search
        form_layout.addWidget(QLabel("Search Patient by Name or Phone:"))
        self.patient_search_input = QLineEdit()
        self.patient_search_input.setPlaceholderText("Type patient name or phone...")
        self.patient_search_input.textChanged.connect(self.on_patient_search)
        form_layout.addWidget(self.patient_search_input)

        self.patient_list_widget = QListWidget()
        self.patient_list_widget.setMaximumHeight(100)
        self.patient_list_widget.itemClicked.connect(self.on_patient_selected)
        form_layout.addWidget(self.patient_list_widget)

        # Doctor dropdown
        form_layout.addWidget(QLabel("Doctor:"))
        self.doctor_input = QComboBox()
        form_layout.addWidget(self.doctor_input)

        # Date picker
        form_layout.addWidget(QLabel("Date:"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addWidget(self.date_input)

        # Time picker
        form_layout.addWidget(QLabel("Time:"))
        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("hh:mm AP")
        self.time_input.setTimeRange(QTime(0, 0), QTime(23, 59))
        form_layout.addWidget(self.time_input)

        # Reason input
        form_layout.addWidget(QLabel("Reason:"))
        self.reason_input = QLineEdit()
        form_layout.addWidget(self.reason_input)

        # Status dropdown
        form_layout.addWidget(QLabel("Status:"))
        self.status_input = QComboBox()
        form_layout.addWidget(self.status_input)



        # --- Right side: Add, Update, Delete, Clear buttons ---
        buttons_right_layout = QVBoxLayout()
        buttons_right_layout.setSpacing(15)
        buttons_right_layout.setContentsMargins(10, 10, 10, 10)

        button_style = """
            background-color: %s; 
            color: white; 
            font-weight: bold; 
            font-size: 16px; 
            min-height: 40px;
        """

        # Add button (green)
        self.add_btn = QPushButton("Add")
        self.add_btn.setStyleSheet(button_style % "#28a745")
        self.add_btn.clicked.connect(self.add_appointment)
        self.add_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        buttons_right_layout.addWidget(self.add_btn)

        # Update button (blue)
        self.update_btn = QPushButton("Update")
        self.update_btn.setStyleSheet(button_style % "#007bff")
        self.update_btn.clicked.connect(self.update_appointment)
        self.update_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        buttons_right_layout.addWidget(self.update_btn)

        # Delete button (red)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet(button_style % "#dc3545")
        self.delete_btn.clicked.connect(self.delete_appointment)
        self.delete_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        buttons_right_layout.addWidget(self.delete_btn)

        # Clear button (gray)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet(button_style % "#6c757d")
        self.clear_btn.clicked.connect(self.clear_form)
        self.clear_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        buttons_right_layout.addWidget(self.clear_btn)

        buttons_right_layout.addStretch()

        # Add layouts to main
        main_layout.addLayout(form_layout, 1)
        main_layout.addLayout(buttons_right_layout, 1)

        # --- Below the main layout: Appointment table ---
        overall_layout = QVBoxLayout()
        overall_layout.addLayout(main_layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search appointment by patient, doctor or status...")
        self.search_input.textChanged.connect(self.refresh_table)
        overall_layout.addWidget(self.search_input)


        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Patient", "Doctor", "Date", "Time", "Reason", "Status"])
        self.table.cellClicked.connect(self.table_clicked)
        overall_layout.addWidget(self.table)

        self.setLayout(overall_layout)

        self.refresh_dropdowns()
        self.refresh_table()

    def refresh_dropdowns(self):
        # Populate doctor dropdown
        self.doctor_input.clear()
        for did, name in DoctorDB().get_all():
            self.doctor_input.addItem(name, did)

        # # Populate status dropdown
        self.status_input.clear()
        for sid, name in StatusDB().get_all():
            self.status_input.addItem(name, sid)

        # Populate full patient list initially
        self.load_patient_list()

    def load_patient_list(self, filter_text=""):
        self.patient_list_widget.clear()
        patients = self.patient_db.get_all()
        filter_text = filter_text.lower()
        for pid, name, phone in patients:
            if filter_text in name.lower() or filter_text in phone.lower():
                item = QListWidgetItem(f"{name} ({phone})")
                item.setData(Qt.ItemDataRole.UserRole, pid)
                self.patient_list_widget.addItem(item)

    def on_patient_search(self, text):
        self.load_patient_list(text)

    def on_patient_selected(self, item):
        self.selected_patient_id = item.data(Qt.ItemDataRole.UserRole)
        self.patient_search_input.setText(item.text())
        # Optionally clear the patient list to reduce clutter
        self.patient_list_widget.clear()

    def set_status(self, status_name):
        # Set the status_input combo to the matching status name
        index = self.status_input.findText(status_name)
        if index != -1:
            self.status_input.setCurrentIndex(index)

    def get_selected_ids(self):
        # Patient comes from self.selected_patient_id instead of combo box
        patient_id = self.selected_patient_id
        doctor_id = self.doctor_input.currentData()
        status_id = self.status_input.currentData()
        return patient_id, doctor_id, status_id

    def add_appointment(self):
        patient_id, doctor_id, status_id = self.get_selected_ids()
        date = self.date_input.date().toString("yyyy-MM-dd")
        time = self.time_input.time().toString("HH:mm")
        reason = self.reason_input.text().strip()

        if patient_id is None:
            QMessageBox.warning(self, "Validation Error", "Select a patient.")
            return

        # Disallow past time for today
        if self.date_input.date() == QDate.currentDate():
            selected_dt = QDateTime(self.date_input.date(), self.time_input.time())
            if selected_dt < QDateTime.currentDateTime():
                QMessageBox.warning(self, "Invalid Time", "You cannot select a past time for today.")
                return

        if patient_id and doctor_id and status_id:
            self.db.insert(patient_id, doctor_id, date, time, reason, status_id)
            self.refresh_table()
            self.clear_form()
        else:
            QMessageBox.warning(self, "Validation", "All fields must be selected.")

    def update_appointment(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "No Selection", "Select an appointment to update.")
            return

        patient_id, doctor_id, status_id = self.get_selected_ids()
        date = self.date_input.date().toString("yyyy-MM-dd")
        time = self.time_input.time().toString("HH:mm")
        reason = self.reason_input.text().strip()

        self.db.update(self.selected_id, patient_id, doctor_id, date, time, reason, status_id)
        self.refresh_table()
        self.clear_form()

    def delete_appointment(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "No Selection", "Select an appointment to delete.")
            return
        self.db.delete(self.selected_id)
        self.refresh_table()
        self.clear_form()

    def table_clicked(self, row, col):
        self.selected_id = int(self.table.item(row, 0).text())

        patient_name = self.table.item(row, 1).text()
        # Set patient_search_input text, but we need to get patient id from name
        # For simplicity, search patient by name in patient_db to get id
        self.selected_patient_id = None
        for pid, name, phone in self.patient_db.get_all():
            if name == patient_name:
                self.selected_patient_id = pid
                self.patient_search_input.setText(f"{name} ({phone})")
                break

        self.doctor_input.setCurrentText(self.table.item(row, 2).text())
        self.date_input.setDate(QDate.fromString(self.table.item(row, 3).text(), "yyyy-MM-dd"))
        self.time_input.setTime(QTime.fromString(self.table.item(row, 4).text(), "hh:mm AP"))
        self.reason_input.setText(self.table.item(row, 5).text())
        self.status_input.setCurrentText(self.table.item(row, 6).text())


    def refresh_table(self):
        keyword = self.search_input.text().lower()
        self.table.setRowCount(0)
        for row in self.db.get_all():
            # row = [id, patient_name, doctor_name, date, time, reason, status]
            if keyword:
                if not (
                    keyword in str(row[1]).lower()
                    or keyword in str(row[2]).lower()
                    or keyword in str(row[6]).lower()
                ):
                    continue

            row_index = self.table.rowCount()
            self.table.insertRow(row_index)

            status = str(row[6]).lower()

            # Define colors for each status
            if status == "pending":
                background_color = QColor("#FFFACD")  # Light yellow
            elif status == "cancelled":
                background_color = QColor("#F08080")  # Light coral (red-ish)
            elif status == "completed":
                background_color = QColor("#90EE90")  # Light green
            else:
                background_color = QColor("white")  # Default white

            for col, val in enumerate(row):
                if col == 4:  # Time column formatting
                    try:
                        time_obj = QTime.fromString(val, "HH:mm")
                        val = time_obj.toString("hh:mm AP")
                    except Exception:
                        pass

                item = QTableWidgetItem(str(val))
                item.setBackground(background_color)  # Set background color based on status
                self.table.setItem(row_index, col, item)

    def clear_form(self):
        self.selected_id = None
        self.selected_patient_id = None
        self.patient_search_input.clear()
        self.patient_list_widget.clear()
        self.doctor_input.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.time_input.setTime(QTime.currentTime())
        self.reason_input.clear()
        self.status_input.setCurrentIndex(0)
