import psycopg2
import logging
from datetime import datetime
from nba_entity_extractor import NBAEntityExtractor
from nba_entity_extractor_offline import NBAEntityExtractorOffline
from typing import List, Dict, Optional

class NewsEntityProcessor:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'dbname': 'James',
            'user': 'postgres',
            'password': 'jcjc1749'
        }
        self.extractor = NBAEntityExtractor()
        self.offline_extractor = NBAEntityExtractorOffline()
        
    def get_existing_news_articles(self, limit: int = None) -> List[Dict]:
        """Get news articles from the existing News table"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            query = """
                SELECT "NewsID", "Title", "Content", "URL", "Date", "Source"
                FROM "NBA"."News"
                ORDER BY "Date" DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cur.execute(query)
            results = cur.fetchall()
            
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "url": row[3],
                    "date": row[4],
                    "source": row[5]
                }
                for row in results
            ]
            
        except Exception as e:
            logging.error(f"Error getting existing news articles: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
    
    def check_article_processed(self, news_id: int) -> bool:
        """Check if an article has already been processed for entity extraction"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Check if there's a corresponding entry in the new news table
            cur.execute("""
                SELECT COUNT(*) FROM "NBA"."news" 
                WHERE title IN (
                    SELECT "Title" FROM "NBA"."News" WHERE "NewsID" = %s
                )
            """, (news_id,))
            
            count = cur.fetchone()[0]
            return count > 0
            
        except Exception as e:
            logging.error(f"Error checking if article processed: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def process_existing_news(self, limit: int = None, force_reprocess: bool = False) -> Dict:
        """Process existing news articles for entity extraction"""
        articles = self.get_existing_news_articles(limit)
        
        processed = 0
        skipped = 0
        failed = 0
        
        for article in articles:
            try:
                # Check if already processed
                if not force_reprocess and self.check_article_processed(article["id"]):
                    skipped += 1
                    continue
                
                # Convert date if needed
                published_at = article["date"]
                if isinstance(published_at, str):
                    try:
                        published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    except:
                        published_at = datetime.now()
                
                # Process the article
                success = self.extractor.process_news_article(
                    title=article["title"],
                    body=article["content"],
                    url=article["url"],
                    published_at=published_at,
                    source=article["source"] or "unknown"
                )
                
                if success:
                    processed += 1
                    logging.info(f"Processed article: {article['title']}")
                else:
                    failed += 1
                    logging.error(f"Failed to process article: {article['title']}")
                    
            except Exception as e:
                failed += 1
                logging.error(f"Error processing article {article['id']}: {e}")
        
        return {
            "total": len(articles),
            "processed": processed,
            "skipped": skipped,
            "failed": failed
        }
    
    def process_new_article(self, title: str, content: str, url: str = None, 
                          source: str = "unknown", published_at: datetime = None) -> bool:
        """Process a single new article"""
        # Try LLM-based extraction first
        try:
            success = self.extractor.process_news_article(
                title=title,
                body=content,
                url=url,
                published_at=published_at or datetime.now(),
                source=source
            )
            if success:
                return True
        except Exception as e:
            logging.warning(f"LLM extraction failed, falling back to offline: {e}")
        
        # Fallback to offline extraction
        return self.offline_extractor.process_news_article(
            title=title,
            body=content,
            url=url,
            published_at=published_at or datetime.now(),
            source=source
        )
    
    def get_entity_statistics(self) -> Dict:
        """Get statistics about extracted entities"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Count entities by type
            cur.execute("""
                SELECT etype, COUNT(*) as count
                FROM "NBA"."entity"
                GROUP BY etype
                ORDER BY count DESC
            """)
            
            entity_counts = {row[0]: row[1] for row in cur.fetchall()}
            
            # Count total news articles processed
            cur.execute('SELECT COUNT(*) FROM "NBA"."news"')
            total_news = cur.fetchone()[0]
            
            # Count total mentions
            cur.execute('SELECT COUNT(*) FROM "NBA"."entity_mention"')
            total_mentions = cur.fetchone()[0]
            
            return {
                "total_news_articles": total_news,
                "total_entities": sum(entity_counts.values()),
                "total_mentions": total_mentions,
                "entity_counts": entity_counts
            }
            
        except Exception as e:
            logging.error(f"Error getting entity statistics: {e}")
            return {}
        finally:
            if 'conn' in locals():
                conn.close()
    
    def search_entities(self, query: str, entity_type: str = None, limit: int = 10) -> List[Dict]:
        """Search for entities by name"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            sql = """
                SELECT e.name, e.etype, e.props, COUNT(em.id) as mention_count
                FROM "NBA"."entity" e
                LEFT JOIN "NBA"."entity_mention" em ON em.entity_id = e.id
                WHERE e.name ILIKE %s
            """
            params = [f"%{query}%"]
            
            if entity_type:
                sql += " AND e.etype = %s"
                params.append(entity_type)
            
            sql += """
                GROUP BY e.id, e.name, e.etype, e.props
                ORDER BY mention_count DESC, e.name
                LIMIT %s
            """
            params.append(limit)
            
            cur.execute(sql, params)
            results = cur.fetchall()
            
            return [
                {
                    "name": row[0],
                    "type": row[1],
                    "props": row[2],
                    "mention_count": row[3]
                }
                for row in results
            ]
            
        except Exception as e:
            logging.error(f"Error searching entities: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

if __name__ == "__main__":
    processor = NewsEntityProcessor()
    
    # Process existing news articles
    print("Processing existing news articles...")
    result = processor.process_existing_news(limit=5)
    print(f"Processing complete: {result}")
    
    # Show statistics
    print("\nEntity Statistics:")
    stats = processor.get_entity_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Test search
    print("\nSearching for 'LeBron':")
    results = processor.search_entities("LeBron", limit=5)
    for result in results:
        print(f"- {result['name']} ({result['type']}) - {result['mention_count']} mentions")
