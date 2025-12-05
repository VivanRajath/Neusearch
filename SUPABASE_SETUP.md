# Supabase PostgreSQL Setup Guide

## 🎯 Overview

This guide shows you how to connect your AI Shopping Assistant to Supabase PostgreSQL instead of running a local database.

## 📋 Prerequisites

- Supabase account ([Sign up free](https://supabase.com))
- Existing Supabase project or create a new one

## 🚀 Steps to Connect

### 1. Get Supabase Connection String

1. Go to [app.supabase.com](https://app.supabase.com)
2. Select your project (or click "New Project")
3. Navigate to **Settings** → **Database**
4. Scroll to **Connection string** section
5. Select **URI** tab
6. Make sure **Transaction** pooler is selected (port 5432)
7. Click **Copy** - it will look like:
   ```
   postgresql://postgres.[project-id]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
   ```
8. **Important**: Replace `[YOUR-PASSWORD]` with your actual database password

### 2. Initialize Database Tables

#### Option A: Using Supabase SQL Editor (Recommended)

1. Go to **SQL Editor** in your Supabase dashboard
2. Click **New Query**
3. Copy and paste the content from `init_db.sql`
4. Click **Run** (or press Ctrl+Enter)

#### Option B: Using Python Script

Run the migration script:
```bash
# Update .env first with your Supabase connection string
python migrate.py
```

### 3. Configure Environment Variables

Edit the `.env` file in your project root:

```env
# Replace with YOUR actual Supabase connection string
DATABASE_URL=postgresql://postgres.[project-id]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# HuggingFace Space URLs (keep as is)
HF_RAG_URL=https://VivanRajath-AI-product.hf.space/index-product
HF_SEARCH_URL=https://VivanRajath-AI-product.hf.space/search
HF_CHAT_URL=https://VivanRajath-AI-product.hf.space/chat

# Scraper Configuration
SCRAPER_SCHEDULE_HOUR=2
```

### 4. Start Services with Supabase

Use the Supabase-specific docker-compose file:

```bash
# Stop current services
docker-compose down

# Start with Supabase configuration
docker-compose -f docker-compose.supabase.yml up --build -d
```

**What changed:**
- ❌ Removed local PostgreSQL container
- ✅ All services now connect to Supabase
- ✅ Data persists in the cloud
- ✅ Better for production deployment

### 5. Verify Connection

Test the backend connection:

```bash
# Check backend health
curl http://localhost:8000/health

# Check products endpoint
curl http://localhost:8000/products

# View backend logs
docker-compose -f docker-compose.supabase.yml logs backend
```

## 🔍 View Data in Supabase

1. Go to Supabase Dashboard → **Table Editor**
2. You should see a `products` table
3. Browse/edit data directly in the UI
4. Run SQL queries in the **SQL Editor**

## 📊 Monitoring

### Check Logs

```bash
# All services
docker-compose -f docker-compose.supabase.yml logs -f

# Specific service
docker-compose -f docker-compose.supabase.yml  logs -f backend
docker-compose -f docker-compose.supabase.yml logs -f scraper
```

### Database Activity

In Supabase Dashboard:
- **Database** → **Roles** - View connections
- **Database** → **Replication** - Monitor performance
- **Logs** → **Postgres Logs** - View queries

## 🎯 Benefits of Using Supabase

✅ **No Local Database**: Saves resources on your machine  
✅ **Cloud Persistence**: Data is safe and backed up  
✅ **Easy Monitoring**: Visual dashboard for all database operations  
✅ **Production Ready**: Same setup works for deployment  
✅ **Free Tier**: 500MB database, enough for thousands of products  
✅ **Real-time**: Built-in support for real-time subscriptions (future feature)  
✅ **Authentication**: Built-in auth system (if needed later)  

## 🔧 Troubleshooting

### Connection Timeout

If services can't connect:
1. Verify your password in the connection string
2. Check Supabase project status (should be "Active")
3. Ensure you're using **Transaction** pooler (port 5432), not Session pooler (port 6543)

### Tables Not Found

Run the initialization:
```bash
python migrate.py
```

Or manually execute `init_db.sql` in Supabase SQL Editor

### Slow Queries

1. Check your Supabase project region (choose closest to you)
2. Consider upgrading from free tier if hitting limits
3. Add indexes if needed (usually not necessary for this app)

## 🔄 Switching Back to Local PostgreSQL

If you need to switch back:

```bash
# Use original docker-compose
docker-compose up --build -d
```

## 🚀 For Production Deployment

When deploying to Render:
1. Add `DATABASE_URL` as environment variable in Render dashboard
2. Use your Supabase connection string
3. All services will automatically connect to Supabase
4. No need for separate database service on Render

## 📝 Notes

- **Connection Pooling**: Supabase handles this automatically
- **Backups**: Supabase backs up daily (paid plans have point-in-time recovery)
- **Scaling**: Supabase handles scaling automatically
- **Cost**: Free tier is sufficient for development and small production loads
