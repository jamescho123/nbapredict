import json
import psycopg2
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

class NBAEntityExtractorOffline:
    """Offline version that uses rule-based extraction as fallback"""
    
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'dbname': 'James',
            'user': 'postgres',
            'password': 'jcjc1749'
        }
        
        # Common NBA team names
        self.team_names = [
            'Lakers', 'Warriors', 'Celtics', 'Heat', 'Bulls', 'Spurs', 'Knicks',
            'Nets', '76ers', 'Raptors', 'Bucks', 'Pacers', 'Hawks', 'Hornets',
            'Magic', 'Wizards', 'Cavaliers', 'Pistons', 'Bucks', 'Timberwolves',
            'Thunder', 'Trail Blazers', 'Jazz', 'Nuggets', 'Suns', 'Kings',
            'Clippers', 'Mavericks', 'Rockets', 'Grizzlies', 'Pelicans'
        ]
        
        # Common NBA player names (partial list)
        self.player_names = [
            'LeBron James', 'Stephen Curry', 'Kevin Durant', 'Giannis Antetokounmpo',
            'Luka Doncic', 'Jayson Tatum', 'Joel Embiid', 'Nikola Jokic',
            'Anthony Davis', 'Draymond Green', 'Klay Thompson', 'Russell Westbrook',
            'James Harden', 'Kawhi Leonard', 'Paul George', 'Damian Lillard'
        ]
    
    def extract_entities_offline(self, article_text: str, title: str = "") -> Optional[Dict]:
        """Extract entities using rule-based approach"""
        entities = []
        
        # Extract teams
        for team in self.team_names:
            if team.lower() in article_text.lower():
                entities.append({
                    "type": "team",
                    "name": team,
                    "details": {}
                })
        
        # Extract players
        for player in self.player_names:
            if player.lower() in article_text.lower():
                entities.append({
                    "type": "player", 
                    "name": player,
                    "details": {}
                })
        
        # Extract points (simple regex)
        points_pattern = r'(\d+)\s+points?'
        points_matches = re.findall(points_pattern, article_text, re.IGNORECASE)
        for points in points_matches:
            entities.append({
                "type": "stat",
                "name": f"{points} points",
                "details": {"category": "points", "value": int(points)}
            })
        
        # Extract injuries
        injury_keywords = ['injury', 'injured', 'hurt', 'day-to-day', 'out', 'surgery']
        for keyword in injury_keywords:
            if keyword.lower() in article_text.lower():
                entities.append({
                    "type": "injury",
                    "name": keyword,
                    "details": {"status": "unknown"}
                })
        
        # Extract technical fouls
        if 'technical foul' in article_text.lower():
            entities.append({
                "type": "penalty",
                "name": "technical foul",
                "details": {"type": "technical foul"}
            })
        
        # Extract conflicts
        conflict_keywords = ['altercation', 'fight', 'confrontation', 'dispute']
        for keyword in conflict_keywords:
            if keyword.lower() in article_text.lower():
                entities.append({
                    "type": "conflict",
                    "name": keyword,
                    "details": {"type": keyword}
                })
        
        return {
            "entities": entities,
            "game": {
                "date": "",
                "arena": "",
                "winner": "",
                "score": {"TEAM1": 0, "TEAM2": 0}
            }
        }
    
    def get_or_create_entity(self, entity_type: str, name: str, props: Dict = None) -> Optional[str]:
        """Get existing entity or create new one, return entity ID"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Try to find existing entity
            cur.execute("""
                SELECT id FROM "NBA"."entity" 
                WHERE etype = %s AND name = %s
            """, (entity_type, name))
            
            result = cur.fetchone()
            if result:
                return result[0]
            
            # Create new entity
            cur.execute("""
                INSERT INTO "NBA"."entity" (etype, name, props)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (entity_type, name, json.dumps(props or {})))
            
            entity_id = cur.fetchone()[0]
            conn.commit()
            return entity_id
            
        except Exception as e:
            logging.error(f"Error getting/creating entity: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    
    def store_news_article(self, title: str, body: str, url: str = None, 
                          published_at: datetime = None, source: str = "unknown") -> Optional[str]:
        """Store news article and return news ID"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO "NBA"."news" (title, body, url, published_at, source)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (title, body, url, published_at or datetime.now(), source))
            
            news_id = cur.fetchone()[0]
            conn.commit()
            return news_id
            
        except Exception as e:
            logging.error(f"Error storing news article: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    
    def store_entity_mention(self, news_id: str, entity_id: str, details: Dict = None) -> bool:
        """Store entity mention linking news to entity"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO "NBA"."entity_mention" (news_id, entity_id, details)
                VALUES (%s, %s, %s)
            """, (news_id, entity_id, json.dumps(details or {})))
            
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Error storing entity mention: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def process_news_article(self, title: str, body: str, url: str = None, 
                           published_at: datetime = None, source: str = "unknown") -> bool:
        """Process a complete news article: extract entities and store everything"""
        try:
            # Store the news article
            news_id = self.store_news_article(title, body, url, published_at, source)
            if not news_id:
                return False
            
            # Extract entities using offline method
            extracted_data = self.extract_entities_offline(body, title)
            if not extracted_data:
                logging.warning(f"Failed to extract entities from article: {title}")
                return False
            
            # Process entities
            entities = extracted_data.get("entities", [])
            for entity_data in entities:
                entity_type = entity_data.get("type")
                name = entity_data.get("name")
                details = entity_data.get("details", {})
                
                if not entity_type or not name:
                    continue
                
                # Get or create entity
                entity_id = self.get_or_create_entity(entity_type, name, details)
                if entity_id:
                    # Store mention
                    self.store_entity_mention(news_id, entity_id, details)
            
            return True
            
        except Exception as e:
            logging.error(f"Error processing news article: {e}")
            return False
    
    def get_latest_injuries(self, limit: int = 10) -> List[Dict]:
        """Get latest player injuries from the database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT e.name AS player,
                       em.details->>'injury' AS injury,
                       em.details->>'status' AS status,
                       n.title, n.published_at
                FROM "NBA"."entity" e
                JOIN "NBA"."entity_mention" em ON em.entity_id = e.id
                JOIN "NBA"."news" n ON n.id = em.news_id
                WHERE e.etype = 'player' AND em.details ? 'injury'
                ORDER BY n.published_at DESC
                LIMIT %s
            """, (limit,))
            
            results = cur.fetchall()
            return [
                {
                    "player": row[0],
                    "injury": row[1],
                    "status": row[2],
                    "title": row[3],
                    "published_at": row[4]
                }
                for row in results
            ]
            
        except Exception as e:
            logging.error(f"Error getting latest injuries: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_technical_fouls(self, limit: int = 10) -> List[Dict]:
        """Get recent technical fouls from the database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT e.name AS player, 
                       em.details->>'penalty' AS penalty, 
                       n.title, n.published_at
                FROM "NBA"."entity" e
                JOIN "NBA"."entity_mention" em ON em.entity_id = e.id
                JOIN "NBA"."news" n ON n.id = em.news_id
                WHERE em.details->>'penalty' = 'technical foul'
                ORDER BY n.published_at DESC
                LIMIT %s
            """, (limit,))
            
            results = cur.fetchall()
            return [
                {
                    "player": row[0],
                    "penalty": row[1],
                    "title": row[2],
                    "published_at": row[3]
                }
                for row in results
            ]
            
        except Exception as e:
            logging.error(f"Error getting technical fouls: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_team_game_summaries(self, team_name: str, limit: int = 10) -> List[Dict]:
        """Get game summaries for a specific team"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT em.details->>'score' AS score, 
                       n.title, n.published_at
                FROM "NBA"."entity" e
                JOIN "NBA"."entity_mention" em ON em.entity_id = e.id
                JOIN "NBA"."news" n ON n.id = em.news_id
                WHERE e.etype = 'team' AND e.name ILIKE %s
                ORDER BY n.published_at DESC
                LIMIT %s
            """, (f"%{team_name}%", limit))
            
            results = cur.fetchall()
            return [
                {
                    "score": row[0],
                    "title": row[1],
                    "published_at": row[2]
                }
                for row in results
            ]
            
        except Exception as e:
            logging.error(f"Error getting team game summaries: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

if __name__ == "__main__":
    # Test the offline extractor
    extractor = NBAEntityExtractorOffline()
    
    # Test article
    test_article = """
    LeBron James dropped 42 points as the Lakers edged the Warriors 112-108. 
    Draymond Green picked up a technical foul after an altercation with Anthony Davis. 
    Anthony Davis is listed as day-to-day with a hip injury. The game was played at 
    Crypto.com Arena in Los Angeles.
    """
    
    success = extractor.process_news_article(
        title="Lakers Edge Warriors in Thriller",
        body=test_article,
        source="test"
    )
    
    if success:
        print("Article processed successfully!")
        
        # Test queries
        print("\nLatest injuries:")
        injuries = extractor.get_latest_injuries(5)
        for injury in injuries:
            print(f"- {injury['player']}: {injury['injury']} ({injury['status']})")
        
        print("\nTechnical fouls:")
        fouls = extractor.get_technical_fouls(5)
        for foul in fouls:
            print(f"- {foul['player']}: {foul['penalty']}")
    else:
        print("Failed to process article")
