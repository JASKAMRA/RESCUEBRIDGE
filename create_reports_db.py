import sqlite3

conn = sqlite3.connect('reports.db')
cursor = conn.cursor()

# Main report table
cursor.execute('''
ALTER TABLE reported_animals ADD COLUMN handled_by TEXT;

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
