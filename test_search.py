#!/usr/bin/env python
import argparse
from news_embedding import search_similar_news
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def main():
    parser = argparse.ArgumentParser(description='Search for similar news articles using vector embeddings')
    parser.add_argument('query', type=str, help='The search query')
    parser.add_argument('--top', type=int, default=5, help='Number of results to return (default: 5)')
    parser.add_argument('--threshold', type=float, default=0.7, help='Similarity threshold (0-1, default: 0.7)')
    
    args = parser.parse_args()
    
    logging.info(f"Searching for: '{args.query}'")
    logging.info(f"Top results: {args.top}")
    logging.info(f"Similarity threshold: {args.threshold}")
    
    results = search_similar_news(args.query, top_k=args.top, similarity_threshold=args.threshold)
    
    if not results:
        logging.info("No results found.")
        return
    
    logging.info(f"Found {len(results)} results:")
    print("\n" + "="*80)
    for i, result in enumerate(results, 1):
        news_id, title, date, source, author, similarity = result
        print(f"{i}. {title}")
        print(f"   Date: {date} | Source: {source} | Author: {author}")
        print(f"   Similarity: {similarity:.4f} | ID: {news_id}")
        print("-"*80)
    
if __name__ == "__main__":
    main() 