import sqlite3


class AppointmentDB:
    def __init__(self):
        self.conn = sqlite3.connect("clinic.db")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_table()

    def create_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            reason TEXT,
            status_id INTEGER,
            FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE SET NULL,
            FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE SET NULL,
            FOREIGN KEY(status_id) REFERENCES statuses(id) ON DELETE SET NULL
        )
        """)
        self.conn.commit()

    def insert(self, patient_id, doctor_id, date, time, reason, status_id):
        self.conn.execute("""
            INSERT INTO appointments (patient_id, doctor_id, date, time, reason, status_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (patient_id, doctor_id, date, time, reason, status_id))
        self.conn.commit()

    def update(self, appointment_id, patient_id, doctor_id, date, time, reason, status_id):
        self.conn.execute("""
            UPDATE appointments
            SET patient_id = ?, doctor_id = ?, date = ?, time = ?, reason = ?, status_id = ?
            WHERE id = ?
        """, (patient_id, doctor_id, date, time, reason, status_id, appointment_id))
        self.conn.commit()

    def delete(self, appointment_id):
        self.conn.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        self.conn.commit()

    def get_all(self):
        return self.conn.execute("""
            SELECT a.id, p.name AS patient, p.phone_number, d.name AS doctor, a.date, a.time,
                a.reason, s.name AS status
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN statuses s ON a.status_id = s.id
        """).fetchall()

    def get_by_date(self, date_str):
        return self.conn.execute("""
            SELECT a.date,a.time,a.reason,p.name, d.name, s.name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN statuses s ON a.status_id = s.id
            WHERE a.date = ?
        """, (date_str,)).fetchall()

    def get_all_joined(self):
        return self.conn.execute("""
            SELECT a.date, p.name, d.name, s.name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN statuses s ON a.status_id = s.id
        """).fetchall()
