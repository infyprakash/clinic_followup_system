# ui/appointments.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QTimeEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import QDate, QTime, QDateTime

from database.appointment_db import AppointmentDB
from database.clinic_db import PatientDB
from database.doctor_db import DoctorDB
from database.setting_db import  StatusDB


class AppointmentBooking(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Appointment Booking")
        self.setGeometry(100, 100, 900, 500)
        self.db = AppointmentDB()
        self.selected_id = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # --- Form Row 1 ---
        form1 = QHBoxLayout()
        self.patient_input = QComboBox()
        self.doctor_input = QComboBox()

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        # self.time_input = QTimeEdit()
        # self.time_input.setDisplayFormat("HH:mm")
        # self.time_input.setTimeRange(QTime(0, 0), QTime(23, 45))
        # self.time_input.setSingleStep(QTime(0, 15))  # 15-minute intervals

        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")
        self.time_input.setTimeRange(QTime(0, 0), QTime(23, 59))

        form1.addWidget(QLabel("Patient:"))
        form1.addWidget(self.patient_input)
        form1.addWidget(QLabel("Doctor:"))
        form1.addWidget(self.doctor_input)
        form1.addWidget(QLabel("Date:"))
        form1.addWidget(self.date_input)
        form1.addWidget(QLabel("Time:"))
        form1.addWidget(self.time_input)

        layout.addLayout(form1)

        # --- Form Row 2 ---
        form2 = QHBoxLayout()
        self.reason_input = QLineEdit()
        self.status_input = QComboBox()

        form2.addWidget(QLabel("Reason:"))
        form2.addWidget(self.reason_input)
        form2.addWidget(QLabel("Status:"))
        form2.addWidget(self.status_input)

        layout.addLayout(form2)

        # --- Buttons ---
        btns = QHBoxLayout()
        add_btn = QPushButton("Add")
        update_btn = QPushButton("Update")
        delete_btn = QPushButton("Delete")
        clear_btn = QPushButton("Clear")

        add_btn.clicked.connect(self.add_appointment)
        update_btn.clicked.connect(self.update_appointment)
        delete_btn.clicked.connect(self.delete_appointment)
        clear_btn.clicked.connect(self.clear_form)

        for b in [add_btn, update_btn, delete_btn, clear_btn]:
            btns.addWidget(b)
        layout.addLayout(btns)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Patient", "Doctor", "Date", "Time", "Reason", "Status"])
        self.table.cellClicked.connect(self.table_clicked)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.refresh_dropdowns()
        self.refresh_table()

    def refresh_dropdowns(self):
        # Populate patient
        self.patient_input.clear()
        for pid, name in PatientDB().get_all():
            self.patient_input.addItem(name, pid)

        # Populate doctor
        self.doctor_input.clear()
        for did, name in DoctorDB().get_all():
            self.doctor_input.addItem(name, did)

        # Populate status
        self.status_input.clear()
        for sid, name in StatusDB().get_all():
            self.status_input.addItem(name, sid)

    def get_selected_ids(self):
        return (
            self.patient_input.currentData(),
            self.doctor_input.currentData(),
            self.status_input.currentData()
        )

    def add_appointment(self):
        patient_id, doctor_id, status_id = self.get_selected_ids()
        date = self.date_input.date().toString("yyyy-MM-dd")
        time = self.time_input.time().toString("HH:mm")
        reason = self.reason_input.text().strip()

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
        self.patient_input.setCurrentText(self.table.item(row, 1).text())
        self.doctor_input.setCurrentText(self.table.item(row, 2).text())
        self.date_input.setDate(QDate.fromString(self.table.item(row, 3).text(), "yyyy-MM-dd"))
        self.time_input.setTime(QTime.fromString(self.table.item(row, 4).text(), "HH:mm"))
        self.reason_input.setText(self.table.item(row, 5).text())
        self.status_input.setCurrentText(self.table.item(row, 6).text())

    def refresh_table(self):
        self.table.setRowCount(0)
        for row in self.db.get_all():
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)
            for col, val in enumerate(row):
                self.table.setItem(row_index, col, QTableWidgetItem(str(val)))

    def clear_form(self):
        self.selected_id = None
        self.patient_input.setCurrentIndex(0)
        self.doctor_input.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.time_input.setTime(QTime(0, 0))
        self.reason_input.clear()
        self.status_input.setCurrentIndex(0)