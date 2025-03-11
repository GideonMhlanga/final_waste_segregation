
from dotenv import load_dotenv
from models.database import Base, init_db
import os

def setup_database():
    """Initialize the database and create all tables."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize database
        engine = init_db()
        
        print("✅ Database initialized successfully!")
        print(f"Connected to: {os.getenv('PGDATABASE')} at {os.getenv('PGHOST')}")
        
        return True
    except Exception as e:
        print("❌ Error initializing database:")
        print(str(e))
        return False

if __name__ == "__main__":
    setup_database()

from dotenv import load_dotenv
from models.database import Base, init_db
import os

def setup_database():
    """Initialize the database and create all tables."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize database
        engine = init_db()
        
        print("✅ Database initialized successfully!")
        print(f"Connected to database")
        
        return True
    except Exception as e:
        print("❌ Error initializing database:")
        print(str(e))
        return False

if __name__ == "__main__":
    setup_database()
