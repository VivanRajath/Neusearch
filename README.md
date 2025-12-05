# Neusearch AI - AI Product Discovery Assistant
> **AI Engineering Intern - Technical Assignment**

A mini AI-powered product discovery assistant designed to understand abstract user queries and recommend relevant products using retrieval-augmented generation (RAG).

🔗 **Live Demo:** [https://neusearch.onrender.com/](https://neusearch.onrender.com/)

---

## 🚀 Overview
This project is an end-to-end e-commerce solution that includes:
1.  **Data Pipeline:** Automated scraping of product data from live e-commerce sites (Hunnit, Traya).
2.  **Vector Search:** Semantic search capabilities powered by a dedicated RAG service hosted on HuggingFace Spaces.
3.  **AI Assistant:** A chatbot that interprets user intent (e.g., "gym wear," "dry scalp") and provides curated recommendations.
4.  **Modern UI:** A clean, responsive React frontend.

## 🏗️ Architecture

The system is built as a **Unified Monolith** for simplified deployment on the Render Free Tier, while offloading heavy AI processing to a separate microservice.

### Components
*   **Frontend:** React (SPA) served via FastAPI static mounting.
*   **Backend:** FastAPI (Python) handling API requests, database interactions, and scraper orchestration.
*   **Database:** PostgreSQL (Relational Data) + ChromaDB (Vector Data on HF Space).
*   **RAG Service:** Hosted separately on [HuggingFace Spaces](https://huggingface.co/spaces/VivanRajath/AI-product) to leverage GPU resources and persistent vector storage.

### Data Flow
1.  **Scrape:** The `BackgroundTasks` in FastAPI scrape product data from target websites.
2.  **Store:** Structured data (Title, Price, Features) is stored in PostgreSQL.
3.  **Sync:** A background job batches new products and pushes them to the HuggingFace RAG service, where embeddings are generated and stored in ChromaDB.
4.  **Query:** User asks a question in the React Chat UI -> Backend acts as a proxy -> RAG Service retrieves relevant context and generates a response using the LLM (Gemini via Google GenAI).

---

## 🛠️ Tech Stack
*   **Language:** Python 3.11, JavaScript (React)
*   **Frameworks:** FastAPI, React.js
*   **Database:** PostgreSQL, SQLAlchemy
*   **AI/ML:** LangChain, ChromaDB, Google Gemini (GenAI), Sentence Transformers
*   **Deployment:** Docker, Render, HuggingFace Spaces

---

## 🏃‍♂️ Running Locally

This project is fully containerized using Docker.

### Prerequisites
*   Docker & Docker Compose
*   Git

### Steps
1.  **Clone the repository**
    ```bash
    git clone https://github.com/VivanRajath/Neusearch.git
    cd Neusearch
    ```

2.  **Configure Environment**
    Create a `.env` file in the root directory (variables are pre-configured for local dev in `docker-compose.yml`, but for production you need these):
    ```env
    DATABASE_URL=postgresql://user:password@db:5432/myapp_db
    HF_RAG_URL=https://VivanRajath-AI-product.hf.space/index-product
    HF_SEARCH_URL=https://VivanRajath-AI-product.hf.space/search
    HF_CHAT_URL=https://VivanRajath-AI-product.hf.space/chat
    ```

3.  **Build and Run**
    ```bash
    docker-compose up --build
    ```

4.  **Access the App**
    *   Frontend & API: `http://localhost:8000`
    *   Docs: `http://localhost:8000/docs`

5.  **Initialize Data**
    The scraper runs automatically on startup. If you see an empty catalog, you can trigger it manually:
    ```bash
    curl -X POST http://localhost:8000/scrape
    ```

---

## 🚢 Deployment (Render)

The application is deployed as a single Web Service on Render to maximize free tier efficiency.

*   **Build Command:** Wrapper around `docker build`.
*   **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 8000`
*   **Docker Strategy:** A multi-stage `Dockerfile` (in the root) builds the React frontend and copies the static assets into the Python container. FastAPI serves these files, effectively simplifying the architecture to a single deployable unit.

### Deployment Challenges & Solutions
*   **Challenge:** Render Free Tier puts services to sleep.
    *   **Solution:** Validated automatic wake-up and database reconnection logic.
*   **Challenge:** "Empty Vector DB" errors due to HF Space restarts.
    *   **Solution:** Implemented a `/force-resync` endpoint and a UI "Refresh Data" button that clears the sync history and re-populates the vector database on demand.
*   **Challenge:** Google GenAI Rate Limits (503 Unavailable).
    *   **Solution:** Implemented robust rate-limiting (2s delay) and batch processing in the RAG sync pipeline.

---

## 🧠 Design Decisions & Trade-offs

1.  **Unified Dockerfile:**
    *   *Decision:* Serve Frontend via Backend.
    *   *Trade-off:* Increases backend image size slightly, but simplifies deployment (1 service vs 2) and eliminates CORS issues entirely.

2.  **Separate RAG Service:**
    *   *Decision:* Host RAG on HuggingFace Spaces.
    *   *Trade-off:* Adds network latency to chat responses, but keeps the main application lightweight and allows the RAG/Vector component to scale independently (or run on better hardware).

3.  **Scraping Strategy:**
    *   *Decision:* On-demand/Startup scraping instead of scheduled cron (due to environment limits).
    *   *Trade-off:* Data might be slightly stale if the app sleeps for days, but it guarantees fresh data on every new deployment/restart.

---

## 🔮 Future Improvements
If I had more time, I would:
1.  **Enhance Scrapers:** Add more robust handling for dynamic JS-heavy sites using Playwright (already installed but used selectively).
2.  **User Personalization:** Store user chat history and preferences to tailor recommendations over time.
3.  **Advanced RAG:** Implement "Hybrid Search" (combining Keyword + Vector search) for better accuracy on specific product names (e.g., SKU search).
4.  **Caching:** Redis cache for frequent queries to reduce latency and API costs.

---

*Submitted by Vivan Rajath for Neusearch AI.*
