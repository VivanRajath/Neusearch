# main.py
import os
import time
from datetime import datetime
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from sqlalchemy import or_, text
from database import Base, engine, get_db
import models
import schemas
import httpx
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks
from scrape import run_all_scrapers
import asyncio

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title="AI Shopping Assistant API")

# Mount static files
# We check if the directory exists to avoid errors in local development if not built
# Handle nested static/static structure from React build
static_dir = Path("static")
if (static_dir / "static").exists():
    app.mount("/static", StaticFiles(directory="static/static"), name="static")
elif static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")



# CORS configuration - allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatQuery(BaseModel):
    query: str
    top_k: int = 5

# Create database tables
# Create database tables
Base.metadata.create_all(bind=engine)

# Migration: Ensure synced_at column exists (for existing databases)
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS synced_at TIMESTAMP"))
        conn.commit()
except Exception as e:
    print(f"Migration warning: {e}")

# HuggingFace Space URLs from environment
HF_RAG_URL = os.getenv("HF_RAG_URL", "https://VivanRajath-AI-product.hf.space/index-product")
HF_SEARCH_URL = os.getenv("HF_SEARCH_URL", "https://VivanRajath-AI-product.hf.space/search")
HF_CHAT_URL = os.getenv("HF_CHAT_URL", "https://VivanRajath-AI-product.hf.space/chat")


@app.get("/")
async def serve_spa():
    """Serve the React App"""
    if static_dir.exists():
        return FileResponse("static/index.html")
    return {"message": "AI Shopping Assistant API is running (Frontend not built)"}



# Catch-all for SPA client-side routing
# This must be at the end of the file or after specific API routes
@app.exception_handler(404)
async def custom_404_handler(request, exc):
    path = request.url.path
    # If trying to access a file with extension that doesn't exist, return 404
    # This prevents "Uncaught SyntaxError: Unexpected token '<'" where HTML is returned for JS/CSS
    if "." in path.split("/")[-1] and static_dir.exists():
        return {"detail": "Not Found"}
        
    if static_dir.exists():
        return FileResponse("static/index.html")
    return {"detail": "Not Found"}

@app.get("/api/health")
def health_check():
    """Health check endpoint for container monitoring"""
    return {
        "status": "healthy",
        "service": "AI Shopping Assistant Backend",
        "database": "connected"
    }

@app.post("/add-product")
def add_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # Check if product already exists to avoid duplicates (optional but good)
    existing = db.query(models.Product).filter(models.Product.url == product.url).first()
    if existing:
        return {"message": "Product already exists", "id": existing.id}
    
    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"message": "Product added", "id": new_product.id}

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    return product

@app.post("/sync-to-rag")
def sync_to_rag(db: Session = Depends(get_db)):
    """
    Sync unsynced products to RAG.
    Rate limited to avoid 503 errors from HF/GenAI.
    """
    # Only get products that haven't been synced yet
    # Limit to 20 at a time to prevent timeout
    products = db.query(models.Product).filter(models.Product.synced_at == None).limit(20).all()
    
    if not products:
        return {"message": "No new products to sync"}

    success_count = 0
    
    for p in products:
        payload = {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "features": p.features,
            "category": p.category,
            "url": p.url,
            "image_url": p.images.split(",")[0] if p.images else ""
        }

        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(HF_RAG_URL, json=payload)
                if response.status_code == 200:
                    p.synced_at = datetime.utcnow()
                    db.commit()
                    success_count += 1
                else:
                    print(f"⚠️ Failed to sync product {p.id}: {response.status_code}")
                    
            # Rate limiting: Sleep 2 seconds between requests
            # This prevents "503 UNAVAILABLE" from Google GenAI
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error sending product {p.id} to HF:", e)

    return {"message": f"Synced {success_count} products to HuggingFace RAG"}

@app.post("/chat")
def chat_endpoint(body: ChatQuery):
    """
    Semantic search chatbot using HF Space.
    All search is done via HF vector database, not local DB.
    """
    
    try:
        with httpx.Client(timeout=30) as client:
            
            # Step 1: Get LLM response from HF /chat
            # (HF /chat internally calls /search and formats response)
            chat_payload = {
                "query": body.query,
                "top_k": body.top_k
            }
            
            chat_response = client.post(HF_CHAT_URL, json=chat_payload)
            chat_data = chat_response.json()
            
            # Step 2: Also get search results for product recommendations
            search_payload = {
                "query": body.query,
                "top_k": body.top_k
            }
            
            search_response = client.post(HF_SEARCH_URL, json=search_payload)
            search_data = search_response.json()
            
            # Step 3: Format recommendations from search results
            recommendations = []
            for result in search_data.get("results", []):
                meta = result.get("metadata", {})
                recommendations.append({
                    "title": meta.get("title", ""),
                    "description": meta.get("description", "")[:200],
                    "category": meta.get("category", ""),
                    "url": meta.get("url", ""),
                    "image_url": meta.get("image", ""),
                    "score": result.get("score", 0)
                })
            
            # Step 4: Return combined response
            return {
                "answer": chat_data.get("response", "Here are some products I found for you!"),
                "recommendations": recommendations
            }
            
    except Exception as e:
        return {
            "answer": "I'm having trouble connecting to the search service. Please try again.",
            "recommendations": [],
            "error": str(e)
        }

# Serve specific root files that React expects
# Placed AFTER API routes to avoid shadowing them
@app.get("/{filename}")
async def serve_root_files(filename: str):
    if static_dir.exists():
        # Check root level first
        file_path = static_dir / filename
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
            
    # If file not found in static root, it might be a client-side route
    # Let the 404 handler decide (or return 404 for specific extensions)
    if "." in filename:
         # It's likely a file request, return 404 if not found
         return {"detail": "Not Found"}
    return FileResponse("static/index.html")

# ---------------------------------------------------
# SCRAPER INTEGRATION (For Unified Deployment)
# ---------------------------------------------------

@app.post("/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks):
    """Manually trigger the scraper in the background"""
    background_tasks.add_task(run_all_scrapers)
    return {"message": "Scraping started in background"}

@app.on_event("startup")
async def startup_event():
    """Run scraper on startup to ensure data exists"""
    # We use asyncio.create_task to run it without blocking startup
    asyncio.create_task(run_all_scrapers())
