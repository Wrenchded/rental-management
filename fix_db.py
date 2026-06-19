import sqlite3

# This script only adds the missing column to your existing database
def fix_db():
    conn = sqlite3.connect("rental_management.db")
    cursor = conn.cursor()
    
    try:
        # This adds the column if it's missing; if it already exists, it will just do nothing
        cursor.execute("ALTER TABLE ServiceLogs ADD COLUMN parts_description TEXT DEFAULT 'No parts used'")
        conn.commit()
        print("Successfully added parts_description column!")
    except sqlite3.OperationalError as e:
        print(f"Column likely already exists: {e}")
    
    conn.close()

if __name__ == "__main__":
    fix_db()