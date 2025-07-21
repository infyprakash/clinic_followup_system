import sqlite3
class FollowUpDB:
    def __init__(self):
        self.conn = sqlite3.connect("clinic.db")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS followups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doctor_id INTEGER,
                date TEXT,
                remarks TEXT,
                status_id INTEGER,
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(id),
                FOREIGN KEY (status_id) REFERENCES statuses(id)
            )
        """)
        self.conn.commit()

    def insert(self, patient_id, doctor_id, date, remarks, status_id):
        self.conn.execute("""
            INSERT INTO followups (patient_id, doctor_id, date, remarks, status_id)
            VALUES (?, ?, ?, ?, ?)
        """, (patient_id, doctor_id, date, remarks, status_id))
        self.conn.commit()

    def update(self, id, patient_id, doctor_id, date, remarks, status_id):
        self.conn.execute("""
            UPDATE followups
            SET patient_id=?, doctor_id=?, date=?, remarks=?, status_id=?
            WHERE id=?
        """, (patient_id, doctor_id, date, remarks, status_id, id))
        self.conn.commit()

    def delete(self, id):
        self.conn.execute("DELETE FROM followups WHERE id=?", (id,))
        self.conn.commit()

    def get_all(self):
        return self.conn.execute("""
            SELECT f.id, p.name, p.phone_number, d.name AS doctor_name, f.date,
                   f.remarks, s.name AS status,
                   (SELECT COUNT(*) FROM followups WHERE patient_id = f.patient_id) AS followup_count
            FROM followups f
            LEFT JOIN patients p ON f.patient_id = p.id
            LEFT JOIN doctors d ON f.doctor_id = d.id
            LEFT JOIN statuses s ON f.status_id = s.id
        """).fetchall()


    def get_patient_followup_counts(self):
        return self.conn.execute("""
            SELECT p.name, COUNT(f.id) as count
            FROM patients p
            LEFT JOIN followups f ON p.id = f.patient_id
            GROUP BY p.id
        """).fetchall()

    def get_all_sorted_by_count(self, descending=True):
        order = "DESC" if descending else "ASC"
        return self.conn.execute(f"""
            SELECT f.id, p.name, f.date, f.remarks, s.name AS status,
                (SELECT COUNT(*) FROM followups WHERE patient_id = f.patient_id) AS followup_count
            FROM followups f
            LEFT JOIN patients p ON f.patient_id = p.id
            LEFT JOIN statuses s ON f.status_id = s.id
            ORDER BY followup_count {order}
        """).fetchall()

    def get_by_status(self, status_name):
        return self.conn.execute("""
            SELECT f.date, p.name, f.remarks, s.name
            FROM followups f
            JOIN patients p ON f.patient_id = p.id
            JOIN statuses s ON f.status_id = s.id
            WHERE s.name = ?
        """, (status_name,)).fetchall()

    def get_all_joined(self):
        return self.conn.execute("""
            SELECT f.date, p.name, f.remarks, s.name
            FROM followups f
            JOIN patients p ON f.patient_id = p.id
            JOIN statuses s ON f.status_id = s.id
        """).fetchall()

    def get_by_date(self, date_str):
        return self.conn.execute("""
            SELECT f.date, p.name, f.remarks, s.name
            FROM followups f
            JOIN patients p ON f.patient_id = p.id
            JOIN statuses s ON f.status_id = s.id
            WHERE f.date = ?
        """, (date_str,)).fetchall()
