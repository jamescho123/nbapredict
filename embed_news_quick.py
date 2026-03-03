"""
Quick News Embedding Script
Embeds recently imported news articles with progress tracking
"""

import logging
import time
from datetime import datetime
from news_embedding import setup_database, fetch_news_without_embeddings, get_embedding, update_news_with_embedding

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler("embedding_progress.log"),
        logging.StreamHandler()
    ]
)

def embed_recent_news(batch_size=50, max_articles=500):
    """Embed recently imported news articles"""
    print("\n" + "="*70)
    print("NBA News Embedding - Quick Update")
    print("="*70 + "\n")
    
    logging.info("Starting news embedding process")
    
    # Setup database
    print("🔧 Setting up database...")
    if not setup_database():
        print("❌ Database setup failed")
        return
    print("✅ Database ready\n")
    
    total_processed = 0
    total_successful = 0
    total_failed = 0
    
    start_time = time.time()
    
    while total_processed < max_articles:
        # Fetch batch
        remaining = max_articles - total_processed
        current_batch_size = min(batch_size, remaining)
        
        news_batch = fetch_news_without_embeddings(current_batch_size)
        
        if not news_batch:
            print("\n✅ No more articles to embed")
            break
        
        batch_count = len(news_batch)
        print(f"\n📦 Batch {total_processed//batch_size + 1}: Processing {batch_count} articles...")
        
        successful = 0
        failed = 0
        
        # Process each article
        for idx, (news_id, title, content) in enumerate(news_batch, 1):
            try:
                # Combine title and content
                full_text = f"{title}\n\n{content}"
                
                # Progress indicator
                print(f"  [{idx}/{batch_count}] Embedding: {title[:60]}...", end=" ")
                
                # Get embedding
                embedding = get_embedding(full_text)
                
                if embedding:
                    # Update news with embedding
                    if update_news_with_embedding(news_id, embedding):
                        print("✅")
                        successful += 1
                    else:
                        print("❌ Update failed")
                        failed += 1
                else:
                    print("❌ Embedding failed")
                    failed += 1
                
                # Brief pause
                time.sleep(0.3)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                failed += 1
        
        # Update totals
        total_processed += batch_count
        total_successful += successful
        total_failed += failed
        
        # Show batch summary
        print(f"\n  📊 Batch Summary:")
        print(f"     Success: {successful}/{batch_count}")
        print(f"     Failed: {failed}/{batch_count}")
        print(f"     Total Progress: {total_successful}/{total_processed}")
        
        # Time estimate
        elapsed = time.time() - start_time
        avg_time = elapsed / total_processed if total_processed > 0 else 0
        remaining_articles = max_articles - total_processed
        estimated_remaining = avg_time * remaining_articles
        
        if remaining_articles > 0 and total_processed < max_articles:
            print(f"     Estimated time remaining: {estimated_remaining/60:.1f} minutes")
        
        # Sleep between batches
        if total_processed < max_articles and news_batch:
            time.sleep(2)
    
    # Final summary
    elapsed = time.time() - start_time
    print("\n" + "="*70)
    print("EMBEDDING COMPLETE!")
    print("="*70)
    print(f"  Total Articles Processed: {total_processed}")
    print(f"  Successfully Embedded: {total_successful}")
    print(f"  Failed: {total_failed}")
    print(f"  Success Rate: {total_successful/total_processed*100:.1f}%")
    print(f"  Total Time: {elapsed/60:.1f} minutes")
    print("="*70 + "\n")
    
    logging.info(f"Embedding complete: {total_successful}/{total_processed} successful")

if __name__ == "__main__":
    # Default: embed up to 500 recent articles in batches of 50
    embed_recent_news(batch_size=50, max_articles=500)

















