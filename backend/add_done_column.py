import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add the parent directory to sys.path to allow importing from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db/factory_db")

def add_done_column():
    print(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Check if column already exists
            check_query = text("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'stamp_traces' 
                AND COLUMN_NAME = 'done'
            """)
            result = connection.execute(check_query).scalar()
            
            if result > 0:
                print("Column 'done' already exists in 'stamp_traces' table.")
            else:
                print("Adding 'done' column to 'stamp_traces' table...")
                alter_query = text("ALTER TABLE stamp_traces ADD COLUMN done BOOLEAN DEFAULT FALSE")
                connection.execute(alter_query)
                connection.commit()
                print("Successfully added 'done' column.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_done_column()
