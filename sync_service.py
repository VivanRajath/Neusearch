"""
Sync Service - Monitors PostgreSQL for new products and syncs to ChromaDB
"""
import os
import time
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import httpx
from models import Product

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myapp_user:mypassword@localhost:5432/myapp_db")
HF_RAG_URL = os.getenv("HF_RAG_URL", "https://VivanRajath-AI-product.hf.space/index-product")
SYNC_INTERVAL = 30  # Check every 30 seconds

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def sync_product_to_chromadb(product: Product):
    """Sync a single product to ChromaDB via HuggingFace Space"""
    try:
        payload = {
            "id": product.id,
            "title": product.title,
            "description": product.description,
            "features": product.features,
            "category": product.category,
            "url": product.url,
            "image_url": product.images.split(",")[0] if product.images else ""
        }
        
        with httpx.Client(timeout=15) as client:
            response = client.post(HF_RAG_URL, json=payload)
            
            if response.status_code == 200:
                print(f"✅ Synced product #{product.id}: {product.title[:50]}...")
                return True
            else:
                print(f"⚠️ Failed to sync product #{product.id}: Status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error syncing product #{product.id}: {e}")
        return False


def sync_unsynced_products():
    """Find and sync all products that haven't been synced to ChromaDB yet"""
    db = SessionLocal()
    synced_count = 0
    
    try:
        # Find products without synced_at timestamp (new products)
        unsynced_products = db.query(Product).filter(
            (Product.synced_at == None) | (Product.updated_at > Product.synced_at)
        ).all()
        
        if unsynced_products:
            print(f"\n🔄 Found {len(unsynced_products)} unsynced products")
            
            for product in unsynced_products:
                if sync_product_to_chromadb(product):
                    # Mark as synced
                    product.synced_at = datetime.utcnow()
                    db.commit()
                    synced_count += 1
                    
                time.sleep(0.5)  # Rate limiting
                
            print(f"✅ Sync batch completed: {synced_count}/{len(unsynced_products)} products synced\n")
        
    except Exception as e:
        print(f"❌ Error during sync batch: {e}")
        db.rollback()
    finally:
        db.close()
    
    return synced_count


def initial_full_sync():
    """Perform initial full sync of all products"""
    print("\n" + "="*60)
    print("🚀 Starting Initial Full Sync to ChromaDB")
    print("="*60 + "\n")
    
    db = SessionLocal()
    try:
        all_products = db.query(Product).all()
        total = len(all_products)
        
        if total == 0:
            print("ℹ️ No products found in database. Waiting for scraper...")
            return
        
        print(f"📦 Found {total} total products in database")
        
        synced = 0
        for i, product in enumerate(all_products, 1):
            print(f"[{i}/{total}] Syncing: {product.title[:40]}...")
            
            if sync_product_to_chromadb(product):
                product.synced_at = datetime.utcnow()
                db.commit()
                synced += 1
            
            time.sleep(0.5)  # Rate limiting
        
        print(f"\n✅ Initial sync completed: {synced}/{total} products synced to ChromaDB\n")
        
    except Exception as e:
        print(f"❌ Error during initial sync: {e}")
        db.rollback()
    finally:
        db.close()


def monitor_and_sync():
    """Continuously monitor for new products and sync them"""
    print("👀 Monitoring PostgreSQL for new products...")
    print(f"⏱️ Check interval: {SYNC_INTERVAL} seconds\n")
    
    while True:
        try:
            synced_count = sync_unsynced_products()
            
            if synced_count > 0:
                print(f"✨ Synced {synced_count} new/updated products at {datetime.now()}")
            
            time.sleep(SYNC_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 Sync service shutting down...")
            break
        except Exception as e:
            print(f"⚠️ Monitoring error: {e}")
            time.sleep(SYNC_INTERVAL)


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🔄 PostgreSQL to ChromaDB Sync Service")
    print("="*60 + "\n")
    
    print(f"📊 Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'connected'}")
    print(f"🤗 HuggingFace: {HF_RAG_URL}")
    print()
    
    # Wait a bit for database to be ready
    print("⏳ Waiting for database to be ready...")
    time.sleep(5)
    
    # Perform initial full sync
    initial_full_sync()
    
    # Start continuous monitoring
    monitor_and_sync()


if __name__ == "__main__":
    main()
