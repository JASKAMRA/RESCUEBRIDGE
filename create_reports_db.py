import sqlite3

conn = sqlite3.connect('medicine.db')
cursor = conn.cursor()

# Main report table
cursor.execute('''
DELETE FROM orders;

''')



conn.commit()
conn.close()

print("Tables created.")
