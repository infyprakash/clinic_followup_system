from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QGroupBox, QCalendarWidget,
    QTabWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
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
        main_layout = QVBoxLayout()

        # Summary
        summary_layout = QHBoxLayout()
        self.total_patients = QLabel("Patients: 0")
        self.total_doctors = QLabel("Doctors: 0")
        self.today_appts = QLabel("Today Appointments: 0")
        self.pending_followups = QLabel("Pending Follow-Ups: 0")

        for label in [self.total_patients, self.total_doctors, self.today_appts, self.pending_followups]:
            label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
            summary_layout.addWidget(label)

        main_layout.addLayout(summary_layout)

        self.tabs = QTabWidget()

        # --- Appointments Tab ---
        appt_tab = QWidget()
        appt_layout = QVBoxLayout()

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

        # Appointment table with new columns
        self.appt_table = QTableWidget(0, 7)
        self.appt_table.setHorizontalHeaderLabels(["Date", "Time", "Reason", "Patient", "Phone", "Doctor", "Status"])
        for i, width in enumerate([90, 70, 150, 130, 110, 130, 90]):
            self.appt_table.setColumnWidth(i, width)

        appt_layout.addWidget(self._group_box("Appointments", self.appt_table))
        appt_tab.setLayout(appt_layout)
        self.tabs.addTab(appt_tab, "Appointments")

        # --- Follow-up Tab ---
        fup_tab = QWidget()
        fup_layout = QVBoxLayout()

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

        # Follow-up table with new columns
        self.followup_table = QTableWidget(0, 7)
        self.followup_table.setHorizontalHeaderLabels([
            "Date", "Patient", "Phone", "Doctor", "Follow-Up Count", "Remarks", "Status"
        ])
        for i, width in enumerate([90, 130, 110, 130, 120, 180, 90]):
            self.followup_table.setColumnWidth(i, width)

        fup_layout.addWidget(self._group_box("Follow-Ups for Selected Date", self.followup_table))
        fup_tab.setLayout(fup_layout)
        self.tabs.addTab(fup_tab, "Follow-Ups")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        # Initial Data Load
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
            # [date, time, reason, patient, doctor, status]
            date, time, reason, patient, doctor, status = row
            phone = self.patient_db.get_phone_by_patient_name(patient) or ""

            if keyword and (keyword not in patient.lower() and keyword not in phone):
                continue

            row_pos = self.appt_table.rowCount()
            self.appt_table.insertRow(row_pos)

            values = [date, time, reason, patient, phone, doctor, status]
            for col, val in enumerate(values):
                self.appt_table.setItem(row_pos, col, QTableWidgetItem(str(val)))

            self._set_row_color(self.appt_table, row_pos, status)

    def refresh_followups_for_date(self):
        keyword = self.fup_search_input.text().lower()
        selected_date = self.fup_calendar.selectedDate().toString("yyyy-MM-dd")
        data = self.followup_db.get_by_date(selected_date)

        self.followup_table.setRowCount(0)
        for row in data:
            # [date, patient, doctor, followup_count, remarks, status]
            date, patient, doctor, followup_count, remarks, status = row
            phone = self.patient_db.get_phone_by_patient_name(patient) or ""

            if keyword and (keyword not in patient.lower() and keyword not in phone):
                continue

            row_pos = self.followup_table.rowCount()
            self.followup_table.insertRow(row_pos)

            values = [date, patient, phone, doctor, followup_count, remarks, status]
            for col, val in enumerate(values):
                self.followup_table.setItem(row_pos, col, QTableWidgetItem(str(val)))

            self._set_row_color(self.followup_table, row_pos, status)

    def on_appt_calendar_date_selected(self):
        self.refresh_appointments()

    def on_fup_calendar_date_selected(self):
        self.refresh_followups_for_date()

    def _set_row_color(self, table, row_index, status):
        color = "#ffffff"
        if status.lower() == "pending":
            color = "#fff3cd"
        elif status.lower() == "cancelled":
            color = "#f8d7da"
        elif status.lower() == "completed":
            color = "#d4edda"

        for col in range(table.columnCount()):
            item = table.item(row_index, col)
            if item:
                item.setBackground(QColor(color))
