from sqlalchemy import create_engine, text
from models.database import init_db
import sqlite3

def table_exists(db_path, table_name):
    """Check if a table exists in the SQLite database."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        return cursor.fetchone() is not None

def get_column_names(db_path, table_name):
    """Retrieve column names of a table in SQLite."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()
        column_names = [column[1] for column in columns_info]
        return column_names

def create_users_table(db_path):
    """Create the users table if it doesn't exist."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(100) NOT NULL
            );
        """)
        conn.commit()
        print("✅ users table created successfully!")

def update_user_schema(db_path):
    """Add new columns to the users table if they don't exist."""
    try:
        # Check if the users table exists
        if not table_exists(db_path, 'users'):
            print("❌ users table does not exist. Creating it...")
            create_users_table(db_path)
        
        # Get existing column names
        column_names = get_column_names(db_path, 'users')
        
        # Add missing columns
        missing_columns = {
            'first_name': 'VARCHAR(100)',
            'surname': 'VARCHAR(100)',
            'id_number': 'VARCHAR(50)',
            'two_factor_enabled': 'INTEGER DEFAULT 0',
            'created_at': 'DATETIME'
        }

        for column, data_type in missing_columns.items():
            if column not in column_names:
                print(f"Adding {column} column to users table...")
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column} {data_type}")
                    conn.commit()
                print(f"✅ {column} column added successfully!")
            else:
                print(f"✅ {column} column already exists.")
        
        return True
    except Exception as e:
        print("❌ Error updating database schema:")
        print(str(e))
        return False
    
if __name__ == "__main__":
    # Replace 'your_database.db' with your actual database path
    update_user_schema('waste_management.db')