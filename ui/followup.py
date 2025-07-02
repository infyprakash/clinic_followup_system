import csv
from fpdf import FPDF
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDateEdit,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QCheckBox, QFileDialog
)
from PyQt6.QtCore import QDate



# from database.db import FollowUpDB, PatientDB, StatusDB

from database.followup_db import FollowUpDB
from database.appointment_db import AppointmentDB
from database.clinic_db import PatientDB
from database.doctor_db import DoctorDB
from database.setting_db import  StatusDB


class FollowUpManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Follow-Up Management")
        self.setGeometry(200, 200, 900, 450)
        self.db = FollowUpDB()
        self.selected_id = None

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # --- Form Layout ---
        form = QHBoxLayout()
        self.patient_input = QComboBox()
        self.status_input = QComboBox()

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.remarks_input = QLineEdit()
        self.remarks_input.setPlaceholderText("Enter remarks")

        form.addWidget(QLabel("Patient:"))
        form.addWidget(self.patient_input)
        form.addWidget(QLabel("Date:"))
        form.addWidget(self.date_input)
        form.addWidget(QLabel("Status:"))
        form.addWidget(self.status_input)

        layout.addLayout(form)

        form2 = QHBoxLayout()
        form2.addWidget(QLabel("Remarks:"))
        form2.addWidget(self.remarks_input)
        layout.addLayout(form2)


        self.sort_checkbox = QCheckBox("Sort by Follow-up Count")
        self.sort_checkbox.stateChanged.connect(self.refresh_table)
        layout.addWidget(self.sort_checkbox)

        export_layout = QHBoxLayout()
        export_btn_csv = QPushButton("Export to CSV")
        export_btn_pdf = QPushButton("Export to PDF")
        export_btn_csv.clicked.connect(self.export_csv)
        export_btn_pdf.clicked.connect(self.export_pdf)
        export_layout.addWidget(export_btn_csv)
        export_layout.addWidget(export_btn_pdf)
        layout.addLayout(export_layout)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        update_btn = QPushButton("Update")
        delete_btn = QPushButton("Delete")
        clear_btn = QPushButton("Clear")

        add_btn.clicked.connect(self.add_followup)
        update_btn.clicked.connect(self.update_followup)
        delete_btn.clicked.connect(self.delete_followup)
        clear_btn.clicked.connect(self.clear_form)

        for b in [add_btn, update_btn, delete_btn, clear_btn]:
            btn_layout.addWidget(b)

        layout.addLayout(btn_layout)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Patient", "Date", "Remarks", "Status", "Follow-up Count"])
        self.table.cellClicked.connect(self.table_clicked)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.refresh_dropdowns()
        self.refresh_table()

    def refresh_dropdowns(self):
        self.patient_input.clear()
        for pid, name in PatientDB().get_all():
            count = self.db.conn.execute("SELECT COUNT(*) FROM followups WHERE patient_id=?", (pid,)).fetchone()[0]
            self.patient_input.addItem(f"{name} ({count})", pid)

        self.status_input.clear()
        for sid, name in StatusDB().get_all():
            self.status_input.addItem(name, sid)

    def get_selected_ids(self):
        return self.patient_input.currentData(), self.status_input.currentData()

    def add_followup(self):
        patient_id, status_id = self.get_selected_ids()
        date = self.date_input.date().toString("yyyy-MM-dd")
        remarks = self.remarks_input.text().strip()

        if patient_id and date:
            self.db.insert(patient_id, date, remarks, status_id)
            self.refresh_table()
            self.clear_form()
        else:
            QMessageBox.warning(self, "Missing", "Patient and Date are required.")

    def update_followup(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "No selection", "Select a follow-up to update.")
            return

        patient_id, status_id = self.get_selected_ids()
        date = self.date_input.date().toString("yyyy-MM-dd")
        remarks = self.remarks_input.text().strip()

        self.db.update(self.selected_id, patient_id, date, remarks, status_id)
        self.refresh_table()
        self.clear_form()

    def delete_followup(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "No selection", "Select a follow-up to delete.")
            return

        self.db.delete(self.selected_id)
        self.refresh_table()
        self.clear_form()

    def table_clicked(self, row, col):
        self.selected_id = int(self.table.item(row, 0).text())
        self.patient_input.setCurrentText(self.table.item(row, 1).text())
        self.date_input.setDate(QDate.fromString(self.table.item(row, 2).text(), "yyyy-MM-dd"))
        self.remarks_input.setText(self.table.item(row, 3).text())
        self.status_input.setCurrentText(self.table.item(row, 4).text())

    def refresh_table(self):
        self.table.setRowCount(0)
        if self.sort_checkbox.isChecked():
            rows = self.db.get_all_sorted_by_count()
        else:
            rows = self.db.get_all()

        for row in rows:
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)
            for col, val in enumerate(row):
                self.table.setItem(row_index, col, QTableWidgetItem(str(val)))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if path:
            with open(path, 'w', newline='') as file:
                writer = csv.writer(file)
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                writer.writerow(headers)
                for row in range(self.table.rowCount()):
                    row_data = [self.table.item(row, col).text() for col in range(self.table.columnCount())]
                    writer.writerow(row_data)
            QMessageBox.information(self, "Success", "Exported to CSV.")

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            col_width = pdf.w / 6.5
            row_height = 8

            headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            for header in headers:
                pdf.cell(col_width, row_height, header, border=1)
            pdf.ln()

            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    value = self.table.item(row, col).text()
                    pdf.cell(col_width, row_height, value, border=1)
                pdf.ln()

            pdf.output(path)
            QMessageBox.information(self, "Success", "Exported to PDF.")


    def clear_form(self):
        self.selected_id = None
        self.patient_input.setCurrentIndex(0)
        self.status_input.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.remarks_input.clear()
