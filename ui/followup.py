from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QDateEdit, QTableWidget, QTableWidgetItem, QMessageBox,
    QListWidget, QListWidgetItem, QSizePolicy,QFormLayout,QFrame
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QFont

from database.followup_db import FollowUpDB
from database.clinic_db import PatientDB
from database.setting_db import StatusDB
from database.doctor_db import DoctorDB  # ⬅️ You need to have this

class FollowUpManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Follow-Up Management")
        self.setGeometry(100, 100, 1100, 500)
        self.db = FollowUpDB()
        self.patient_db = PatientDB()
        self.status_db = StatusDB()
        self.doctor_db = DoctorDB()
        self.selected_id = None
        self.selected_patient_id = None
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        top_layout = QHBoxLayout()

        input_font = QFont("Arial", 12)

        # ----- Left Form -----
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)

        # Patient Search
        self.patient_search_input = QLineEdit()
        self.patient_search_input.setPlaceholderText("Start typing to search patient...")
        self.patient_search_input.setFont(input_font)
        self.patient_search_input.setMinimumWidth(400)
        self.patient_search_input.setMinimumHeight(35)
        self.patient_search_input.textChanged.connect(self.on_patient_search)

        self.patient_list_widget = QListWidget()
        self.patient_list_widget.setMaximumHeight(80)
        self.patient_list_widget.itemClicked.connect(self.on_patient_selected)

        # Doctor
        self.doctor_input = QComboBox()
        self.doctor_input.setFont(input_font)
        self.doctor_input.setMinimumWidth(400)
        self.doctor_input.setMinimumHeight(35)

        # Status
        self.status_input = QComboBox()
        self.status_input.setFont(input_font)
        self.status_input.setMinimumWidth(400)
        self.status_input.setMinimumHeight(35)

        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setFont(input_font)
        self.date_input.setMinimumWidth(400)
        self.date_input.setMinimumHeight(35)

        # Remarks
        self.remarks_input = QLineEdit()
        self.remarks_input.setFont(input_font)
        self.remarks_input.setMinimumWidth(400)
        self.remarks_input.setMinimumHeight(35)

        form_layout.addRow("🔍 Search Patient:", self.patient_search_input)
        form_layout.addRow("", self.patient_list_widget)
        form_layout.addRow("👨‍⚕️ Doctor:", self.doctor_input)
        form_layout.addRow("📌 Status:", self.status_input)
        form_layout.addRow("📅 Follow-up Date:", self.date_input)
        form_layout.addRow("📝 Remarks:", self.remarks_input)

        top_layout.addLayout(form_layout, 2)

        # ----- Right Buttons -----
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

        self.add_btn.clicked.connect(self.add_followup)
        self.update_btn.clicked.connect(self.update_followup)
        self.delete_btn.clicked.connect(self.delete_followup)
        self.clear_btn.clicked.connect(self.clear_form)

        for btn in [self.add_btn, self.update_btn, self.delete_btn, self.clear_btn]:
            button_layout.addWidget(btn)

        button_layout.addStretch()
        top_layout.addLayout(button_layout, 1)

        main_layout.addLayout(top_layout)

        # --- Separator ---
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # --- Table Search ---
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by patient, phone, or doctor name...")
        self.search_input.setFont(input_font)
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("padding: 6px;")
        self.search_input.textChanged.connect(self.refresh_table)
        main_layout.addWidget(self.search_input)

        # --- Table View ---
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Patient", "Phone", "Doctor", "Date", "Remarks", "Status", "Follow-up Count"
        ])
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

        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        self.refresh_dropdowns()
        self.refresh_table()


    def on_patient_search(self, text):
        self.load_patient_list(text)

    def on_patient_selected(self, item):
        self.selected_patient_id = item.data(Qt.ItemDataRole.UserRole)
        self.patient_search_input.setText(item.text())
        self.patient_list_widget.clear()

    def load_patient_list(self, filter_text=""):
        self.patient_list_widget.clear()
        patients = self.patient_db.get_all()
        filter_text = filter_text.lower()
        for pid, name, phone in patients:
            if filter_text in name.lower() or filter_text in phone.lower():
                item = QListWidgetItem(f"{name} ({phone})")
                item.setData(Qt.ItemDataRole.UserRole, pid)
                self.patient_list_widget.addItem(item)

    def refresh_dropdowns(self):
        # Status
        self.status_input.clear()
        for sid, name in self.status_db.get_all():
            self.status_input.addItem(name, sid)

        # Doctor
        self.doctor_input.clear()
        for did, name in self.doctor_db.get_all():
            self.doctor_input.addItem(name, did)

        self.load_patient_list()

    def get_selected_ids(self):
        return self.selected_patient_id, self.doctor_input.currentData(), self.status_input.currentData()

    def add_followup(self):
        patient_id, doctor_id, status_id = self.get_selected_ids()
        date = self.date_input.date().toString("yyyy-MM-dd")
        remarks = self.remarks_input.text().strip()

        if not patient_id:
            QMessageBox.warning(self, "Validation Error", "Please select a patient.")
            return

        self.db.insert(patient_id, doctor_id, date, remarks, status_id)
        self.refresh_table()
        self.clear_form()

    def update_followup(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "No Selection", "Select a follow-up to update.")
            return

        patient_id, doctor_id, status_id = self.get_selected_ids()
        date = self.date_input.date().toString("yyyy-MM-dd")
        remarks = self.remarks_input.text().strip()

        self.db.update(self.selected_id, patient_id, doctor_id, date, remarks, status_id)
        self.refresh_table()
        self.clear_form()

    def delete_followup(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "No Selection", "Select a follow-up to delete.")
            return

        self.db.delete(self.selected_id)
        self.refresh_table()
        self.clear_form()

    def table_clicked(self, row, col):
        self.selected_id = int(self.table.item(row, 0).text())
        patient_name = self.table.item(row, 1).text()
        patient_phone = self.table.item(row, 2).text()
        doctor_name = self.table.item(row, 3).text()

        for pid, name, phone in self.patient_db.get_all():
            if name == patient_name and phone == patient_phone:
                self.selected_patient_id = pid
                self.patient_search_input.setText(f"{name} ({phone})")
                break

        self.date_input.setDate(QDate.fromString(self.table.item(row, 4).text(), "yyyy-MM-dd"))
        self.remarks_input.setText(self.table.item(row, 5).text())
        self.status_input.setCurrentText(self.table.item(row, 6).text())
        self.doctor_input.setCurrentText(doctor_name)

    def refresh_table(self):
        keyword = self.search_input.text().lower()
        rows = self.db.get_all()

        self.table.setRowCount(0)
        for row in rows:
            patient_name = row[1].lower()
            patient_phone = row[2].lower()
            doctor_name = row[3].lower()

            if keyword and keyword not in patient_name and keyword not in patient_phone and keyword not in doctor_name:
                continue

            row_index = self.table.rowCount()
            self.table.insertRow(row_index)

            status = str(row[6]).lower()
            if status == "pending":
                background_color = QColor("#FFFACD")
            elif status == "cancelled":
                background_color = QColor("#F08080")
            elif status == "completed":
                background_color = QColor("#90EE90")
            else:
                background_color = QColor("white")

            for col, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setBackground(background_color)
                self.table.setItem(row_index, col, item)

    def clear_form(self):
        self.selected_id = None
        self.selected_patient_id = None
        self.patient_search_input.clear()
        self.patient_list_widget.clear()
        self.doctor_input.setCurrentIndex(0)
        self.status_input.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.remarks_input.clear()
