import sqlite3

conn = sqlite3.connect('reports.db')
cursor = conn.cursor()

# Main report table
cursor.execute('''
CREATE TABLE IF NOT EXISTS reported_animals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT NOT NULL,
    city TEXT NOT NULL,
    landmarks TEXT,
    animal_type TEXT NOT NULL,
    condition TEXT NOT NULL,
    description TEXT,
    phone TEXT NOT NULL,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    status TEXT DEFAULT 'Submitted'
)
''')

# Table to store multiple images per report
cursor.execute('''
CREATE TABLE IF NOT EXISTS animal_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER,
    image BLOB,
    FOREIGN KEY(report_id) REFERENCES reported_animals(id)
)
''')

conn.commit()
conn.close()

print("Tables created.")
