#!/usr/bin/env python3
"""
Vector-Enhanced NBA Prediction System
Integrates vector embeddings with traditional prediction methods
"""

import psycopg2
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json

# Import existing modules
from database_prediction import (
    connect_to_database, get_team_stats, get_player_stats, 
    get_head_to_head_record, calculate_team_strength, get_team_context_data
)
from vector_embedding_system import NBAVectorEmbeddingSystem

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

class VectorEnhancedPredictionSystem:
    """Enhanced prediction system using vector embeddings"""
    
    def __init__(self):
        self.conn = None
        self.embedding_system = NBAVectorEmbeddingSystem()
        self.team_embeddings = {}
        self.player_embeddings = {}
        self.match_embeddings = {}
        
    def connect_to_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            logging.info("Database connection successful")
            return True
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return False
    
    def load_embeddings(self):
        """Load all embeddings from database"""
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
    
    def get_team_vector_similarity(self, team1: str, team2: str) -> float:
        """Calculate vector similarity between two teams"""
        if not self.team_embeddings:
            self.load_embeddings()
        
        team1_id = None
        team2_id = None
        
        # Find team IDs
        for team_id, data in self.team_embeddings.items():
            if data['name'].lower() == team1.lower():
                team1_id = team_id
            if data['name'].lower() == team2.lower():
                team2_id = team_id
        
        if team1_id is None or team2_id is None:
            return 0.0
        
        # Calculate cosine similarity
        embedding1 = self.team_embeddings[team1_id]['embedding']
        embedding2 = self.team_embeddings[team2_id]['embedding']
        
        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        
        return float(similarity)
    
    def get_team_style_analysis(self, team_name: str) -> Dict:
        """Analyze team playing style using vector embeddings"""
        if not self.team_embeddings:
            self.load_embeddings()
        
        # Find team
        target_team_id = None
        for team_id, data in self.team_embeddings.items():
            if data['name'].lower() == team_name.lower():
                target_team_id = team_id
                break
        
        if target_team_id is None:
            return {}
        
        target_embedding = self.team_embeddings[target_team_id]['embedding']
        
        # Find similar teams
        similarities = []
        for team_id, data in self.team_embeddings.items():
            if team_id != target_team_id:
                similarity = np.dot(target_embedding, data['embedding']) / (
                    np.linalg.norm(target_embedding) * np.linalg.norm(data['embedding'])
                )
                similarities.append((data['name'], similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Analyze style patterns
        style_analysis = {
            'team_name': team_name,
            'similar_teams': similarities[:5],
            'style_confidence': similarities[0][1] if similarities else 0.0,
            'conference_affinity': self._analyze_conference_affinity(team_name, similarities),
            'division_affinity': self._analyze_division_affinity(team_name, similarities)
        }
        
        return style_analysis
    
    def _analyze_conference_affinity(self, team_name: str, similarities: List[Tuple[str, float]]) -> Dict:
        """Analyze conference affinity based on similar teams"""
        if not self.conn:
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            # Get team's conference
            cursor.execute(f'''
                SELECT "Conference" FROM "{DB_SCHEMA}"."Teams"
                WHERE "TeamName" = %s
            ''', (team_name,))
            team_conference = cursor.fetchone()
            if not team_conference:
                return {}
            
            team_conference = team_conference[0]
            
            # Analyze similar teams' conferences
            conference_scores = {}
            for similar_team, similarity in similarities[:10]:  # Top 10 similar teams
                cursor.execute(f'''
                    SELECT "Conference" FROM "{DB_SCHEMA}"."Teams"
                    WHERE "TeamName" = %s
                ''', (similar_team,))
                conf_result = cursor.fetchone()
                if conf_result:
                    conf = conf_result[0]
                    if conf not in conference_scores:
                        conference_scores[conf] = 0
                    conference_scores[conf] += similarity
            
            return {
                'own_conference': team_conference,
                'conference_scores': conference_scores,
                'cross_conference_similarity': conference_scores.get(team_conference, 0) / sum(conference_scores.values()) if conference_scores else 0
            }
            
        except Exception as e:
            logging.error(f"Error analyzing conference affinity: {e}")
            return {}
    
    def _analyze_division_affinity(self, team_name: str, similarities: List[Tuple[str, float]]) -> Dict:
        """Analyze division affinity based on similar teams"""
        if not self.conn:
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            # Get team's division
            cursor.execute(f'''
                SELECT "Division" FROM "{DB_SCHEMA}"."Teams"
                WHERE "TeamName" = %s
            ''', (team_name,))
            team_division = cursor.fetchone()
            if not team_division:
                return {}
            
            team_division = team_division[0]
            
            # Analyze similar teams' divisions
            division_scores = {}
            for similar_team, similarity in similarities[:10]:  # Top 10 similar teams
                cursor.execute(f'''
                    SELECT "Division" FROM "{DB_SCHEMA}"."Teams"
                    WHERE "TeamName" = %s
                ''', (similar_team,))
                div_result = cursor.fetchone()
                if div_result:
                    div = div_result[0]
                    if div not in division_scores:
                        division_scores[div] = 0
                    division_scores[div] += similarity
            
            return {
                'own_division': team_division,
                'division_scores': division_scores,
                'same_division_similarity': division_scores.get(team_division, 0) / sum(division_scores.values()) if division_scores else 0
            }
            
        except Exception as e:
            logging.error(f"Error analyzing division affinity: {e}")
            return {}
    
    def get_historical_match_similarity(self, home_team: str, away_team: str) -> Dict:
        """Find similar historical matches using vector embeddings"""
        if not self.match_embeddings:
            self.load_embeddings()
        
        # Create query for this matchup
        query_description = f"Game: {away_team} @ {home_team}"
        query_embedding = self.embedding_system.get_embedding(query_description)
        
        if query_embedding is None:
            return {}
        
        # Find similar matches
        similarities = []
        for game_id, data in self.match_embeddings.items():
            similarity = np.dot(query_embedding, data['embedding']) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(data['embedding'])
            )
            similarities.append({
                'game_id': game_id,
                'home_team': data['home_team'],
                'away_team': data['away_team'],
                'date': data['date'],
                'similarity': similarity
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return {
            'query_matchup': f"{away_team} @ {home_team}",
            'similar_matches': similarities[:10],
            'avg_similarity': np.mean([m['similarity'] for m in similarities[:5]]) if similarities else 0.0,
            'high_similarity_matches': [m for m in similarities if m['similarity'] > 0.8]
        }
    
    def predict_with_vector_enhancement(self, home_team: str, away_team: str) -> Dict:
        """Enhanced prediction using vector embeddings"""
        if not self.conn:
            if not self.connect_to_database():
                return {}
        
        # Load embeddings if not already loaded
        if not self.team_embeddings:
            self.load_embeddings()
        
        # Get traditional prediction data
        from database_prediction import predict_game_outcome
        traditional_prediction = predict_game_outcome(home_team, away_team)
        
        # Get vector-based insights
        vector_insights = {
            'team_similarity': self.get_team_vector_similarity(home_team, away_team),
            'home_team_style': self.get_team_style_analysis(home_team),
            'away_team_style': self.get_team_style_analysis(away_team),
            'historical_match_similarity': self.get_historical_match_similarity(home_team, away_team)
        }
        
        # Calculate vector-enhanced confidence
        vector_confidence_boost = self._calculate_vector_confidence_boost(vector_insights)
        
        # Enhance the traditional prediction
        enhanced_prediction = traditional_prediction.copy()
        enhanced_prediction['vector_insights'] = vector_insights
        enhanced_prediction['vector_confidence_boost'] = vector_confidence_boost
        enhanced_prediction['enhanced_confidence'] = min(0.95, 
            traditional_prediction.get('confidence', 0.5) + vector_confidence_boost
        )
        
        # Add vector-based predictions
        enhanced_prediction['vector_predictions'] = self._generate_vector_predictions(
            home_team, away_team, vector_insights
        )
        
        return enhanced_prediction
    
    def _calculate_vector_confidence_boost(self, vector_insights: Dict) -> float:
        """Calculate confidence boost from vector insights"""
        boost = 0.0
        
        # Team similarity boost
        team_similarity = vector_insights.get('team_similarity', 0.0)
        if team_similarity > 0.7:
            boost += 0.1  # High similarity teams
        elif team_similarity > 0.5:
            boost += 0.05  # Moderate similarity
        
        # Style analysis confidence
        home_style_conf = vector_insights.get('home_team_style', {}).get('style_confidence', 0.0)
        away_style_conf = vector_insights.get('away_team_style', {}).get('style_confidence', 0.0)
        avg_style_conf = (home_style_conf + away_style_conf) / 2
        boost += avg_style_conf * 0.1
        
        # Historical match similarity
        hist_similarity = vector_insights.get('historical_match_similarity', {}).get('avg_similarity', 0.0)
        if hist_similarity > 0.8:
            boost += 0.15  # Very similar historical matches
        elif hist_similarity > 0.6:
            boost += 0.1   # Moderately similar matches
        
        return min(0.3, boost)  # Cap at 30% boost
    
    def _generate_vector_predictions(self, home_team: str, away_team: str, vector_insights: Dict) -> Dict:
        """Generate additional predictions based on vector analysis"""
        predictions = {}
        
        # Style-based predictions
        home_style = vector_insights.get('home_team_style', {})
        away_style = vector_insights.get('away_team_style', {})
        
        # Conference/division advantage
        home_conf_affinity = home_style.get('conference_affinity', {}).get('cross_conference_similarity', 0.5)
        away_conf_affinity = away_style.get('conference_affinity', {}).get('cross_conference_similarity', 0.5)
        
        predictions['conference_advantage'] = {
            'home_team': home_conf_affinity,
            'away_team': away_conf_affinity,
            'advantage': 'home' if home_conf_affinity > away_conf_affinity else 'away'
        }
        
        # Team similarity impact
        team_similarity = vector_insights.get('team_similarity', 0.0)
        predictions['similarity_impact'] = {
            'similarity_score': team_similarity,
            'prediction': 'close_game' if team_similarity > 0.7 else 'mismatch' if team_similarity < 0.3 else 'moderate_difference'
        }
        
        # Historical match patterns
        hist_similarity = vector_insights.get('historical_match_similarity', {})
        similar_matches = hist_similarity.get('similar_matches', [])
        
        if similar_matches:
            predictions['historical_patterns'] = {
                'similar_matches_count': len(similar_matches),
                'avg_similarity': hist_similarity.get('avg_similarity', 0.0),
                'high_similarity_count': len(hist_similarity.get('high_similarity_matches', []))
            }
        else:
            predictions['historical_patterns'] = {
                'similar_matches_count': 0,
                'avg_similarity': 0.0,
                'high_similarity_count': 0
            }
        
        return predictions
    
    def get_vector_enhanced_team_comparison(self, home_team: str, away_team: str) -> Dict:
        """Get comprehensive team comparison using vector embeddings"""
        if not self.team_embeddings:
            self.load_embeddings()
        
        comparison = {
            'home_team': home_team,
            'away_team': away_team,
            'vector_similarity': self.get_team_vector_similarity(home_team, away_team),
            'home_team_analysis': self.get_team_style_analysis(home_team),
            'away_team_analysis': self.get_team_style_analysis(away_team),
            'historical_context': self.get_historical_match_similarity(home_team, away_team)
        }
        
        return comparison
    
    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

def main():
    """Test the vector-enhanced prediction system"""
    system = VectorEnhancedPredictionSystem()
    
    try:
        if system.connect_to_database():
            system.load_embeddings()
            
            # Test prediction
            home_team = "Los Angeles Lakers"
            away_team = "Golden State Warriors"
            
            print(f"🏀 Vector-Enhanced Prediction: {away_team} @ {home_team}")
            print("=" * 60)
            
            prediction = system.predict_with_vector_enhancement(home_team, away_team)
            
            if prediction:
                print(f"Predicted Winner: {prediction.get('predicted_winner', 'Unknown')}")
                print(f"Traditional Confidence: {prediction.get('confidence', 0):.2%}")
                print(f"Vector Confidence Boost: {prediction.get('vector_confidence_boost', 0):.2%}")
                print(f"Enhanced Confidence: {prediction.get('enhanced_confidence', 0):.2%}")
                
                print(f"\nVector Insights:")
                vector_insights = prediction.get('vector_insights', {})
                print(f"Team Similarity: {vector_insights.get('team_similarity', 0):.3f}")
                
                home_style = vector_insights.get('home_team_style', {})
                print(f"Home Team Style Confidence: {home_style.get('style_confidence', 0):.3f}")
                
                away_style = vector_insights.get('away_team_style', {})
                print(f"Away Team Style Confidence: {away_style.get('style_confidence', 0):.3f}")
                
                hist_similarity = vector_insights.get('historical_match_similarity', {})
                print(f"Historical Match Similarity: {hist_similarity.get('avg_similarity', 0):.3f}")
                
                print(f"\nSimilar Teams to {home_team}:")
                for team, sim in home_style.get('similar_teams', [])[:3]:
                    print(f"  - {team}: {sim:.3f}")
                
                print(f"\nSimilar Teams to {away_team}:")
                for team, sim in away_style.get('similar_teams', [])[:3]:
                    print(f"  - {team}: {sim:.3f}")
            else:
                print("❌ Prediction failed")
        else:
            print("❌ Failed to connect to database")
    finally:
        system.close_connection()

if __name__ == "__main__":
    main()
