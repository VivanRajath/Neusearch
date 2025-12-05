from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from google import genai
import numpy as np
import uuid
import os

# --------------------------
# LLM CONFIG
# --------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.5-flash"

# --------------------------
# FASTAPI APP
# --------------------------
app = FastAPI()

# --------------------------
# EMBEDDING MODEL
# --------------------------
embedder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")


# --------------------------
# CHROMA VECTOR STORE
# --------------------------
chroma_client = chromadb.PersistentClient(path="./vector_store")
collection = chroma_client.get_or_create_collection(
    name="products",
    metadata={"hnsw:space": "cosine"}
)

# --------------------------
# PRODUCT INDEXING ENDPOINT
# --------------------------
class Product(BaseModel):
    id: int
    title: str
    description: str
    features: str
    category: str
    url: str
    image_url: str


@app.post("/index-product")
def index_product(product: Product):
    text = (
        f"Title: {product.title}\n"
        f"Category: {product.category}\n"
        f"Description: {product.description}\n"
        f"Features: {product.features}\n"
        f"URL: {product.url}\n"
    )

    emb = embedder.encode(text).tolist()

    collection.upsert(
        ids=[str(product.id)],
        embeddings=[emb],
        metadatas=[{
            "title": product.title,
            "description": product.description,
            "category": product.category,
            "features": product.features,
            "url": product.url,
            "image": product.image_url,
        }],
        documents=[text]
    )

    return {"message": "indexed", "product_id": product.id}

# --------------------------
# SEARCH ENDPOINT
# --------------------------
class Query(BaseModel):
    query: str
    top_k: int = 5


@app.post("/search")
def search_products(body: Query):
    q_emb = embedder.encode(body.query).tolist()

    results = collection.query(
        query_embeddings=[q_emb],
        n_results=body.top_k
    )

    output = []
    for meta, score in zip(results["metadatas"][0], results["distances"][0]):
        output.append({
            "metadata": meta,
            "score": float(score)
        })

    return {"results": output}

# --------------------------
# CHATBOT ENDPOINT
# --------------------------
class ChatRequest(BaseModel):
    query: str
    top_k: int = 5


@app.post("/chat")
def chat(body: ChatRequest):

    # --------------------------
    # Encode Query
    # --------------------------
    q_emb = embedder.encode(body.query).tolist()

    results = collection.query(
        query_embeddings=[q_emb],
        n_results=body.top_k
    )

    raw_metas = results["metadatas"][0]
    raw_distances = results["distances"][0]

    # --------------------------
    # Filter noisy / irrelevant results
    # Cosine distance close to 0 = good match
    # We keep only results with >0.30 similarity
    # similarity = 1 - distance
    # --------------------------
    filtered = []
    for meta, dist in zip(raw_metas, raw_distances):
        similarity = 1 - dist
        if similarity >= 0.30:  # threshold to control noise
            filtered.append((meta, similarity))

    # If no meaningful results → fallback response
    if not filtered:
        return {"response": "I don’t have yoga items in your collection yet. Want me to add some?"}

    # Sort by highest similarity
    filtered.sort(key=lambda x: x[1], reverse=True)

    # Pick top 3 for cleaner LLM prompt
    top_items = filtered[:3]

    # --------------------------
    # Build product context for LLM
    # --------------------------
    blocks = ""
    for meta, sim in top_items:
        blocks += (
            f"Product:\n"
            f"Title: {meta['title']}\n"
            f"Category: {meta['category']}\n"
            f"Description: {meta['description']}\n"
            f"URL: {meta['url']}\n"
            f"Image: {meta['image']}\n"
            f"Relevance: {sim:.2f}\n\n"
        )

    # --------------------------
    # LLM Prompt
    # --------------------------
    prompt = f"""
You are an AI shopping assistant. Recommend ONLY from the retrieved products below.

USER QUERY:
{body.query}

RETRIEVED PRODUCTS:
{blocks}

RULES:
1. Recommend only from these products.
2. Show 2–3 options max.
3. Keep responses short and helpful.
4. If they seem interested in yoga items, focus on the most relevant match.

Now give the final recommendation.
"""

    # Call Gemini
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return {"response": response.text}
