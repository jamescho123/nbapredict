#!/usr/bin/env python3
"""
Backtest NBA Prediction Model on 2024-25 Season Data
Tests model performance on realistic historical data
"""

import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sys
import os
import json
from typing import Dict, List, Tuple, Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_prediction import (
    predict_game_outcome, 
    get_team_context_data,
    calculate_team_strength,
    analyze_news_sentiment
)

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

class Season2024_25Backtester:
    """Backtesting system for 2024-25 NBA season"""
    
    def __init__(self):
        self.conn = None
        self.results = []
        self.performance_metrics = {}
        
    def connect_to_database(self):
        """Connect to the PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            logging.info("Database connection successful")
            return True
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return False
    
    def get_2024_25_games(self, limit: int = 100) -> List[Dict]:
        """Get 2024-25 season games for backtesting"""
        if not self.conn:
            return []
        
        try:
            # Only get games that have already occurred (before June 15, 2025 - after playoffs)
            cutoff_date = '2025-06-15'
            query = f'''
            SELECT r."GameID", r."Date", r."HomeTeam", r."AwayTeam", 
                   r."HomeScore", r."AwayScore", r."Winner", r."Margin", r."TotalPoints"
            FROM "{DB_SCHEMA}"."Season2024_25_Results" r
            WHERE r."Date" < %s
            ORDER BY r."Date" ASC
            LIMIT %s
            '''
            
            df = pd.read_sql_query(query, self.conn, params=[cutoff_date, limit])
            return df.to_dict('records')
        except Exception as e:
            logging.error(f"Error fetching 2024-25 games: {e}")
            return []
    
    def get_team_context_for_date(self, team_name: str, game_date: str) -> Dict:
        """Get team context data for a specific date in 2024-25 season"""
        try:
            # Get team stats from 2024-25 season
            cursor = self.conn.cursor()
            cursor.execute(f'''
                SELECT "Wins", "Losses", "WinPercentage", "PointsFor", "PointsAgainst", 
                       "PointDifferential", "HomeWins", "AwayWins"
                FROM "{DB_SCHEMA}"."Season2024_25_TeamStats"
                WHERE "TeamName" = %s
            ''', (team_name,))
            
            team_stats_row = cursor.fetchone()
            if not team_stats_row:
                return self.get_default_context()
            
            wins, losses, win_pct, points_for, points_against, point_diff, home_wins, away_wins = team_stats_row
            
            # Get recent news for the team
            cursor.execute(f'''
                SELECT "Title", "Content", "Date", "Sentiment"
                FROM "{DB_SCHEMA}"."Season2024_25_News"
                WHERE "Team" = %s AND "Date" <= %s
                ORDER BY "Date" DESC
                LIMIT 10
            ''', (team_name, game_date))
            
            news_data = cursor.fetchall()
            news_articles = []
            for title, content, date, sentiment in news_data:
                news_articles.append({
                    'Title': title,
                    'Content': content,
                    'Date': date,
                    'Sentiment': sentiment
                })
            
            # Calculate recent form (simulate based on overall record)
            recent_games = min(10, wins + losses)
            recent_wins = int(recent_games * win_pct * np.random.uniform(0.8, 1.2))
            recent_wins = max(0, min(recent_games, recent_wins))
            recent_losses = recent_games - recent_wins
            
            context = {
                'team_stats': {
                    'Wins': wins,
                    'Losses': losses,
                    'PointsFor': points_for,
                    'PointsAgainst': points_against
                },
                'recent_form': {
                    'wins': recent_wins,
                    'losses': recent_losses,
                    'win_percentage': recent_wins / recent_games if recent_games > 0 else 0.5,
                    'total_games': recent_games
                },
                'news': news_articles,
                'players': []  # Simplified for backtesting
            }
            
            return context
            
        except Exception as e:
            logging.error(f"Error getting team context for {team_name}: {e}")
            return self.get_default_context()
    
    def get_default_context(self) -> Dict:
        """Get default context when data is not available"""
        return {
            'team_stats': {'Wins': 41, 'Losses': 41, 'PointsFor': 9000, 'PointsAgainst': 9000},
            'recent_form': {'wins': 5, 'losses': 5, 'win_percentage': 0.5, 'total_games': 10},
            'news': [],
            'players': []
        }
    
    def make_historical_prediction(self, home_team: str, away_team: str, game_date: str) -> Dict:
        """Make a prediction for a historical 2024-25 game"""
        try:
            # Get team contexts for the specific date
            home_context = self.get_team_context_for_date(home_team, game_date)
            away_context = self.get_team_context_for_date(away_team, game_date)
            
            # Calculate team strengths
            home_strength, home_confidence = calculate_team_strength(home_context)
            away_strength, away_confidence = calculate_team_strength(away_context)
            
            # Apply home advantage
            home_advantage = 0.1
            home_strength += home_advantage
            
            # Calculate prediction
            prediction_score = home_strength - away_strength
            
            # Enhanced confidence calculation
            base_confidence = min(0.9, abs(prediction_score) * 2 + 0.3)
            data_quality = (home_confidence + away_confidence) / 2
            confidence = (base_confidence + data_quality) / 2
            
            # Determine predicted winner
            if prediction_score > 0:
                predicted_winner = home_team
            else:
                predicted_winner = away_team
            
            # Predict scores
            home_score = int(110 + (home_strength - 0.5) * 20 + home_advantage * 10)
            away_score = int(110 + (away_strength - 0.5) * 20)
            
            # Add some randomness
            home_score += np.random.randint(-8, 8)
            away_score += np.random.randint(-8, 8)
            
            # Ensure realistic bounds
            home_score = max(85, min(150, home_score))
            away_score = max(85, min(150, away_score))
            
            return {
                'predicted_winner': predicted_winner,
                'confidence': confidence,
                'prediction_score': prediction_score,
                'home_strength': home_strength,
                'away_strength': away_strength,
                'home_confidence': home_confidence,
                'away_confidence': away_confidence,
                'predicted_home_score': home_score,
                'predicted_away_score': away_score,
                'predicted_margin': abs(home_score - away_score)
            }
            
        except Exception as e:
            logging.error(f"Error making historical prediction: {e}")
            return {
                'predicted_winner': home_team,
                'confidence': 0.5,
                'prediction_score': 0.0,
                'home_strength': 0.5,
                'away_strength': 0.5,
                'home_confidence': 0.5,
                'away_confidence': 0.5,
                'predicted_home_score': 110,
                'predicted_away_score': 108,
                'predicted_margin': 2
            }
    
    def run_season_backtest(self, num_games: int = 200) -> Dict:
        """Run backtest on 2024-25 season data"""
        print(f"Starting 2024-25 Season Backtest")
        print(f"Testing on {num_games} games")
        print("=" * 60)
        
        # Get historical games
        historical_games = self.get_2024_25_games(num_games)
        
        if not historical_games:
            print("No 2024-25 season data found. Please run the import first.")
            return {}
        
        print(f"Found {len(historical_games)} games from 2024-25 season")
        
        # Run predictions
        correct_predictions = 0
        total_predictions = 0
        confidence_scores = []
        score_errors = []
        margin_errors = []
        
        results = []
        
        for i, game in enumerate(historical_games):
            home_team = game['HomeTeam']
            away_team = game['AwayTeam']
            game_date = str(game['Date'])
            home_score = game['HomeScore']
            away_score = game['AwayScore']
            actual_winner = game['Winner']
            actual_margin = game['Margin']
            
            # Make prediction
            prediction = self.make_historical_prediction(home_team, away_team, game_date)
            predicted_winner = prediction['predicted_winner']
            confidence = prediction['confidence']
            predicted_home_score = prediction['predicted_home_score']
            predicted_away_score = prediction['predicted_away_score']
            predicted_margin = prediction['predicted_margin']
            
            # Check if prediction is correct
            is_correct = (predicted_winner == actual_winner)
            if is_correct:
                correct_predictions += 1
            
            total_predictions += 1
            confidence_scores.append(confidence)
            
            # Calculate score prediction error
            home_score_error = abs(predicted_home_score - home_score)
            away_score_error = abs(predicted_away_score - away_score)
            score_error = (home_score_error + away_score_error) / 2
            score_errors.append(score_error)
            
            # Calculate margin error
            margin_error = abs(predicted_margin - actual_margin)
            margin_errors.append(margin_error)
            
            # Store result
            result = {
                'game_id': game['GameID'],
                'date': game_date,
                'home_team': home_team,
                'away_team': away_team,
                'actual_home_score': home_score,
                'actual_away_score': away_score,
                'actual_winner': actual_winner,
                'actual_margin': actual_margin,
                'predicted_winner': predicted_winner,
                'predicted_home_score': predicted_home_score,
                'predicted_away_score': predicted_away_score,
                'predicted_margin': predicted_margin,
                'confidence': confidence,
                'is_correct': is_correct,
                'score_error': score_error,
                'margin_error': margin_error
            }
            results.append(result)
            
            # Progress update
            if (i + 1) % 25 == 0:
                current_accuracy = correct_predictions / total_predictions
                print(f"Processed {i + 1}/{len(historical_games)} games... (Accuracy: {current_accuracy:.1%})")
        
        # Calculate comprehensive metrics
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
        avg_score_error = np.mean(score_errors) if score_errors else 0
        avg_margin_error = np.mean(margin_errors) if margin_errors else 0
        
        # Confidence-based analysis
        confidence_ranges = [
            (0.0, 0.5, "Low"),
            (0.5, 0.7, "Medium"),
            (0.7, 0.9, "High"),
            (0.9, 1.0, "Very High")
        ]
        
        confidence_analysis = {}
        for min_conf, max_conf, label in confidence_ranges:
            range_games = [r for r in results if min_conf <= r['confidence'] < max_conf]
            if range_games:
                correct = sum(1 for r in range_games if r['is_correct'])
                accuracy_range = correct / len(range_games)
                confidence_analysis[label] = {
                    'count': len(range_games),
                    'accuracy': accuracy_range,
                    'avg_confidence': np.mean([r['confidence'] for r in range_games])
                }
        
        # Store results
        self.results = results
        self.performance_metrics = {
            'total_games': total_predictions,
            'correct_predictions': correct_predictions,
            'accuracy': accuracy,
            'avg_confidence': avg_confidence,
            'avg_score_error': avg_score_error,
            'avg_margin_error': avg_margin_error,
            'confidence_analysis': confidence_analysis,
            'test_type': '2024_25_season_backtest'
        }
        
        return self.performance_metrics
    
    def print_detailed_results(self):
        """Print detailed backtest results"""
        if not self.performance_metrics:
            print("No backtest results available")
            return
        
        metrics = self.performance_metrics
        
        print("\n" + "=" * 80)
        print("2024-25 SEASON BACKTEST RESULTS")
        print("=" * 80)
        
        print(f"Total Games Tested: {metrics['total_games']}")
        print(f"Correct Predictions: {metrics['correct_predictions']}")
        print(f"Overall Accuracy: {metrics['accuracy']:.1%}")
        print(f"Average Confidence: {metrics['avg_confidence']:.1%}")
        print(f"Average Score Error: {metrics['avg_score_error']:.1f} points")
        print(f"Average Margin Error: {metrics['avg_margin_error']:.1f} points")
        
        # Confidence-based accuracy analysis
        if 'confidence_analysis' in metrics:
            print(f"\nConfidence-Based Performance:")
            for label, data in metrics['confidence_analysis'].items():
                print(f"   {label} Confidence: {data['count']} games, {data['accuracy']:.1%} accuracy (avg conf: {data['avg_confidence']:.1%})")
        
        # Model evaluation
        print(f"\nModel Evaluation:")
        if metrics['accuracy'] >= 0.6:
            print("   Model shows GOOD performance (>=60% accuracy)")
        elif metrics['accuracy'] >= 0.55:
            print("   Model shows MODERATE performance (55-60% accuracy)")
        else:
            print("   Model shows POOR performance (<55% accuracy)")
        
        if metrics['avg_confidence'] >= 0.7:
            print("   Model shows HIGH confidence")
        elif metrics['avg_confidence'] >= 0.5:
            print("   Model shows MODERATE confidence")
        else:
            print("   Model shows LOW confidence")
        
        # Score prediction evaluation
        if metrics['avg_score_error'] <= 10:
            print("   Score predictions are ACCURATE (<=10 point error)")
        elif metrics['avg_score_error'] <= 15:
            print("   Score predictions are MODERATE (10-15 point error)")
        else:
            print("   Score predictions are INACCURATE (>15 point error)")
    
    def save_results(self, filename: str = None):
        """Save backtest results to file"""
        if not self.results:
            print("No results to save")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"2024_25_season_backtest_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump({
                    'performance_metrics': self.performance_metrics,
                    'detailed_results': self.results
                }, f, indent=2, default=str)
            
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving results: {e}")

def main():
    """Main function to run 2024-25 season backtest"""
    backtester = Season2024_25Backtester()
    
    if not backtester.connect_to_database():
        print("Failed to connect to database")
        return
    
    try:
        print("Starting 2024-25 NBA Season Backtest")
        print("=" * 80)
        
        # Run backtest
        metrics = backtester.run_season_backtest(num_games=150)
        
        if metrics:
            backtester.print_detailed_results()
            backtester.save_results()
            
            print(f"\n2024-25 Season Backtest Complete!")
            print(f"Tested {metrics.get('total_games', 0)} games")
            print(f"Overall Accuracy: {metrics.get('accuracy', 0):.1%}")
            print(f"Average Confidence: {metrics.get('avg_confidence', 0):.1%}")
        else:
            print("Backtest failed - no 2024-25 season data found")
            print("Please run 'python import_manual_2024_25_games.py' first")
            
    except Exception as e:
        print(f"Error during backtest: {e}")
        logging.error(f"Backtest error: {e}")
    finally:
        if backtester.conn:
            backtester.conn.close()

if __name__ == "__main__":
    main()
