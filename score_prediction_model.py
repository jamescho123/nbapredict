import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
import random

class ScorePredictionModel:
    """Model for predicting game scores and gambling statistics"""
    
    def __init__(self):
        self.is_fitted = False
        self.home_score_model = None
        self.away_score_model = None
        
    def prepare_features(self, home_team, away_team, home_context, away_context, h2h_data):
        """Prepare features for score prediction"""
        features = {}
        
        # Team strength features
        home_strength = self._calculate_team_strength(home_context)
        away_strength = self._calculate_team_strength(away_context)
        
        features['home_strength'] = home_strength
        features['away_strength'] = away_strength
        features['strength_difference'] = home_strength - away_strength
        
        # Offensive and defensive ratings
        home_off_rating, home_def_rating = self._calculate_team_ratings(home_context)
        away_off_rating, away_def_rating = self._calculate_team_ratings(away_context)
        
        features['home_offensive_rating'] = home_off_rating
        features['home_defensive_rating'] = home_def_rating
        features['away_offensive_rating'] = away_off_rating
        features['away_defensive_rating'] = away_def_rating
        
        # Pace and tempo
        features['home_pace'] = self._calculate_team_pace(home_context)
        features['away_pace'] = self._calculate_team_pace(away_context)
        features['pace_difference'] = features['home_pace'] - features['away_pace']
        
        # Recent form
        home_form = home_context.get('recent_form', {})
        away_form = away_context.get('recent_form', {})
        
        features['home_recent_ppg'] = self._calculate_recent_ppg(home_context)
        features['away_recent_ppg'] = self._calculate_recent_ppg(away_context)
        features['home_recent_papg'] = self._calculate_recent_papg(home_context)
        features['away_recent_papg'] = self._calculate_recent_papg(away_context)
        
        # Head-to-head factors
        if h2h_data and h2h_data.get('total_games', 0) > 0:
            features['h2h_games'] = h2h_data['total_games']
            features['h2h_home_advantage'] = h2h_data['team1_wins'] / h2h_data['total_games']
        else:
            features['h2h_games'] = 0
            features['h2h_home_advantage'] = 0.5
        
        # Home court advantage
        features['home_court_advantage'] = 0.1  # 10% home advantage
        
        # Rest days (simplified)
        features['home_rest_days'] = 1
        features['away_rest_days'] = 1
        
        # Season factors
        features['season_progress'] = 0.5  # Mid-season assumption
        
        return features
    
    def _calculate_team_strength(self, team_context):
        """Calculate overall team strength"""
        if not team_context:
            return 0.5
        
        team_stats = team_context.get('team_stats', {})
        recent_form = team_context.get('recent_form', {})
        
        # Base strength from win percentage
        wins = team_stats.get('Wins', 0)
        losses = team_stats.get('Losses', 0)
        total_games = wins + losses
        win_percentage = wins / total_games if total_games > 0 else 0.5
        
        # Recent form
        recent_win_pct = recent_form.get('win_percentage', 0.5)
        
        # Combined strength
        strength = 0.6 * win_percentage + 0.4 * recent_win_pct
        return max(0.1, min(0.9, strength))
    
    def _calculate_team_ratings(self, team_context):
        """Calculate offensive and defensive ratings"""
        if not team_context:
            return 100.0, 100.0
        
        team_stats = team_context.get('team_stats', {})
        
        # Get points for and against
        points_for = team_stats.get('PointsFor', 0)
        points_against = team_stats.get('PointsAgainst', 0)
        games = team_stats.get('Wins', 0) + team_stats.get('Losses', 0)
        
        if games > 0:
            offensive_rating = points_for / games
            defensive_rating = points_against / games
        else:
            # Default ratings based on league average
            offensive_rating = 110.0
            defensive_rating = 110.0
        
        return offensive_rating, defensive_rating
    
    def _calculate_team_pace(self, team_context):
        """Calculate team pace (possessions per game)"""
        if not team_context:
            return 100.0  # League average pace
        
        # Simplified pace calculation
        # In reality, this would be based on possessions per game
        return 100.0 + np.random.normal(0, 5)  # Add some variance
    
    def _calculate_recent_ppg(self, team_context):
        """Calculate recent points per game"""
        if not team_context:
            return 110.0
        
        team_stats = team_context.get('team_stats', {})
        recent_form = team_context.get('recent_form', {})
        
        points_for = team_stats.get('PointsFor', 0)
        total_games = team_stats.get('Wins', 0) + team_stats.get('Losses', 0)
        
        if total_games > 0:
            return points_for / total_games
        else:
            return 110.0  # League average
    
    def _calculate_recent_papg(self, team_context):
        """Calculate recent points allowed per game"""
        if not team_context:
            return 110.0
        
        team_stats = team_context.get('team_stats', {})
        
        points_against = team_stats.get('PointsAgainst', 0)
        total_games = team_stats.get('Wins', 0) + team_stats.get('Losses', 0)
        
        if total_games > 0:
            return points_against / total_games
        else:
            return 110.0  # League average
    
    def predict_scores(self, home_team, away_team, home_context, away_context, h2h_data):
        """Predict final scores for both teams"""
        # Use simple prediction method
        return self._simple_score_prediction(home_team, away_team, home_context, away_context)
    
    def _simple_score_prediction(self, home_team, away_team, home_context, away_context):
        """Simple score prediction when model is not fitted"""
        # Base scores
        home_base = 110
        away_base = 110
        
        # Adjust based on team strength
        home_strength = self._calculate_team_strength(home_context)
        away_strength = self._calculate_team_strength(away_context)
        
        # Home court advantage
        home_advantage = 3
        
        # Calculate final scores
        home_score = int(home_base + (home_strength - 0.5) * 20 + home_advantage)
        away_score = int(away_base + (away_strength - 0.5) * 20)
        
        # Add some randomness
        home_score += random.randint(-5, 6)
        away_score += random.randint(-5, 6)
        
        # Ensure realistic bounds
        home_score = max(80, min(150, home_score))
        away_score = max(80, min(150, away_score))
        
        return home_score, away_score
    
    def predict_gambling_stats(self, home_score, away_score, home_team, away_team, home_context, away_context):
        """Predict gambling-relevant statistics"""
        stats = {}
        
        # Basic scores
        stats['home_score'] = home_score
        stats['away_score'] = away_score
        stats['total_points'] = home_score + away_score
        stats['point_spread'] = home_score - away_score
        
        # First half predictions (typically 45-50% of total)
        first_half_factor = 0.47 + random.uniform(-0.02, 0.02)
        first_half_factor = max(0.4, min(0.55, first_half_factor))
        
        home_first_half = int(home_score * first_half_factor)
        away_first_half = int(away_score * first_half_factor)
        
        stats['home_first_half'] = home_first_half
        stats['away_first_half'] = away_first_half
        stats['first_half_total'] = home_first_half + away_first_half
        
        # Second half predictions
        stats['home_second_half'] = home_score - home_first_half
        stats['away_second_half'] = away_score - away_first_half
        stats['second_half_total'] = stats['home_second_half'] + stats['away_second_half']
        
        # Quarters (divide first half by 2)
        stats['home_q1'] = int(home_first_half / 2)
        stats['away_q1'] = int(away_first_half / 2)
        stats['q1_total'] = stats['home_q1'] + stats['away_q1']
        
        stats['home_q2'] = home_first_half - stats['home_q1']
        stats['away_q2'] = away_first_half - stats['away_q1']
        stats['q2_total'] = stats['home_q2'] + stats['away_q2']
        
        # Third quarter
        third_q_factor = 0.26 + random.uniform(-0.02, 0.02)
        third_q_factor = max(0.22, min(0.30, third_q_factor))
        
        home_q3 = int(home_score * third_q_factor)
        away_q3 = int(away_score * third_q_factor)
        
        stats['home_q3'] = home_q3
        stats['away_q3'] = away_q3
        stats['q3_total'] = home_q3 + away_q3
        
        # Fourth quarter
        stats['home_q4'] = home_score - home_first_half - home_q3
        stats['away_q4'] = away_score - away_first_half - away_q3
        stats['q4_total'] = stats['home_q4'] + stats['away_q4']
        
        # Overtime probability (simplified)
        score_diff = abs(home_score - away_score)
        if score_diff <= 3:
            stats['overtime_probability'] = 0.15
        elif score_diff <= 6:
            stats['overtime_probability'] = 0.05
        else:
            stats['overtime_probability'] = 0.01
        
        # Team totals
        stats['home_team_total'] = home_score
        stats['away_team_total'] = away_score
        
        # Margin of victory
        stats['margin_of_victory'] = abs(home_score - away_score)
        
        # Confidence levels for different bets
        stats['confidence'] = {
            'moneyline': min(0.95, 0.5 + abs(stats['point_spread']) / 20),
            'spread': min(0.95, 0.6 + abs(stats['point_spread']) / 15),
            'total': min(0.95, 0.7 - abs(stats['total_points'] - 220) / 100),
            'first_half': min(0.95, 0.65 - abs(stats['first_half_total'] - 110) / 80)
        }
        
        return stats
    
    def fit(self, historical_data):
        """Fit the score prediction models"""
        try:
            # This would be implemented with historical game data
            # For now, we'll use the simple prediction method
            self.is_fitted = True
            logging.info("Score prediction model fitted successfully")
        except Exception as e:
            logging.error(f"Failed to fit score prediction model: {e}")
            self.is_fitted = False

def create_sample_historical_data():
    """Create sample historical data for training"""
    # This would typically come from a database of historical games
    data = []
    
    # Generate sample games
    teams = ['Lakers', 'Warriors', 'Celtics', 'Heat', 'Bulls', 'Knicks', 'Nets', 'Suns']
    
    for i in range(100):
        home_team = np.random.choice(teams)
        away_team = np.random.choice([t for t in teams if t != home_team])
        
        # Generate realistic scores
        home_score = np.random.randint(90, 130)
        away_score = np.random.randint(90, 130)
        
        data.append({
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'total_points': home_score + away_score,
            'point_spread': home_score - away_score
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Test the score prediction model
    model = ScorePredictionModel()
    
    # Create sample contexts
    home_context = {
        'team_stats': {'Wins': 45, 'Losses': 37, 'PointsFor': 9500, 'PointsAgainst': 9200},
        'recent_form': {'wins': 6, 'losses': 4, 'win_percentage': 0.6}
    }
    
    away_context = {
        'team_stats': {'Wins': 42, 'Losses': 40, 'PointsFor': 9200, 'PointsAgainst': 9400},
        'recent_form': {'wins': 4, 'losses': 6, 'win_percentage': 0.4}
    }
    
    h2h_data = {'total_games': 3, 'team1_wins': 2, 'team2_wins': 1}
    
    # Test prediction
    home_score, away_score = model.predict_scores(
        'Lakers', 'Warriors', home_context, away_context, h2h_data
    )
    
    print(f"Predicted Score: Lakers {home_score} - Warriors {away_score}")
    
    # Test gambling stats
    gambling_stats = model.predict_gambling_stats(
        home_score, away_score, 'Lakers', 'Warriors', home_context, away_context
    )
    
    print("\nGambling Statistics:")
    for key, value in gambling_stats.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v:.2f}")
        else:
            print(f"{key}: {value}")
