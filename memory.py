import sqlite3


class Memory:

    def __init__(self, database="akhim_memory.db"):
        self.database = database
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.database)

    def create_table(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def save(self, role, message):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO messages (role, message) VALUES (?, ?)",
            (role, message)
        )

        conn.commit()
        conn.close()

    def get_recent(self, limit=20):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT role, message
            FROM messages
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        rows.reverse()

        return rows

    def clear(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM messages")

        conn.commit()
        conn.close()
