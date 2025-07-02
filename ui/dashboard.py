from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QGroupBox, QCalendarWidget
)
from PyQt6.QtCore import Qt, QDate
from database.clinic_db import PatientDB
from database.doctor_db import DoctorDB
from database.appointment_db import AppointmentDB
from database.followup_db import FollowUpDB


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.patient_db = PatientDB()
        self.doctor_db = DoctorDB()
        self.appointment_db = AppointmentDB()
        self.followup_db = FollowUpDB()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 🔁 Calendar widget to filter follow-ups
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.selectionChanged.connect(self.on_calendar_date_selected)
        layout.addWidget(self._group_box("📅 Select Date to View Follow-Ups", self.calendar))

        # 🔁 Top Summary Boxes
        summary_layout = QHBoxLayout()
        self.total_patients = QLabel("Patients: 0")
        self.total_doctors = QLabel("Doctors: 0")
        self.today_appts = QLabel("Today Appointments: 0")
        self.pending_followups = QLabel("Pending Follow-Ups: 0")

        for label in [self.total_patients, self.total_doctors, self.today_appts, self.pending_followups]:
            label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
            summary_layout.addWidget(label)

        layout.addLayout(summary_layout)

        # 🔁 Search bar for appointments
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search Appointments by patient name...")
        self.search_input.textChanged.connect(self.refresh_appointments)
        layout.addWidget(self.search_input)

        # Appointments Table
        self.appt_table = QTableWidget(0, 4)
        self.appt_table.setHorizontalHeaderLabels(["Date", "Patient", "Doctor", "Status"])
        layout.addWidget(self._group_box("Appointments", self.appt_table))

        # Follow-up Table
        self.followup_table = QTableWidget(0, 4)
        self.followup_table.setHorizontalHeaderLabels(["Date", "Patient", "Remarks", "Status"])
        layout.addWidget(self._group_box("Follow-Ups for Selected Date", self.followup_table))

        self.setLayout(layout)

        # Initial load
        self.refresh_summary()
        self.refresh_appointments()
        self.refresh_followups_for_date(QDate.currentDate())

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
        keyword = self.search_input.text().lower()
        data = self.appointment_db.get_all_joined()

        self.appt_table.setRowCount(0)
        for row in data:
            date, patient, doctor, status = row
            if keyword and keyword not in patient.lower():
                continue
            row_pos = self.appt_table.rowCount()
            self.appt_table.insertRow(row_pos)
            for col, val in enumerate(row):
                self.appt_table.setItem(row_pos, col, QTableWidgetItem(str(val)))

    def refresh_followups_for_date(self, qdate: QDate):
        """Get follow-ups by selected date."""
        date_str = qdate.toString("yyyy-MM-dd")
        data = self.followup_db.get_by_date(date_str)

        self.followup_table.setRowCount(0)
        for row in data:
            row_pos = self.followup_table.rowCount()
            self.followup_table.insertRow(row_pos)
            for col, val in enumerate(row):
                self.followup_table.setItem(row_pos, col, QTableWidgetItem(str(val)))

    def on_calendar_date_selected(self):
        selected_date = self.calendar.selectedDate()
        self.refresh_followups_for_date(selected_date)
