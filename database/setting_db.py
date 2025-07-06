import sqlite3

# database/db.py

class SpecializationDB:
    def __init__(self):
        self.conn = sqlite3.connect("clinic.db")
        self.create_table()

    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS specializations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        self.conn.commit()

    def insert(self, name):
        self.conn.execute("INSERT OR IGNORE INTO specializations (name) VALUES (?)", (name,))
        self.conn.commit()

    def get_all(self):
        return self.conn.execute("SELECT * FROM specializations").fetchall()

    def delete(self, id):
        self.conn.execute("DELETE FROM specializations WHERE id=?", (id,))
        self.conn.commit()


class StatusDB:
    def __init__(self):
        self.conn = sqlite3.connect("clinic.db")
        self.create_table()
        self.seed_statuses()

    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS statuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        self.conn.commit()

    def insert(self, name):
        self.conn.execute("INSERT OR IGNORE INTO statuses (name) VALUES (?)", (name,))
        self.conn.commit()

    def seed_statuses(self):
        default_statuses = ["Pending", "Completed", "Cancelled"]
        for status in default_statuses:
            self.insert(status)

    def get_all(self):
        return self.conn.execute("SELECT * FROM statuses").fetchall()

    def delete(self, id):
        self.conn.execute("DELETE FROM statuses WHERE id=?", (id,))
        self.conn.commit()
