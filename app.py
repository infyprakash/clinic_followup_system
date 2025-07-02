import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QHBoxLayout, QVBoxLayout, QStackedWidget, QSizePolicy
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

# Import your 5 UI modules
from ui.patient import PatientManagement
from ui.doctor import DoctorManagement
from ui.settings import SettingsWindow
from ui.appointment import AppointmentBooking
from ui.followup import FollowUpManager
from ui.dashboard import Dashboard


from database.followup_db import FollowUpDB
from database.appointment_db import AppointmentDB
from database.clinic_db import PatientDB
from database.doctor_db import DoctorDB
from database.setting_db import  StatusDB



class MainDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subhekta Polyclinic Pvt. Ltd.")
        self.setGeometry(100, 100, 1100, 600)

        # Main container
        container = QWidget()
        main_layout = QHBoxLayout(container)

        # Left menu
        self.menu_layout = QVBoxLayout()
        self.menu_layout.setSpacing(20)

        # Navigation buttons
        self.btn_dashboard = self.create_nav_button("🏠 Dashboard")
        self.btn_patients = self.create_nav_button("Patients")
        self.btn_doctors = self.create_nav_button("Doctors")
        self.btn_appointments = self.create_nav_button("Appointments")
        self.btn_followups = self.create_nav_button("Follow-Ups")
        self.btn_settings = self.create_nav_button("Settings")


        self.btn_dashboard.clicked.connect(lambda: self.display_page(0))
        self.btn_patients.clicked.connect(lambda: self.display_page(1))
        self.btn_doctors.clicked.connect(lambda: self.display_page(2))
        self.btn_appointments.clicked.connect(lambda: self.display_page(3))
        self.btn_followups.clicked.connect(lambda: self.display_page(4))
        self.btn_settings.clicked.connect(lambda: self.display_page(5))

        for btn in [
            self.btn_dashboard,
            self.btn_patients,
            self.btn_doctors,
            self.btn_appointments,
            self.btn_followups,
            self.btn_settings,
        ]:
            self.menu_layout.addWidget(btn)

        # 🔄 Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.refresh_btn.setFixedHeight(40)
        self.refresh_btn.clicked.connect(self.refresh_all_dropdowns)
        self.menu_layout.addWidget(self.refresh_btn)

        self.menu_layout.addStretch()

        # Create UI modules once and store them
        self.dashboard_ui = Dashboard()
        self.patient_ui = PatientManagement()
        self.doctor_ui = DoctorManagement()
        self.appointment_ui = AppointmentBooking()
        self.followup_ui = FollowUpManager()
        self.settings_ui = SettingsWindow()

        # Right content area (stacked views)
        self.stack = QStackedWidget()
        self.stack.addWidget(self.dashboard_ui)
        self.stack.addWidget(self.patient_ui)
        self.stack.addWidget(self.doctor_ui)
        self.stack.addWidget(self.appointment_ui)
        self.stack.addWidget(self.followup_ui)
        self.stack.addWidget(self.settings_ui)

        # Combine menu and content
        main_layout.addLayout(self.menu_layout, 1)
        main_layout.addWidget(self.stack, 4)

        self.setCentralWidget(container)

    def create_nav_button(self, text, icon_path=None):
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        if icon_path:
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
        return btn

    def display_page(self, index):
        self.stack.setCurrentIndex(index)

    def refresh_all_dropdowns(self):
        """Calls refresh on dropdowns that depend on shared data like patients or doctors."""
        if hasattr(self.followup_ui, "refresh_dropdowns"):
            self.followup_ui.refresh_dropdowns()
        if hasattr(self.appointment_ui, "refresh_dropdowns"):
            self.appointment_ui.refresh_dropdowns()
        if hasattr(self.settings_ui, "refresh_dropdowns"):
            self.settings_ui.refresh_dropdowns()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainDashboard()
    window.show()
    sys.exit(app.exec())





