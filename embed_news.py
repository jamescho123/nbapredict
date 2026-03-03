#!/usr/bin/env python
import sys
import os
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("embedding_updates.log"),
        logging.StreamHandler()
    ]
)

# Import the embedding functions
from news_embedding import setup_database, process_news_embeddings

def main():
    """Main function to update embeddings for news articles"""
    start_time = time.time()
    logging.info(f"Starting embedding update at {datetime.now()}")
    
    try:
        # Setup database with pgvector
        setup_database()
        
        # Process news embeddings with larger batch size for efficiency
        process_news_embeddings(batch_size=20)
        
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"Embedding update completed in {duration:.2f} seconds")
    except Exception as e:
        logging.error(f"Error during embedding update: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 