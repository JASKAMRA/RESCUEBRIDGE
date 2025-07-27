import sqlite3
import os

def column_exists(cursor, table_name, column_name):
    """
    Checks if a column exists in the specified table.
    """
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    return column_name in columns

def add_price_per_column():
    """
    Adds 'price_per' column to medicines table if it doesn't exist.
    """
    db_path = 'medicine.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' does not exist.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if column_exists(cursor, 'medicines', 'price_per'):
        print("ℹ️ Column 'price_per' already exists in 'medicines' table.")
    else:
        try:
            cursor.execute("ALTER TABLE medicines ADD COLUMN price_per INTEGER;")
            conn.commit()
            print("✅ Column 'price_per' added to 'medicines' table.")
        except sqlite3.OperationalError as e:
            print(f"❌ Error adding column: {e}")

    conn.close()

if __name__ == "__main__":
    print("➕ Adding column 'price_per' to medicines table")
    add_price_per_column()
