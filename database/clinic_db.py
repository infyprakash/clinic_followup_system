import sqlite3

class PatientDB:
    def __init__(self):
        self.conn = sqlite3.connect("clinic.db")
        self.create_table()
    def create_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS patients(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gender TEXT,
            date_of_birth TEXT,
            phone_number TEXT,
            address TEXT
        )
        """)
        self.conn.commit()
    def insert_patient(self,name,gender,date_of_birth,phone_number,address):
        self.conn.execute("INSERT INTO patients (name,gender,date_of_birth,phone_number,address) values (?,?,?,?,?)",(name,gender,date_of_birth,phone_number,address))
        self.conn.commit()
    def get_all_patients(self):
        return self.conn.execute("SELECT * FROM patients").fetchall()
    def delete_patient(self,id):
        self.conn.execute("DELETE FROM patients WHERE id=?",(id,))
        self.conn.commit()
    def update_patient(self,id,name,gender,date_of_birth,phone_number,address):
        self.conn.execute("UPDATE patients set name=?,gender=?,date_of_birth=?,phone_number=?,address=? WHERE id=?",(name,gender,date_of_birth,phone_number,address,id))
    def get_all(self):
        return self.conn.execute("SELECT id, name FROM patients").fetchall()

    def get_all_with_summary(self):
        return self.conn.execute("""
            SELECT 
                p.id, p.name, p.gender, p.date_of_birth, p.phone_number, p.address,
                IFNULL(appt.total_appointments, 0) as appointments,
                IFNULL(fup.total_followups, 0) as followups
            FROM patients p
            LEFT JOIN (
                SELECT patient_id, COUNT(*) as total_appointments
                FROM appointments
                GROUP BY patient_id
            ) appt ON p.id = appt.patient_id
            LEFT JOIN (
                SELECT patient_id, COUNT(*) as total_followups
                FROM followups
                GROUP BY patient_id
            ) fup ON p.id = fup.patient_id
        """).fetchall()
    

