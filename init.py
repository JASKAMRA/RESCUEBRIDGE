import sqlite3

def init_db():
    conn = sqlite3.connect('donations.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            amount INTEGER,
            purpose TEXT,
            payment_method TEXT,
            anonymous INTEGER,
            date TEXT,
            status TEXT,
            recipient TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()
