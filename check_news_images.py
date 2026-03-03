from db_config import get_connection, DB_SCHEMA
import os

def check_news_images():
    print(f"--- NBA News Image Audit ---")
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Database Counts
    cur.execute(f'SELECT count(*) FROM "{DB_SCHEMA}"."News"')
    total = cur.fetchone()[0]
    
    cur.execute(f'SELECT count(*) FROM "{DB_SCHEMA}"."News" WHERE "ImageURL" IS NOT NULL')
    db_images = cur.fetchone()[0]
    
    cur.execute(f'SELECT count(*) FROM "{DB_SCHEMA}"."News" WHERE "ImageStatus" = \'completed\'')
    completed_status = cur.fetchone()[0]
    
    print(f"Total News Articles: {total}")
    print(f"Articles with ImageURL in DB: {db_images} ({db_images/total:.1%})")
    print(f"Articles with 'completed' ImageStatus: {completed_status}")
    
    # 2. File System Check
    cur.execute(f'SELECT "NewsID", "ImageURL" FROM "{DB_SCHEMA}"."News" WHERE "ImageURL" IS NOT NULL LIMIT 500')
    rows = cur.fetchall()
    
    exists_count = 0
    missing_count = 0
    
    for news_id, url in rows:
        if url and os.path.exists(url):
            exists_count += 1
        else:
            missing_count += 1
            
    print(f"\nPhysical File Check (sampled first {len(rows)}):")
    print(f"  - Files found: {exists_count}")
    print(f"  - Files missing: {missing_count}")
    
    # 3. List recent news without images
    print("\nRecent News WITHOUT Images:")
    cur.execute(f'SELECT "NewsID", "Title", "Date" FROM "{DB_SCHEMA}"."News" WHERE "ImageURL" IS NULL ORDER BY "Date" DESC LIMIT 5')
    no_images = cur.fetchall()
    for row in no_images:
        print(f"  - [{row[2]}] (ID: {row[0]}) {row[1]}")
        
    conn.close()

if __name__ == "__main__":
    check_news_images()
