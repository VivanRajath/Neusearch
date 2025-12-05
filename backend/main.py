# main.py
import os
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import Base, engine, get_db
import models
import schemas
import httpx
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title="AI Shopping Assistant API")

# Mount static files
# We check if the directory exists to avoid errors in local development if not built
static_dir = Path("static")
if static_dir.exists():
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
Base.metadata.create_all(bind=engine)

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

    products = db.query(models.Product).all()

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
            with httpx.Client(timeout=15) as client:
                client.post(HF_RAG_URL, json=payload)
        except Exception as e:
            print("Error sending to HF:", e)

    return {"message": "All products synced to HuggingFace RAG"}

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
