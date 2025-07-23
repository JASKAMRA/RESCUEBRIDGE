import sqlite3

conn = sqlite3.connect('reports.db')
cursor = conn.cursor()

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

conn.commit()
conn.close()

print("reports.db created successfully with table 'reported_animals'")
