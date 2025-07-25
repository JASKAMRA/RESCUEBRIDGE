import sqlite3
import os

def create_medicine_database():
    """
    Medicine database create karta hai required table ke saath
    """
    # Database file path
    db_path = 'medicine.db'
    
    # Database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Medicine table create karna
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_name TEXT NOT NULL,
            no_of_boxes INTEGER NOT NULL DEFAULT 0,
            restock_level INTEGER NOT NULL DEFAULT 0,
            shopkeeper_email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shopkeeper_email) REFERENCES shopkeepers("Email")
        )
    ''')
    
    # Index create karna faster searching ke liye
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_medicine_name 
        ON medicines(medicine_name)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_shopkeeper_email 
        ON medicines(shopkeeper_email)
    ''')
    
    # Changes commit karna
    conn.commit()
    print(f"✅ Medicine database '{db_path}' successfully created!")
    print("📋 Table 'medicines' with columns: id, medicine_name, no_of_boxes, restock_level, shopkeeper_email, created_at")
    
    # Connection close karna
    conn.close()

def check_database_exists():
    """
    Check karta hai ki database file exist karti hai ya nahi
    """
    db_path = 'medicine.db'
    if os.path.exists(db_path):
        print(f"📁 Database file '{db_path}' already exists")
        return True
    else:
        print(f"📁 Database file '{db_path}' does not exist")
        return False

if __name__ == "__main__":
    print("🏥 Medicine Database Initialization")
    print("=" * 40)
    
    # Check if database already exists
    if not check_database_exists():
        print("🔧 Creating new database...")
        create_medicine_database()
    else:
        choice = input("Database already exists. Recreate? (y/n): ").lower()
        if choice == 'y':
            create_medicine_database()
        else:
            print("⏭️ Skipping database creation")
    
    print("\n✨ Initialization complete!")