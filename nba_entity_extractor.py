import json
import requests
import psycopg2
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

class NBAEntityExtractor:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.db_config = {
            'host': 'localhost',
            'dbname': 'James',
            'user': 'postgres',
            'password': 'jcjc1749'
        }
        
    def get_llm_response(self, prompt: str, model: str = "llama3.1:latest") -> Optional[str]:
        """Get response from Ollama LLM"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            logging.error(f"Error getting LLM response: {e}")
            return None
    
    def extract_entities(self, article_text: str, title: str = "") -> Optional[Dict]:
        """Extract entities from NBA news article using LLM"""
        prompt = f"""You are an information extraction system for NBA news.
Read the following NBA news article and extract structured entities.
Return ONLY valid JSON in this format:
{{
  "entities": [
    {{"type":"player","name":"", "details":{{}}}},
    {{"type":"team","name":"", "details":{{}}}},
    {{"type":"injury","name":"", "details":{{}}}},
    {{"type":"penalty","name":"", "details":{{}}}},
    {{"type":"stat","name":"", "details":{{}}}},
    {{"type":"conflict","name":"", "details":{{}}}},
    {{"type":"trade","name":"", "details":{{}}}},
    {{"type":"award","name":"", "details":{{}}}},
    {{"type":"location","name":"", "details":{{}}}},
    {{"type":"date","name":"", "details":{{}}}}
  ],
  "game": {{
    "date":"",
    "arena":"",
    "winner":"",
    "score":{{"TEAM1":0,"TEAM2":0}}
  }}
}}

Details can include things like:
- player: {{"points":42, "rebounds":12, "assists":8}}
- injury: {{"type":"ankle sprain", "status":"day-to-day", "player":"Player Name"}}
- penalty: {{"type":"technical foul", "player":"Player Name"}}
- stat: {{"category":"assists", "value":10, "player":"Player Name"}}
- conflict: {{"type":"altercation", "players":["Player1", "Player2"]}}
- trade: {{"from_team":"Team A", "to_team":"Team B", "player":"Player Name"}}
- award: {{"type":"MVP candidate", "player":"Player Name"}}
- location: {{"type":"arena", "name":"Crypto.com Arena"}}
- date: {{"type":"game_date", "value":"2025-01-20"}}

Article Title: {title}

Article: {article_text}"""

        response = self.get_llm_response(prompt)
        if not response:
            return None
            
        try:
            # Clean the response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing LLM response as JSON: {e}")
            logging.error(f"Response was: {response}")
            return None
    
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
            
            # Extract entities using LLM
            extracted_data = self.extract_entities(body, title)
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
            
            # Process game information if available
            game_data = extracted_data.get("game", {})
            if game_data:
                # Store game as an entity
                game_name = f"{game_data.get('winner', 'Unknown')} vs {game_data.get('arena', 'Unknown Arena')}"
                game_id = self.get_or_create_entity("game", game_name, game_data)
                if game_id:
                    self.store_entity_mention(news_id, game_id, game_data)
            
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
    # Test the extractor
    extractor = NBAEntityExtractor()
    
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
