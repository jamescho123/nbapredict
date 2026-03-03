"""
Weekly Data Update Orchestrator
Runs all necessary data extraction scripts to keep the NBA database fresh.
Suggested frequency: Daily or Weekly (Monday morning)
"""

import sys
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='daily_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Also log to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Import update functions
try:
    from update_stats import update_todays_stats
    from quick_news_update import crawl_recent_nba_news
    from news_embedding import setup_database, process_news_embeddings
    from generate_news_images import update_news_with_images
except ImportError as e:
    logging.error(f"Error importing modules: {e}")
    sys.exit(1)

def run_weekly_update():
    start_time = time.time()
    logging.info(f"{'='*60}")
    logging.info(f"STARTING AUTOMATED DATA UPDATE")
    logging.info(f"{'='*60}")
    
    # 1. Update Game Stats (Basketball Reference)
    logging.info("STEP 1: Updating Game Statistics...")
    try:
        stats_success = update_todays_stats()
        if stats_success:
            logging.info(">>> Stats update completed successfully.")
        else:
            logging.warning(">>> Stats update encountered warnings or errors.")
    except Exception as e:
        logging.error(f">>> CRITICAL ERROR updating stats: {e}")

    # 2. Update News (Basketball News)
    logging.info("STEP 2: Updating NBA News...")
    try:
        # Crawl 10 pages for weekly update (approx 200 articles)
        crawl_recent_nba_news(max_pages=10) 
        logging.info(">>> News update completed.")
    except Exception as e:
        logging.error(f">>> CRITICAL ERROR updating news: {e}")

    # 3. Embed News (Ollama / pgvector)
    logging.info("STEP 3: Embedding News Articles...")
    try:
        if setup_database():
            process_news_embeddings(batch_size=20)
            logging.info(">>> News embedding completed.")
        else:
            logging.error(">>> CRITICAL ERROR: Database setup failed for embedding.")
    except Exception as e:
        logging.error(f">>> CRITICAL ERROR embedding news: {e}")

    # 4. Generate News Images (Nano Banana Style)
    logging.info("STEP 4: Generating News Images...")
    try:
        update_news_with_images()
        logging.info(">>> News images generated successfully.")
    except Exception as e:
        logging.error(f">>> CRITICAL ERROR generating images: {e}")

    elapsed = time.time() - start_time
    logging.info(f"{'='*60}")
    logging.info(f"UPDATE COMPLETE | Duration: {elapsed:.2f} seconds")
    logging.info(f"{'='*60}\n")

if __name__ == "__main__":
    run_weekly_update()
