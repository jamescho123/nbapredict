#!/usr/bin/env python3
"""
Vector Embedding System for NBA Teams, Players, and Matches
Creates and manages vector embeddings for enhanced predictions
"""

import psycopg2
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime, timedelta
import requests
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: Ollama not available. Using fallback embedding method.")

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NBAVectorEmbeddingSystem:
    """System for creating and managing vector embeddings for NBA data"""
    
    def __init__(self):
        self.conn = None
        self.team_embeddings = {}
        self.player_embeddings = {}
        self.match_embeddings = {}
        self.embedding_model = "bge-m3:latest"
        
    def connect_to_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            logging.info("Database connection successful")
            return True
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return False
    
    def get_embedding(self, text: str, model: str = None) -> Optional[np.ndarray]:
        """Get embedding for text using Ollama or fallback method"""
        if not OLLAMA_AVAILABLE:
            return self._get_fallback_embedding(text)
            
        if model is None:
            model = self.embedding_model
            
        try:
            response = ollama.embeddings(model=model, prompt=text)
            return np.array(response['embedding'])
        except Exception as e:
            logging.error(f"Failed to get embedding: {e}")
            return self._get_fallback_embedding(text)
    
    def _get_fallback_embedding(self, text: str) -> np.ndarray:
        """Fallback embedding method using simple text features"""
        # Create a simple embedding based on text features
        # This is a basic fallback - not as good as real embeddings but functional
        
        # Convert text to lowercase and split into words
        words = text.lower().split()
        
        # Create a simple feature vector (1024 dimensions to match typical embeddings)
        embedding = np.zeros(1024)
        
        # Hash-based features
        for i, word in enumerate(words):
            # Use word hash to determine position in embedding
            word_hash = hash(word) % 1024
            embedding[word_hash] += 1.0 / (i + 1)  # Weight by position
        
        # Add text length feature
        embedding[0] = len(text) / 1000.0  # Normalize text length
        
        # Add word count feature
        embedding[1] = len(words) / 100.0  # Normalize word count
        
        # Add character diversity feature
        unique_chars = len(set(text.lower()))
        embedding[2] = unique_chars / 100.0
        
        # Normalize the embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def create_team_embeddings(self):
        """Create vector embeddings for all teams"""
        if not self.conn:
            if not self.connect_to_database():
                return False
        
        try:
            cursor = self.conn.cursor()
            
            # Get team data
            cursor.execute(f'''
                SELECT "TeamID", "TeamName", "Conference", "Division", "State"
                FROM "{DB_SCHEMA}"."Teams"
            ''')
            teams = cursor.fetchall()
            
            logging.info(f"Creating embeddings for {len(teams)} teams")
            
            for team_id, team_name, conference, division, state in teams:
                # Create comprehensive team description
                team_description = f"""
                Team: {team_name}
                Conference: {conference or 'Unknown'}
                Division: {division or 'Unknown'}
                State: {state or 'Unknown'}
                """
                
                # Get team statistics if available
                try:
                    cursor.execute(f'''
                        SELECT "Wins", "Losses", "PointsFor", "PointsAgainst"
                        FROM "{DB_SCHEMA}"."Teams"
                        WHERE "TeamID" = %s
                    ''', (team_id,))
                    stats = cursor.fetchone()
                    
                    if stats and stats[0] is not None:
                        wins, losses, points_for, points_against = stats
                        win_pct = wins / (wins + losses) if (wins + losses) > 0 else 0.5
                        team_description += f"""
                        Record: {wins}-{losses} (Win%: {win_pct:.3f})
                        Points For: {points_for or 0}
                        Points Against: {points_against or 0}
                        """
                except:
                    pass
                
                # Get embedding
                embedding = self.get_embedding(team_description)
                if embedding is not None:
                    self.team_embeddings[team_id] = {
                        'name': team_name,
                        'embedding': embedding,
                        'description': team_description.strip()
                    }
                    logging.info(f"Created embedding for {team_name}")
            
            # Store in database
            self._store_team_embeddings()
            return True
            
        except Exception as e:
            logging.error(f"Error creating team embeddings: {e}")
            return False
    
    def create_player_embeddings(self):
        """Create vector embeddings for all players"""
        if not self.conn:
            if not self.connect_to_database():
                return False
        
        try:
            cursor = self.conn.cursor()
            
            # Get player data
            cursor.execute(f'''
                SELECT "PlayerID", "PlayerName", "Position", "Height", "Weight", "TeamID"
                FROM "{DB_SCHEMA}"."Players"
            ''')
            players = cursor.fetchall()
            
            logging.info(f"Creating embeddings for {len(players)} players")
            
            for player_id, player_name, position, height, weight, team_id in players:
                # Create comprehensive player description
                player_description = f"""
                Player: {player_name}
                Position: {position or 'Unknown'}
                Height: {height or 'Unknown'}
                Weight: {weight or 'Unknown'}
                """
                
                # Get team name
                if team_id:
                    try:
                        cursor.execute(f'''
                            SELECT "TeamName" FROM "{DB_SCHEMA}"."Teams"
                            WHERE "TeamID" = %s
                        ''', (team_id,))
                        team_result = cursor.fetchone()
                        if team_result:
                            player_description += f"Team: {team_result[0]}\n"
                    except:
                        pass
                
                # Get player statistics if available
                try:
                    cursor.execute(f'''
                        SELECT "Points", "Rebounds", "Assists", "Steals", "Blocks"
                        FROM "{DB_SCHEMA}"."Players"
                        WHERE "PlayerID" = %s
                    ''', (player_id,))
                    stats = cursor.fetchone()
                    
                    if stats and any(s is not None for s in stats):
                        points, rebounds, assists, steals, blocks = stats
                        player_description += f"""
                        Stats: {points or 0} PPG, {rebounds or 0} RPG, {assists or 0} APG
                        Steals: {steals or 0}, Blocks: {blocks or 0}
                        """
                except:
                    pass
                
                # Get embedding
                embedding = self.get_embedding(player_description)
                if embedding is not None:
                    self.player_embeddings[player_id] = {
                        'name': player_name,
                        'embedding': embedding,
                        'description': player_description.strip(),
                        'team_id': team_id
                    }
                    logging.info(f"Created embedding for {player_name}")
            
            # Store in database
            self._store_player_embeddings()
            return True
            
        except Exception as e:
            logging.error(f"Error creating player embeddings: {e}")
            return False
    
    def create_match_embeddings(self):
        """Create vector embeddings for matches/games"""
        if not self.conn:
            if not self.connect_to_database():
                return False
        
        try:
            cursor = self.conn.cursor()
            
            # Get match data from Schedule table
            cursor.execute(f'''
                SELECT "GameID", "Date", "Time", "HomeTeam", "AwayTeam", "Venue", "City", "State"
                FROM "{DB_SCHEMA}"."Schedule"
                ORDER BY "Date"
            ''')
            matches = cursor.fetchall()
            
            logging.info(f"Creating embeddings for {len(matches)} matches")
            
            for game_id, date, time, home_team, away_team, venue, city, state in matches:
                # Create comprehensive match description
                match_description = f"""
                Game: {away_team} @ {home_team}
                Date: {date}
                Time: {time}
                Venue: {venue or 'Unknown'}
                Location: {city or 'Unknown'}, {state or 'Unknown'}
                """
                
                # Add team context
                try:
                    # Get home team info
                    cursor.execute(f'''
                        SELECT "Conference", "Division" FROM "{DB_SCHEMA}"."Teams"
                        WHERE "TeamName" = %s
                    ''', (home_team,))
                    home_info = cursor.fetchone()
                    if home_info:
                        match_description += f"Home Team: {home_team} ({home_info[0] or 'Unknown'} Conference, {home_info[1] or 'Unknown'} Division)\n"
                    
                    # Get away team info
                    cursor.execute(f'''
                        SELECT "Conference", "Division" FROM "{DB_SCHEMA}"."Teams"
                        WHERE "TeamName" = %s
                    ''', (away_team,))
                    away_info = cursor.fetchone()
                    if away_info:
                        match_description += f"Away Team: {away_team} ({away_info[0] or 'Unknown'} Conference, {away_info[1] or 'Unknown'} Division)\n"
                except:
                    pass
                
                # Get embedding
                embedding = self.get_embedding(match_description)
                if embedding is not None:
                    self.match_embeddings[game_id] = {
                        'home_team': home_team,
                        'away_team': away_team,
                        'date': date,
                        'embedding': embedding,
                        'description': match_description.strip()
                    }
                    logging.info(f"Created embedding for {away_team} @ {home_team}")
            
            # Store in database
            self._store_match_embeddings()
            return True
            
        except Exception as e:
            logging.error(f"Error creating match embeddings: {e}")
            return False
    
    def _store_team_embeddings(self):
        """Store team embeddings in database"""
        try:
            cursor = self.conn.cursor()
            
            # Create table if not exists
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS "{DB_SCHEMA}"."TeamEmbeddings" (
                    "TeamID" INTEGER PRIMARY KEY,
                    "Embedding" vector(1024),
                    "Description" TEXT,
                    "CreatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert embeddings
            for team_id, data in self.team_embeddings.items():
                cursor.execute(f'''
                    INSERT INTO "{DB_SCHEMA}"."TeamEmbeddings" 
                    ("TeamID", "Embedding", "Description")
                    VALUES (%s, %s, %s)
                    ON CONFLICT ("TeamID") DO UPDATE SET
                    "Embedding" = EXCLUDED."Embedding",
                    "Description" = EXCLUDED."Description",
                    "CreatedAt" = CURRENT_TIMESTAMP
                ''', (team_id, data['embedding'].tolist(), data['description']))
            
            self.conn.commit()
            logging.info(f"Stored {len(self.team_embeddings)} team embeddings")
            
        except Exception as e:
            logging.error(f"Error storing team embeddings: {e}")
            self.conn.rollback()
    
    def _store_player_embeddings(self):
        """Store player embeddings in database"""
        try:
            cursor = self.conn.cursor()
            
            # Create table if not exists
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS "{DB_SCHEMA}"."PlayerEmbeddings" (
                    "PlayerID" INTEGER PRIMARY KEY,
                    "Embedding" vector(1024),
                    "Description" TEXT,
                    "TeamID" INTEGER,
                    "CreatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert embeddings
            for player_id, data in self.player_embeddings.items():
                cursor.execute(f'''
                    INSERT INTO "{DB_SCHEMA}"."PlayerEmbeddings" 
                    ("PlayerID", "Embedding", "Description", "TeamID")
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT ("PlayerID") DO UPDATE SET
                    "Embedding" = EXCLUDED."Embedding",
                    "Description" = EXCLUDED."Description",
                    "TeamID" = EXCLUDED."TeamID",
                    "CreatedAt" = CURRENT_TIMESTAMP
                ''', (player_id, data['embedding'].tolist(), data['description'], data['team_id']))
            
            self.conn.commit()
            logging.info(f"Stored {len(self.player_embeddings)} player embeddings")
            
        except Exception as e:
            logging.error(f"Error storing player embeddings: {e}")
            self.conn.rollback()
    
    def _store_match_embeddings(self):
        """Store match embeddings in database"""
        try:
            cursor = self.conn.cursor()
            
            # Create table if not exists
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS "{DB_SCHEMA}"."MatchEmbeddings" (
                    "GameID" INTEGER PRIMARY KEY,
                    "Embedding" vector(1024),
                    "Description" TEXT,
                    "HomeTeam" VARCHAR(50),
                    "AwayTeam" VARCHAR(50),
                    "GameDate" DATE,
                    "CreatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert embeddings
            for game_id, data in self.match_embeddings.items():
                cursor.execute(f'''
                    INSERT INTO "{DB_SCHEMA}"."MatchEmbeddings" 
                    ("GameID", "Embedding", "Description", "HomeTeam", "AwayTeam", "GameDate")
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT ("GameID") DO UPDATE SET
                    "Embedding" = EXCLUDED."Embedding",
                    "Description" = EXCLUDED."Description",
                    "HomeTeam" = EXCLUDED."HomeTeam",
                    "AwayTeam" = EXCLUDED."AwayTeam",
                    "GameDate" = EXCLUDED."GameDate",
                    "CreatedAt" = CURRENT_TIMESTAMP
                ''', (game_id, data['embedding'].tolist(), data['description'], 
                      data['home_team'], data['away_team'], data['date']))
            
            self.conn.commit()
            logging.info(f"Stored {len(self.match_embeddings)} match embeddings")
            
        except Exception as e:
            logging.error(f"Error storing match embeddings: {e}")
            self.conn.rollback()
    
    def load_embeddings_from_db(self):
        """Load embeddings from database"""
        if not self.conn:
            if not self.connect_to_database():
                return False
        
        try:
            cursor = self.conn.cursor()
            
            # Load team embeddings
            cursor.execute(f'''
                SELECT "TeamID", "Embedding", "Description"
                FROM "{DB_SCHEMA}"."TeamEmbeddings"
            ''')
            team_data = cursor.fetchall()
            
            for team_id, embedding, description in team_data:
                self.team_embeddings[team_id] = {
                    'name': description.split('\n')[0].replace('Team: ', ''),
                    'embedding': np.array(embedding),
                    'description': description
                }
            
            # Load player embeddings
            cursor.execute(f'''
                SELECT "PlayerID", "Embedding", "Description", "TeamID"
                FROM "{DB_SCHEMA}"."PlayerEmbeddings"
            ''')
            player_data = cursor.fetchall()
            
            for player_id, embedding, description, team_id in player_data:
                self.player_embeddings[player_id] = {
                    'name': description.split('\n')[0].replace('Player: ', ''),
                    'embedding': np.array(embedding),
                    'description': description,
                    'team_id': team_id
                }
            
            # Load match embeddings
            cursor.execute(f'''
                SELECT "GameID", "Embedding", "Description", "HomeTeam", "AwayTeam", "GameDate"
                FROM "{DB_SCHEMA}"."MatchEmbeddings"
            ''')
            match_data = cursor.fetchall()
            
            for game_id, embedding, description, home_team, away_team, game_date in match_data:
                self.match_embeddings[game_id] = {
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': game_date,
                    'embedding': np.array(embedding),
                    'description': description
                }
            
            logging.info(f"Loaded {len(self.team_embeddings)} team, {len(self.player_embeddings)} player, {len(self.match_embeddings)} match embeddings")
            return True
            
        except Exception as e:
            logging.error(f"Error loading embeddings: {e}")
            return False
    
    def find_similar_teams(self, team_name: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar teams based on vector similarity"""
        if not self.team_embeddings:
            self.load_embeddings_from_db()
        
        # Find team by name
        target_team_id = None
        for team_id, data in self.team_embeddings.items():
            if data['name'].lower() == team_name.lower():
                target_team_id = team_id
                break
        
        if target_team_id is None:
            return []
        
        target_embedding = self.team_embeddings[target_team_id]['embedding']
        similarities = []
        
        for team_id, data in self.team_embeddings.items():
            if team_id != target_team_id:
                similarity = np.dot(target_embedding, data['embedding']) / (
                    np.linalg.norm(target_embedding) * np.linalg.norm(data['embedding'])
                )
                similarities.append((data['name'], similarity))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
    
    def find_similar_players(self, player_name: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar players based on vector similarity"""
        if not self.player_embeddings:
            self.load_embeddings_from_db()
        
        # Find player by name
        target_player_id = None
        for player_id, data in self.player_embeddings.items():
            if data['name'].lower() == player_name.lower():
                target_player_id = player_id
                break
        
        if target_player_id is None:
            return []
        
        target_embedding = self.player_embeddings[target_player_id]['embedding']
        similarities = []
        
        for player_id, data in self.player_embeddings.items():
            if player_id != target_player_id:
                similarity = np.dot(target_embedding, data['embedding']) / (
                    np.linalg.norm(target_embedding) * np.linalg.norm(data['embedding'])
                )
                similarities.append((data['name'], similarity))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
    
    def find_similar_matches(self, home_team: str, away_team: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar matches based on vector similarity"""
        if not self.match_embeddings:
            self.load_embeddings_from_db()
        
        # Create query description
        query_description = f"Game: {away_team} @ {home_team}"
        query_embedding = self.get_embedding(query_description)
        
        if query_embedding is None:
            return []
        
        similarities = []
        
        for game_id, data in self.match_embeddings.items():
            similarity = np.dot(query_embedding, data['embedding']) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(data['embedding'])
            )
            match_desc = f"{data['away_team']} @ {data['home_team']} ({data['date']})"
            similarities.append((match_desc, similarity))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
    
    def create_all_embeddings(self):
        """Create all embeddings (teams, players, matches)"""
        logging.info("Starting comprehensive embedding creation...")
        
        success = True
        success &= self.create_team_embeddings()
        success &= self.create_player_embeddings()
        success &= self.create_match_embeddings()
        
        if success:
            logging.info("All embeddings created successfully!")
        else:
            logging.error("Some embeddings failed to create")
        
        return success
    
    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

def main():
    """Main function to create all embeddings"""
    embedding_system = NBAVectorEmbeddingSystem()
    
    try:
        if embedding_system.connect_to_database():
            success = embedding_system.create_all_embeddings()
            if success:
                print("✅ All embeddings created successfully!")
            else:
                print("❌ Some embeddings failed to create")
        else:
            print("❌ Failed to connect to database")
    finally:
        embedding_system.close_connection()

if __name__ == "__main__":
    main()
