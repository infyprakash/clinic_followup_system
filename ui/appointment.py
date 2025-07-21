from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QTimeEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QListWidget, QListWidgetItem, QSizePolicy,QFormLayout,QFrame
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

        input_font = QFont("Arial", 12)

        # --- Left: Form ---
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)

        # Patient search input
        self.patient_search_input = QLineEdit()
        self.patient_search_input.setPlaceholderText("Type patient name or phone...")
        self.patient_search_input.setFont(input_font)
        self.patient_search_input.setMinimumWidth(400)
        self.patient_search_input.setMinimumHeight(35)
        self.patient_search_input.textChanged.connect(self.on_patient_search)

        self.patient_list_widget = QListWidget()
        self.patient_list_widget.setMaximumHeight(100)
        self.patient_list_widget.itemClicked.connect(self.on_patient_selected)

        # Doctor dropdown
        self.doctor_input = QComboBox()
        self.doctor_input.setFont(input_font)
        self.doctor_input.setMinimumWidth(400)
        self.doctor_input.setMinimumHeight(35)

        # Date
        self.date_input = QDateEdit()
        self.date_input.setFont(input_font)
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMinimumWidth(400)
        self.date_input.setMinimumHeight(35)

        # Time
        self.time_input = QTimeEdit()
        self.time_input.setFont(input_font)
        self.time_input.setDisplayFormat("hh:mm AP")
        self.time_input.setTimeRange(QTime(0, 0), QTime(23, 59))
        self.time_input.setMinimumWidth(400)
        self.time_input.setMinimumHeight(35)

        # Reason input
        self.reason_input = QLineEdit()
        self.reason_input.setFont(input_font)
        self.reason_input.setMinimumWidth(400)
        self.reason_input.setMinimumHeight(35)

        # Status dropdown
        self.status_input = QComboBox()
        self.status_input.setFont(input_font)
        self.status_input.setMinimumWidth(400)
        self.status_input.setMinimumHeight(35)

        # Add fields to form layout
        form_layout.addRow("🔎 Search Patient:", self.patient_search_input)
        form_layout.addRow("", self.patient_list_widget)
        form_layout.addRow("👨‍⚕️ Doctor:", self.doctor_input)
        form_layout.addRow("📅 Date:", self.date_input)
        form_layout.addRow("⏰ Time:", self.time_input)
        form_layout.addRow("📝 Reason:", self.reason_input)
        form_layout.addRow("📌 Status:", self.status_input)

        # --- Right: Buttons ---
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

        self.add_btn = styled_button("➕ Add", "#28a745")
        self.update_btn = styled_button("🔄 Update", "#007bff")
        self.delete_btn = styled_button("🗑️ Delete", "#dc3545")
        self.clear_btn = styled_button("🧹 Clear", "#6c757d")

        self.add_btn.clicked.connect(self.add_appointment)
        self.update_btn.clicked.connect(self.update_appointment)
        self.delete_btn.clicked.connect(self.delete_appointment)
        self.clear_btn.clicked.connect(self.clear_form)

        for btn in [self.add_btn, self.update_btn, self.delete_btn, self.clear_btn]:
            button_layout.addWidget(btn)

        button_layout.addStretch()

        # Add to main horizontal layout
        main_layout.addLayout(form_layout, 2)
        main_layout.addLayout(button_layout, 1)

        # --- Overall layout with table ---
        overall_layout = QVBoxLayout()
        overall_layout.setContentsMargins(20, 20, 20, 20)
        overall_layout.addLayout(main_layout)

        # --- Separator ---
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        overall_layout.addWidget(separator)

        # Search field for table
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search appointment by patient, doctor or status...")
        self.search_input.setFont(input_font)
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("padding: 6px;")
        self.search_input.textChanged.connect(self.refresh_table)
        overall_layout.addWidget(self.search_input)

        # Appointment table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Patient", "Phone", "Doctor", "Date", "Time", "Reason", "Status"])
        self.table.setFont(QFont("Arial", 11))
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
        patient_phone = self.table.item(row, 2).text()

        self.selected_patient_id = None
        for pid, name, phone in self.patient_db.get_all():
            if name == patient_name and phone == patient_phone:
                self.selected_patient_id = pid
                self.patient_search_input.setText(f"{name} ({phone})")
                break

        self.doctor_input.setCurrentText(self.table.item(row, 3).text())
        self.date_input.setDate(QDate.fromString(self.table.item(row, 4).text(), "yyyy-MM-dd"))
        self.time_input.setTime(QTime.fromString(self.table.item(row, 5).text(), "hh:mm AP"))
        self.reason_input.setText(self.table.item(row, 6).text())
        self.status_input.setCurrentText(self.table.item(row, 7).text())



    def refresh_table(self):
        keyword = self.search_input.text().lower()
        self.table.setRowCount(0)

        for row in self.db.get_all():
            # row = [id, patient_name, patient_phone, doctor_name, date, time, reason, status]
            if keyword:
                if not (
                    keyword in str(row[1]).lower()
                    or keyword in str(row[2]).lower()
                    or keyword in str(row[3]).lower()
                    or keyword in str(row[7]).lower()
                ):
                    continue

            row_index = self.table.rowCount()
            self.table.insertRow(row_index)

            status = str(row[7]).lower()

            if status == "pending":
                background_color = QColor("#FFFACD")
            elif status == "cancelled":
                background_color = QColor("#F08080")
            elif status == "completed":
                background_color = QColor("#90EE90")
            else:
                background_color = QColor("white")

            for col, val in enumerate(row):
                if col == 5:  # Time formatting
                    try:
                        time_obj = QTime.fromString(val, "HH:mm")
                        val = time_obj.toString("hh:mm AP")
                    except Exception:
                        pass

                item = QTableWidgetItem(str(val))
                item.setBackground(background_color)
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
