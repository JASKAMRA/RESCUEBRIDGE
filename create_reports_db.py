import sqlite3

conn = sqlite3.connect('medicine.db')
cursor = conn.cursor()

# Main report table


# Table to store multiple images per report
cursor.execute('''
ALTER TABLE orders
ADD status TEXT DEFAULT 'pending';

''')

conn.commit()
conn.close()

print("Tables created.")
