# Quick Start Guide

## Prerequisites

```powershell
# Install Python dependencies
pip install playwright asgiref sqlalchemy psycopg2-binary fastapi uvicorn apscheduler httpx

# Install Playwright browser
playwright install chromium
```

## Running the Application

### 1. Setup Database (First Time Only)

```powershell
python migrate.py
```

### 2. Run the Scraper

```powershell
python scrape.py
```

This will scrape products from Traya and Hunnit and save them directly to PostgreSQL.

### 3. Start the Backend

```powershell
uvicorn main:app --reload
```

Backend runs at: `http://localhost:8000`

### 4. Start the Frontend

```powershell
cd frontend
npm start
```

Frontend opens at: `http://localhost:3000`

---

## Key Features

✨ **Dark Theme** - Modern, sleek dark UI with gradient accents
🎨 **Smooth Animations** - Fade-ins, hovers, and transitions
🛍️ **Two Sources** - Traya (Hair products) & Hunnit (Clothing)
💾 **Direct DB** - Scrapers save directly to PostgreSQL
🔄 **Real-time** - React fetches from FastAPI backend

---

## Troubleshooting

**Scraper fails?**
- Check internet connection
- Ensure Playwright Chromium is installed
- Verify website URLs are accessible

**Database errors?**
- Ensure PostgreSQL is running
- Check credentials in `database.py`
- Run `python migrate.py`

**Frontend not showing products?**
- Ensure backend is running (`uvicorn main:app --reload`)
- Check `http://localhost:8000/products` returns data
- Verify CORS is enabled in `main.py`
