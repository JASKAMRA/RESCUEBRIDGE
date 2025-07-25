import sqlite3

def init_db():
    conn = sqlite3.connect('ngo_pets.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ngo_pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ngo_email TEXT NOT NULL,
            name TEXT NOT NULL,
            breed TEXT NOT NULL,
            injury TEXT NOT NULL,
            medication TEXT NOT NULL,
            type TEXT NOT NULL,
            dosage TEXT NOT NULL,
            frequency TEXT NOT NULL,
            days_left INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ngo_email) REFERENCES ngos("Email")
        )
    ''')
    conn.commit()
    conn.close()

init_db()