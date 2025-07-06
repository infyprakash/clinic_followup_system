from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QDateEdit, QTableWidget, QTableWidgetItem, QMessageBox,
    QListWidget, QListWidgetItem, QSizePolicy
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont,QColor


from database.followup_db import FollowUpDB
from database.clinic_db import PatientDB
from database.setting_db import StatusDB


class FollowUpManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Follow-Up Management")
        self.setGeometry(100, 100, 1000, 500)
        self.db = FollowUpDB()
        self.patient_db = PatientDB()
        self.status_db = StatusDB()
        self.selected_id = None
        self.selected_patient_id = None
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # --- Top Section: Form and Buttons (side by side) ---
        top_layout = QHBoxLayout()

        # ----- Left Form Section -----
        form_layout = QVBoxLayout()

        # Searchable patient
        form_layout.addWidget(QLabel("Search Patient (Name or Phone):"))
        self.patient_search_input = QLineEdit()
        self.patient_search_input.setPlaceholderText("Start typing to search patient...")
        self.patient_search_input.textChanged.connect(self.on_patient_search)
        form_layout.addWidget(self.patient_search_input)

        self.patient_list_widget = QListWidget()
        self.patient_list_widget.setMaximumHeight(80)
        self.patient_list_widget.itemClicked.connect(self.on_patient_selected)
        form_layout.addWidget(self.patient_list_widget)

        # Status
        form_layout.addWidget(QLabel("Status:"))
        self.status_input = QComboBox()
        form_layout.addWidget(self.status_input)

        # Date
        form_layout.addWidget(QLabel("Follow-up Date:"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addWidget(self.date_input)

        # Remarks
        form_layout.addWidget(QLabel("Remarks:"))
        self.remarks_input = QLineEdit()
        form_layout.addWidget(self.remarks_input)

        top_layout.addLayout(form_layout, 2)

        # ----- Right Button Section -----
        button_layout = QVBoxLayout()

        self.add_btn = QPushButton("Add")
        self.update_btn = QPushButton("Update")
        self.delete_btn = QPushButton("Delete")
        self.clear_btn = QPushButton("Clear")

        for btn, color in zip(
            [self.add_btn, self.update_btn, self.delete_btn, self.clear_btn],
            ["#4CAF50", "#2196F3", "#f44336", "#9E9E9E"]
        ):
            btn.setStyleSheet(f"""
                background-color: {color};
                color: white;
                font-weight: bold;
                font-size: 16px;
                min-height: 40px;
            """)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button_layout.addWidget(btn)

        button_layout.addStretch()
        top_layout.addLayout(button_layout, 1)

        main_layout.addLayout(top_layout)


        # --- Bottom Section: Search + Table ---
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by patient name or phone...")
        self.search_input.textChanged.connect(self.refresh_table)
        main_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Patient", "Date", "Remarks", "Status", "Follow-up Count"])
        self.table.cellClicked.connect(self.table_clicked)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        # Connect button actions
        self.add_btn.clicked.connect(self.add_followup)
        self.update_btn.clicked.connect(self.update_followup)
        self.delete_btn.clicked.connect(self.delete_followup)
        self.clear_btn.clicked.connect(self.clear_form)

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
        self.status_input.clear()
        for sid, name in self.status_db.get_all():
            self.status_input.addItem(name, sid)

        self.load_patient_list()

    def get_selected_ids(self):
        return self.selected_patient_id, self.status_input.currentData()

    def add_followup(self):
        patient_id, status_id = self.get_selected_ids()
        date = self.date_input.date().toString("yyyy-MM-dd")
        remarks = self.remarks_input.text().strip()

        if not patient_id:
            QMessageBox.warning(self, "Validation Error", "Please select a patient.")
            return

        self.db.insert(patient_id, date, remarks, status_id)
        self.refresh_table()
        self.clear_form()

    def update_followup(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "No Selection", "Select a follow-up to update.")
            return

        patient_id, status_id = self.get_selected_ids()
        date = self.date_input.date().toString("yyyy-MM-dd")
        remarks = self.remarks_input.text().strip()

        self.db.update(self.selected_id, patient_id, date, remarks, status_id)
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

        for pid, name, phone in self.patient_db.get_all():
            display = f"{name} ({phone})"
            if name in patient_name:
                self.selected_patient_id = pid
                self.patient_search_input.setText(display)
                break

        self.date_input.setDate(QDate.fromString(self.table.item(row, 2).text(), "yyyy-MM-dd"))
        self.remarks_input.setText(self.table.item(row, 3).text())
        self.status_input.setCurrentText(self.table.item(row, 4).text())

    def refresh_table(self):
        keyword = self.search_input.text().lower()
        rows = self.db.get_all()

        self.table.setRowCount(0)
        for row in rows:
            if keyword and keyword not in row[1].lower():
                continue
            
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)

            # Assuming follow-up status is in column index 6 (adjust if different)
            follow_up_status = str(row[4]).lower()

            # Define colors based on follow-up status
            if follow_up_status == "pending":
                background_color = QColor("#FFFACD")  # Light yellow
            elif follow_up_status == "cancelled":
                background_color = QColor("#F08080")  # Light coral (red-ish)
            elif follow_up_status == "completed":
                background_color = QColor("#90EE90")  # Light green
            else:
                background_color = QColor("white")  # Default

            for col, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setBackground(background_color)
                self.table.setItem(row_index, col, item)

    def clear_form(self):
        self.selected_id = None
        self.selected_patient_id = None
        self.patient_search_input.clear()
        self.patient_list_widget.clear()
        self.status_input.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.remarks_input.clear()
