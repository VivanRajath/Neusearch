from database import SessionLocal, engine
from models import Base, Product

# Create tables if not exist (just in case)
Base.metadata.create_all(bind=engine)

def clean_database():
    print("🧹 Cleaning database...")
    db = SessionLocal()
    try:
        num_deleted = db.query(Product).delete()
        db.commit()
        print(f"✅ Deleted {num_deleted} products. Database is now empty.")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_database()
