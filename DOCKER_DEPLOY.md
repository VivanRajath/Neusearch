# AI Shopping Assistant - Docker Deployment Guide

## 🚀 Quick Start with Docker

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### Local Development with Docker

1. **Clone and navigate to the project**:
   ```bash
   cd c:\Users\Vivan Rajath\Desktop\post
   ```

2. **Start all services**:
   ```bash
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL database on port 5432
   - Backend API on http://localhost:8000
   - Frontend on http://localhost:3000
   - Scraper service (runs daily at 2:00 AM UTC)
   - Sync service (continuously monitors for new products)

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Docker Commands

```bash
# Start all services
docker-compose up

# Start in detached mode (background)
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f scraper
docker-compose logs -f sync-service

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Rebuild services after code changes
docker-compose up --build

# Run scraper manually (for testing)
docker-compose exec scraper python scrape.py
```

## 📦 Services Overview

### 1. PostgreSQL Database
- Stores all product data
- Persistent volume for data retention
- Auto-initializes with `init_db.sql`

### 2. Backend API (FastAPI)
- REST API for product management
- Chat interface with HuggingFace RAG
- Health check endpoint at `/health`

### 3. Frontend (React)
- Modern UI for product browsing
- AI-powered chat interface
- Served via nginx in production

### 4. Scraper Service
- Runs daily at 2:00 AM UTC (configurable)
- Scrapes Traya and Hunnit product catalogs
- Automatically saves to PostgreSQL
- Runs initial scrape on startup

### 5. Sync Service
- Monitors PostgreSQL for new/updated products
- Automatically syncs to ChromaDB via HuggingFace Space
- Runs continuously with 30-second check interval
- Performs full sync on startup

## 🌐 Deploying to Render

### Option 1: Using Render Blueprint (Recommended)

1. **Push code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Add Docker configuration"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click "Apply" to create all services

### Option 2: Manual Setup

1. **Create PostgreSQL Database**:
   - New → PostgreSQL
   - Name: `shopping-assistant-db`
   - Plan: Starter (or Free)
   - Note the connection string

2. **Create Backend Web Service**:
   - New → Web Service
   - Connect repository
   - Name: `shopping-assistant-backend`
   - Environment: Docker
   - Dockerfile path: `./Dockerfile.backend`
   - Add environment variables:
     - `DATABASE_URL`: <from PostgreSQL service>
     - `HF_RAG_URL`: https://VivanRajath-AI-product.hf.space/index-product
     - `HF_SEARCH_URL`: https://VivanRajath-AI-product.hf.space/search
     - `HF_CHAT_URL`: https://VivanRajath-AI-product.hf.space/chat
   - Health Check Path: `/health`

3. **Create Frontend Web Service**:
   - New → Web Service
   - Same repository
   - Name: `shopping-assistant-frontend`
   - Environment: Docker
   - Dockerfile path: `./Dockerfile.frontend`

4. **Create Scraper Background Worker**:
   - New → Background Worker
   - Name: `shopping-assistant-scraper`
   - Environment: Docker
   - Dockerfile path: `./Dockerfile.scraper`
   - Add environment variables:
     - `DATABASE_URL`: <from PostgreSQL service>
     - `SCRAPER_SCHEDULE_HOUR`: 2

5. **Create Sync Background Worker**:
   - New → Background Worker
   - Name: `shopping-assistant-sync`
   - Environment: Docker
   - Dockerfile path: `./Dockerfile.backend`
   - Docker Command: `python sync_service.py`
   - Add environment variables:
     - `DATABASE_URL`: <from PostgreSQL service>
     - `HF_RAG_URL`: https://VivanRajath-AI-product.hf.space/index-product

## ⚙️ Configuration

### Environment Variables

Create a `.env` file for local development (see `.env.example`):

```env
DATABASE_URL=postgresql://myapp_user:mypassword@postgres:5432/myapp_db
HF_RAG_URL=https://VivanRajath-AI-product.hf.space/index-product
HF_SEARCH_URL=https://VivanRajath-AI-product.hf.space/search
HF_CHAT_URL=https://VivanRajath-AI-product.hf.space/chat
SCRAPER_SCHEDULE_HOUR=2
```

### Scraper Schedule

Change the scraper execution time by setting `SCRAPER_SCHEDULE_HOUR` (0-23):
- `0` = Midnight UTC
- `2` = 2:00 AM UTC (default)
- `14` = 2:00 PM UTC

## 🧪 Testing

### Test Locally

1. **Verify all services are running**:
   ```bash
   docker-compose ps
   ```

2. **Test backend health**:
   ```bash
   curl http://localhost:8000/health
   ```

3. **Test product listing**:
   ```bash
   curl http://localhost:8000/products
   ```

4. **Manually trigger scraper**:
   ```bash
   docker-compose exec scraper python scrape.py
   ```

5. **Check database**:
   ```bash
   docker-compose exec postgres psql -U myapp_user -d myapp_db -c "SELECT COUNT(*) FROM products;"
   ```

6. **Verify sync service**:
   ```bash
   docker-compose logs sync-service
   ```

## 📊 Monitoring

### View Service Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f scraper
docker-compose logs -f sync-service
docker-compose logs -f backend
```

### Check Service Status

```bash
docker-compose ps
```

### Database Queries

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U myapp_user -d myapp_db

# In psql:
SELECT COUNT(*) FROM products;
SELECT * FROM products WHERE synced_at IS NULL;
SELECT source, COUNT(*) FROM products GROUP BY source;
```

## 🛠️ Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Database connection errors
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres
```

### Scraper not working
```bash
# Check scraper logs
docker-compose logs scraper

# Run manually
docker-compose exec scraper python scrape.py
```

### Sync service not syncing
```bash
# Check sync logs
docker-compose logs sync-service

# Verify products exist
docker-compose exec postgres psql -U myapp_user -d myapp_db -c "SELECT COUNT(*) FROM products WHERE synced_at IS NULL;"
```

## 📝 Notes

- **First Run**: The scraper runs immediately on startup to populate initial data
- **Daily Schedule**: Subsequent scrapes run at the configured hour (default 2:00 AM UTC)
- **Sync Service**: Continuously monitors database and syncs new products every 30 seconds
- **Data Persistence**: PostgreSQL data is stored in a Docker volume and persists across restarts
- **HuggingFace Space**: Ensure your HF Space is running and accessible for RAG to work
