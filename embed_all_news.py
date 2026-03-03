import logging
import time
from news_embedding import setup_database, fetch_news_without_embeddings, get_embedding, update_news_with_embedding

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("full_embedding_process.log"),
        logging.StreamHandler()
    ]
)

def embed_all_news(batch_size=20, sleep_between_batches=5):
    """Process all news articles without embeddings in batches"""
    logging.info("Starting full embedding process")
    
    # Setup database first
    if not setup_database():
        logging.error("Database setup failed. Aborting.")
        return
    
    total_processed = 0
    total_successful = 0
    total_failed = 0
    
    while True:
        # Fetch a batch of news without embeddings
        news_batch = fetch_news_without_embeddings(batch_size)
        
        if not news_batch:
            logging.info("No more news articles to process. Done!")
            break
        
        batch_count = len(news_batch)
        logging.info(f"Processing batch of {batch_count} news articles")
        
        successful = 0
        failed = 0
        
        # Process each article in the batch
        for news_id, title, content in news_batch:
            try:
                # Combine title and content
                full_text = f"{title}\n\n{content}"
                
                # Get embedding
                logging.info(f"Getting embedding for news ID {news_id}: {title}")
                embedding = get_embedding(full_text)
                
                if embedding:
                    # Update news with embedding
                    if update_news_with_embedding(news_id, embedding):
                        logging.info(f"Successfully embedded news ID {news_id}")
                        successful += 1
                    else:
                        logging.error(f"Failed to update news ID {news_id} with embedding")
                        failed += 1
                else:
                    logging.error(f"Failed to get embedding for news ID {news_id}")
                    failed += 1
                
                # Brief pause to avoid overwhelming the API
                time.sleep(0.5)
                
            except Exception as e:
                logging.error(f"Error processing news ID {news_id}: {e}")
                failed += 1
        
        # Update totals
        total_processed += batch_count
        total_successful += successful
        total_failed += failed
        
        logging.info(f"Batch complete. Successful: {successful}, Failed: {failed}")
        logging.info(f"Total progress: Processed {total_processed}, Successful: {total_successful}, Failed: {total_failed}")
        
        # Sleep between batches to give the system a break
        if sleep_between_batches > 0:
            logging.info(f"Sleeping for {sleep_between_batches} seconds before next batch...")
            time.sleep(sleep_between_batches)
    
    logging.info(f"Embedding process complete!")
    logging.info(f"Total articles processed: {total_processed}")
    logging.info(f"Total successful: {total_successful}")
    logging.info(f"Total failed: {total_failed}")

if __name__ == "__main__":
    embed_all_news() 