import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sqlalchemy import text
from config.config import engine

def add_columns():
    print("Adding found_time and circumstances columns to found_items table...")
    
    with engine.begin() as conn:
        try:
            conn.execute(text("""
                ALTER TABLE found_items 
                ADD COLUMN IF NOT EXISTS found_time VARCHAR(5);
            """))
            
            conn.execute(text("""
                ALTER TABLE found_items 
                ADD COLUMN IF NOT EXISTS circumstances VARCHAR(500);
            """))
            
            print("Columns added successfully!")
        except Exception as e:
            print(f"Error: {e}")
            raise

if __name__ == "__main__":
    add_columns()

