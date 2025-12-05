"""
Scraper Service - Runs the scraper on a daily schedule
"""
import asyncio
import os
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from scrape import run_all_scrapers
import httpx

# Configuration
SCRAPER_HOUR = int(os.getenv("SCRAPER_SCHEDULE_HOUR", "2"))  # Default 2 AM
HF_RAG_URL = os.getenv("HF_RAG_URL", "https://VivanRajath-AI-product.hf.space/index-product")

async def run_scraper_job():
    """Run the scraper and trigger sync"""
    print(f"\n{'='*60}")
    print(f"🕐 Scraper Job Started at {datetime.now()}")
    print(f"{'='*60}\n")
    
    try:
        # Run the scraper
        await run_all_scrapers()
        
        print("\n✅ Scraping completed successfully!")
        
        # Trigger manual sync to ensure all products are in ChromaDB
        print("\n🔄 Triggering sync to ChromaDB...")
        try:
            # The sync service will handle this automatically, but we can also trigger via backend API
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post("http://backend:8000/sync-to-rag")
                if response.status_code == 200:
                    print("✅ Sync triggered successfully!")
                else:
                    print(f"⚠️ Sync trigger returned status {response.status_code}")
        except Exception as sync_error:
            print(f"⚠️ Could not trigger sync (sync service should handle this): {sync_error}")
        
    except Exception as e:
        print(f"\n❌ Scraper job failed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"🏁 Scraper Job Finished at {datetime.now()}")
    print(f"{'='*60}\n")


def scraper_wrapper():
    """Synchronous wrapper for the async scraper"""
    asyncio.run(run_scraper_job())


def main():
    """Main entry point - sets up scheduler and runs indefinitely"""
    print("🚀 Scraper Service Starting...")
    print(f"⏰ Scheduled to run daily at {SCRAPER_HOUR}:00 UTC")
    
    # Create scheduler with UTC timezone
    scheduler = BlockingScheduler(timezone=pytz.UTC)
    
    # Schedule daily scraper at specified hour
    trigger = CronTrigger(hour=SCRAPER_HOUR, minute=0, timezone=pytz.UTC)
    scheduler.add_job(
        scraper_wrapper,
        trigger=trigger,
        id='daily_scraper',
        name='Daily Product Scraper',
        replace_existing=True
    )
    
    print("✅ Scheduler configured successfully!")
    
    
    # Run immediately on startup for initial data load
    print("\n🎬 Running initial scrape on startup...")
    scraper_wrapper()
    
    # Start the scheduler (blocking)
    print("\n⏳ Scheduler started. Waiting for next scheduled run...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Scraper service shutting down...")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
