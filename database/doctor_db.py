import sqlite3

class DoctorDB:
    def __init__(self):
        self.conn = sqlite3.connect("clinic.db")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_table()

    def create_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization_id INTEGER,
            FOREIGN KEY(specialization_id) REFERENCES specializations(id) ON DELETE SET NULL
        )
        """)
        self.conn.commit()

    def insert(self, name, specialization_id):
        self.conn.execute(
            "INSERT INTO doctors (name, specialization_id) VALUES (?, ?)",
            (name, specialization_id)
        )
        self.conn.commit()

    def get_all(self):
        return self.conn.execute("""
            SELECT d.id, d.name, s.name AS specialization
            FROM doctors d
            LEFT JOIN specializations s ON d.specialization_id = s.id
        """).fetchall()

    def delete(self, doctor_id):
        self.conn.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
        self.conn.commit()

    def update(self, doctor_id, name, specialization_id):
        self.conn.execute(
            "UPDATE doctors SET name = ?, specialization_id = ? WHERE id = ?",
            (name, specialization_id, doctor_id)
        )
        self.conn.commit()
    def get_all(self):
        return self.conn.execute("SELECT id, name FROM doctors").fetchall()