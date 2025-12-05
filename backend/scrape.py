import asyncio
import requests
import json
import re
from asgiref.sync import sync_to_async
from models import Product
from database import SessionLocal


def clean_html(raw_html):
    """Remove HTML tags, scripts, and styles to get clean text"""
    if not raw_html:
        return ""
    
    # Remove script and style elements content
    cleanr = re.compile('<script.*?>.*?</script>', re.DOTALL)
    cleantext = re.sub(cleanr, '', raw_html)
    
    cleanr = re.compile('<style.*?>.*?</style>', re.DOTALL)
    cleantext = re.sub(cleanr, '', cleantext)
    
    # Remove HTML tags
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', cleantext)
    
    # Replace HTML entities
    cleantext = cleantext.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    
    return " ".join(cleantext.split()) 



def save_product(db, url, source, title, price, description, images, category, features):
    """Synchronous function to save product to database"""
    try:
        existing = db.query(Product).filter(Product.url == url).first()
        if existing:
            # Update existing product
            existing.source = source
            existing.title = title
            existing.price = price
            existing.description = description
            existing.images = images
            existing.category = category
            existing.features = features
        else:
            # Create new product
            new_product = Product(
                url=url,
                source=source,
                title=title,
                price=price,
                description=description,
                images=images,
                category=category,
                features=features
            )
            db.add(new_product)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f" Database error: {e}")


async def scrape_shopify_site(site_name, base_url, default_category, limit_per_page=250):
    print(f"\n🔵 [{site_name}] Starting scrape via JSON API (Paginated)...")
    
    page = 1
    saved_count = 0
    db = SessionLocal()
    
    try:
        while True:
            api_url = f"{base_url}/products.json?limit={limit_per_page}&page={page}"
            print(f" [{site_name}] Fetching page {page}...")
            
            response = await asyncio.to_thread(requests.get, api_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
            
            if response.status_code != 200:
                print(f" [{site_name}] Failed to fetch page {page}: {response.status_code}")
                break

            data = response.json()
            products = data.get("products", [])
            
            if not products:
                print(f" [{site_name}] No more products found at page {page}.")
                break
            
            print(f"[{site_name}] Page {page}: Found {len(products)} products")
            
            for p in products:
                try:
                    title = p.get("title")
                    handle = p.get("handle")
                    product_url = f"{base_url}/products/{handle}"
                    
                    # Description
                    body_html = p.get("body_html", "")
                    description = clean_html(body_html)
                    
                    # Images
                    images_list = [img.get("src") for img in p.get("images", [])]
                    images_str = ", ".join(images_list) # Store all images
                    
                    # Price (from first variant)
                    variants = p.get("variants", [])
                    price = "0"
                    if variants:
                        raw_price = variants[0].get("price", "0")
                        try:
                            price_float = float(raw_price)
                            price = str(int(price_float)) if price_float.is_integer() else str(price_float)
                        except:
                            price = raw_price
                    
                    if price == "0":
                        continue

                    # Category & Features
                    category = p.get("product_type") or default_category
                    features = ", ".join(p.get("tags", [])) if p.get("tags") else ""

                    # Save to DB
                    await sync_to_async(save_product)(
                        db=db,
                        url=product_url,
                        source=site_name,
                        title=title,
                        price=price,
                        description=description[:1000],
                        images=images_str,
                        category=category,
                        features=features
                    )
                    saved_count += 1
                    print(f" [{site_name}] Saved: {title[:30]}... (₹{price})")
                    
                except Exception as e:
                    print(f" [{site_name}] Error processing product: {e}")
                    continue
            
            page += 1
            await asyncio.sleep(1) 
            
    except Exception as e:
        print(f" [{site_name}] Fatal error: {e}")
    finally:
        db.close()
        
    print(f" [{site_name}] Completed - {saved_count} products saved.")



# MAIN RUNNER

async def run_all_scrapers():
    print(" Starting all scrapers (JSON Method)...")
    print("=" * 60)
    
    # Scrape Traya
    await scrape_shopify_site("Traya", "https://traya.health", "Hair & Wellness")
    
    # Scrape Hunnit
    await scrape_shopify_site("Hunnit", "https://www.hunnit.com", "Clothing")
    
    print("\n" + "=" * 60)
    print("🎉 All scrapers completed!")


if __name__ == "__main__":
    asyncio.run(run_all_scrapers())
