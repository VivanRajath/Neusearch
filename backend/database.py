# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use environment variable with fallback to local development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://shopping_assistant_db_bl24_user:8JuXTw1qNp4wyvOkGgl4bj6uXfjPhSSo@dpg-d4pdevnpm1nc73cels6g-a/shopping_assistant_db_bl24"
)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Connecting to database at: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'SQLite/Local'}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
