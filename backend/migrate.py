from database import engine
from sqlalchemy import text

def migrate():
    try:
        with engine.connect() as conn:

            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS source VARCHAR(50)"))
            conn.commit()
            print("Migration successful: Added 'source' column to 'products' table.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
