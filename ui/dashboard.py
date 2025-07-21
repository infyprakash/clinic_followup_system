from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QGroupBox, QCalendarWidget,
    QTabWidget
)
from PyQt6.QtCore import Qt, QDate
from database.clinic_db import PatientDB
from database.doctor_db import DoctorDB
from database.appointment_db import AppointmentDB
from database.followup_db import FollowUpDB
from PyQt6.QtGui import QColor


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.patient_db = PatientDB()
        self.doctor_db = DoctorDB()
        self.appointment_db = AppointmentDB()
        self.followup_db = FollowUpDB()

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Summary Section
        summary_layout = QHBoxLayout()
        self.total_patients = QLabel("Patients: 0")
        self.total_doctors = QLabel("Doctors: 0")
        self.today_appts = QLabel("Today Appointments: 0")
        self.pending_followups = QLabel("Pending Follow-Ups: 0")
        for label in [self.total_patients, self.total_doctors, self.today_appts, self.pending_followups]:
            label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
            summary_layout.addWidget(label)
        main_layout.addLayout(summary_layout)

        # Tab Widget for Appointment and Follow-up
        self.tabs = QTabWidget()

        # --- Appointment Tab ---
        appt_tab = QWidget()
        appt_layout = QVBoxLayout()

        # Appointment calendar and search
        appt_controls_layout = QHBoxLayout()
        self.appt_calendar = QCalendarWidget()
        self.appt_calendar.setGridVisible(True)
        self.appt_calendar.setSelectedDate(QDate.currentDate())
        self.appt_calendar.selectionChanged.connect(self.on_appt_calendar_date_selected)
        appt_controls_layout.addWidget(self._group_box("📅 Select Date", self.appt_calendar))

        appt_search_layout = QVBoxLayout()
        self.appt_search_input = QLineEdit()
        self.appt_search_input.setPlaceholderText("🔍 Search Appointments by patient name or phone...")
        self.appt_search_input.textChanged.connect(self.refresh_appointments)
        appt_search_layout.addWidget(self._group_box("Search Patient", self.appt_search_input))
        appt_controls_layout.addLayout(appt_search_layout)

        appt_layout.addLayout(appt_controls_layout)

        # Appointment table with wider columns
        self.appt_table = QTableWidget(0, 5)
        self.appt_table.setHorizontalHeaderLabels(["Date", "Patient", "Phone", "Doctor", "Status"])
        self.appt_table.setColumnWidth(0, 100)  # Date
        self.appt_table.setColumnWidth(1, 150)  # Patient
        self.appt_table.setColumnWidth(2, 120)  # Phone
        self.appt_table.setColumnWidth(3, 150)  # Doctor
        self.appt_table.setColumnWidth(4, 100)  # Status

        appt_layout.addWidget(self._group_box("Appointments", self.appt_table))

        appt_tab.setLayout(appt_layout)
        self.tabs.addTab(appt_tab, "Appointments")

        # --- Follow-Up Tab ---
        fup_tab = QWidget()
        fup_layout = QVBoxLayout()

        # Follow-up calendar and search
        fup_controls_layout = QHBoxLayout()
        self.fup_calendar = QCalendarWidget()
        self.fup_calendar.setGridVisible(True)
        self.fup_calendar.setSelectedDate(QDate.currentDate())
        self.fup_calendar.selectionChanged.connect(self.on_fup_calendar_date_selected)
        fup_controls_layout.addWidget(self._group_box("📅 Select Date", self.fup_calendar))

        fup_search_layout = QVBoxLayout()
        self.fup_search_input = QLineEdit()
        self.fup_search_input.setPlaceholderText("🔍 Search Follow-Ups by patient name or phone...")
        self.fup_search_input.textChanged.connect(self.refresh_followups_for_date)
        fup_search_layout.addWidget(self._group_box("Search Patient", self.fup_search_input))
        fup_controls_layout.addLayout(fup_search_layout)

        fup_layout.addLayout(fup_controls_layout)

        # Follow-up table with wider columns
        self.followup_table = QTableWidget(0, 5)
        self.followup_table.setHorizontalHeaderLabels(["Date", "Patient", "Phone", "Remarks", "Status"])
        self.followup_table.setColumnWidth(0, 100)  # Date
        self.followup_table.setColumnWidth(1, 150)  # Patient
        self.followup_table.setColumnWidth(2, 120)  # Phone
        self.followup_table.setColumnWidth(3, 200)  # Remarks
        self.followup_table.setColumnWidth(4, 100)  # Status

        fup_layout.addWidget(self._group_box("Follow-Ups for Selected Date", self.followup_table))

        fup_tab.setLayout(fup_layout)
        self.tabs.addTab(fup_tab, "Follow-Ups")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        # Initial load
        self.refresh_summary()
        self.refresh_appointments()
        self.refresh_followups_for_date()

    def _group_box(self, title, widget):
        box = QGroupBox(title)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        box.setLayout(layout)
        return box

    def refresh_summary(self):
        patients = self.patient_db.get_all()
        doctors = self.doctor_db.get_all()
        today = QDate.currentDate().toString("yyyy-MM-dd")
        today_appts = self.appointment_db.get_by_date(today)
        pending_fups = self.followup_db.get_by_status("Pending")

        self.total_patients.setText(f"Patients: {len(patients)}")
        self.total_doctors.setText(f"Doctors: {len(doctors)}")
        self.today_appts.setText(f"Today Appointments: {len(today_appts)}")
        self.pending_followups.setText(f"Pending Follow-Ups: {len(pending_fups)}")

    def refresh_appointments(self):
        keyword = self.appt_search_input.text().lower()
        selected_date = self.appt_calendar.selectedDate().toString("yyyy-MM-dd")
        data = self.appointment_db.get_by_date(selected_date)

        self.appt_table.setRowCount(0)
        for row in data:
            # Assuming row = [date, patient, doctor, status]
            date, patient, doctor, status = row

            # Fetch patient phone number (you should implement get_phone_by_patient_name)
            phone = self.patient_db.get_phone_by_patient_name(patient) or ""

            # Filter search by patient name or phone
            if keyword and (keyword not in patient.lower() and keyword not in phone):
                continue

            row_pos = self.appt_table.rowCount()
            self.appt_table.insertRow(row_pos)

            values = [date, patient, phone, doctor, status]
            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                self.appt_table.setItem(row_pos, col, item)

            # Apply row color based on status
            if status.lower() == "pending":
                self._set_row_color(self.appt_table, row_pos, "#fff3cd")  # Yellow
            elif status.lower() == "cancelled":
                self._set_row_color(self.appt_table, row_pos, "#f8d7da")  # Red
            elif status.lower() == "completed":
                self._set_row_color(self.appt_table, row_pos, "#d4edda")  # Green

    def refresh_followups_for_date(self):
        keyword = self.fup_search_input.text().lower()
        selected_date = self.fup_calendar.selectedDate().toString("yyyy-MM-dd")
        data = self.followup_db.get_by_date(selected_date)

        self.followup_table.setRowCount(0)
        for row in data:
            # Assuming row = [date, patient, remarks, status]
            date, patient, remarks, status = row

            # Fetch patient phone number
            phone = self.patient_db.get_phone_by_patient_name(patient) or ""

            # Filter by patient name or phone
            if keyword and (keyword not in patient.lower() and keyword not in phone):
                continue

            row_pos = self.followup_table.rowCount()
            self.followup_table.insertRow(row_pos)

            values = [date, patient, phone, remarks, status]
            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                self.followup_table.setItem(row_pos, col, item)

            # Apply row color based on status
            if status.lower() == "pending":
                self._set_row_color(self.followup_table, row_pos, "#fff3cd")  # Yellow
            elif status.lower() == "cancelled":
                self._set_row_color(self.followup_table, row_pos, "#f8d7da")  # Red
            elif status.lower() == "completed":
                self._set_row_color(self.followup_table, row_pos, "#d4edda")  # Green

    def on_appt_calendar_date_selected(self):
        self.refresh_appointments()

    def on_fup_calendar_date_selected(self):
        self.refresh_followups_for_date()

    def _set_row_color(self, table, row_index, color_hex):
        """Apply background color to all cells in a given row."""
        color = QColor(color_hex)
        for col in range(table.columnCount()):
            item = table.item(row_index, col)
            if item:
                item.setBackground(color)
