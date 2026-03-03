"""
Enhanced NBA Prediction Engine with Advanced Configuration

This module extends database_prediction.py to use the advanced configuration
for more accurate predictions with extensive parameter tuning.
"""

import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from model_config_advanced import load_config, get_parameter
from database_prediction import (
    DB_CONFIG, DB_SCHEMA,
    get_team_stats, get_recent_matches, get_team_news,
    get_head_to_head_record, analyze_news_sentiment
)

# Load advanced configuration
ADVANCED_CONFIG = load_config()

def calculate_rest_days_impact(team_name, game_date, conn):
    """Calculate rest days impact on team performance"""
    raise NotImplementedError()

def calculate_travel_distance_impact(home_team, away_team):
    """Calculate travel distance and time zone impact"""
    raise NotImplementedError()

def calculate_schedule_difficulty(team_name, game_date, conn):
    """Calculate schedule difficulty (games in last 7 days, road trip length)"""
    raise NotImplementedError()

def get_injury_impact(team_name, game_date=None):
    """Get injury impact from news and player availability"""
    raise NotImplementedError()

def calculate_advanced_team_strength(team_context, opponent_context=None):
    """
    Calculate team strength using advanced configuration with extensive parameters
    
    Args:
        team_context: Dict containing team stats, recent form, news, etc.
        opponent_context: Optional opponent context for matchup-specific adjustments
        
    Returns:
        tuple: (strength_score, confidence_score)
    """
    if not team_context:
        return 0.5, 0.1
    
    team_stats = team_context.get('team_stats', {})
    recent_form = team_context.get('recent_form', {})
    news_data = team_context.get('news', [])
    
    # Basic stats
    wins = team_stats.get('Wins', 0)
    losses = team_stats.get('Losses', 0)
    total_games = wins + losses
    win_percentage = wins / total_games if total_games > 0 else 0.5
    
    points_for = team_stats.get('PointsFor', 0)
    points_against = team_stats.get('PointsAgainst', 0)
    
    # ============================================
    # CORE STRENGTH COMPONENTS
    # ============================================
    weights = get_parameter(ADVANCED_CONFIG, 'strength_weights', default={})
    
    # 1. Win Percentage (0.25 weight)
    win_pct_score = win_percentage
    
    # 2. Point Differential (0.20 weight)
    if total_games > 0:
        point_diff = (points_for - points_against) / total_games
        point_diff_normalized = max(0, min(1, (point_diff + 12) / 24))
    else:
        point_diff_normalized = 0.5
    
    # 3. Offensive Efficiency (0.15 weight)
    if total_games > 0:
        ppg = points_for / total_games
        off_efficiency = min(1.0, max(0.0, (ppg - 95) / 30))
    else:
        off_efficiency = 0.5
    
    # 4. Defensive Efficiency (0.15 weight)
    if total_games > 0:
        opp_ppg = points_against / total_games
        def_efficiency = min(1.0, max(0.0, 1 - (opp_ppg - 95) / 30))
    else:
        def_efficiency = 0.5
    
    # 5. Recent Form (0.15 weight) - with time decay
    recent_form_config = get_parameter(ADVANCED_CONFIG, 'recent_form', default={})
    windows = get_parameter(recent_form_config, 'windows', default={})
    
    recent_win_pct = recent_form.get('win_percentage', win_percentage)
    recent_games_count = recent_form.get('total_games', 0)
    
    if recent_games_count >= 10:
        form_score = recent_win_pct
    elif recent_games_count > 0:
        form_score = 0.7 * recent_win_pct + 0.3 * win_percentage
    else:
        form_score = win_percentage
    
    # 6. News Sentiment (0.10 weight)
    sentiment_score = analyze_news_sentiment_advanced(news_data)
    
    # ============================================
    # CALCULATE BASE STRENGTH
    # ============================================
    base_strength = (
        weights.get('win_percentage', 0.25) * win_pct_score +
        weights.get('point_differential', 0.20) * point_diff_normalized +
        weights.get('offensive_efficiency', 0.15) * off_efficiency +
        weights.get('defensive_efficiency', 0.15) * def_efficiency +
        weights.get('recent_form', 0.15) * form_score +
        weights.get('news_sentiment', 0.10) * sentiment_score
    )
    
    # ============================================
    # DATA QUALITY CONFIDENCE
    # ============================================
    confidence = 0.5
    
    if total_games >= 20:
        confidence += 0.25
    elif total_games >= 10:
        confidence += 0.15
    elif total_games > 0:
        confidence += 0.05
    
    if recent_games_count >= 10:
        confidence += 0.15
    elif recent_games_count >= 5:
        confidence += 0.10
    
    if len(news_data) >= 5:
        confidence += 0.10
    elif len(news_data) > 0:
        confidence += 0.05
    
    confidence = min(0.95, max(0.30, confidence))
    
    return base_strength, confidence

def analyze_news_sentiment_advanced(news_data):
    """
    Advanced news sentiment analysis using detailed configuration
    
    Args:
        news_data: List of news articles with title, content, date, source
        
    Returns:
        float: Sentiment score from 0.0 to 1.0
    """
    if not news_data:
        return 0.5
    
    sentiment_config = get_parameter(ADVANCED_CONFIG, 'news_sentiment', default={})
    recency_weights = get_parameter(sentiment_config, 'weight_by_recency', default={})
    sentiment_multipliers = get_parameter(sentiment_config, 'sentiment_multiplier', default={})
    
    total_weighted_sentiment = 0.0
    total_weight = 0.0
    
    current_date = datetime.now()
    
    for article in news_data:
        try:
            article_date = article.get('Date') or article.get('PublishedDate')
            if isinstance(article_date, str):
                article_date = datetime.fromisoformat(article_date.replace('Z', '+00:00'))
            
            days_ago = (current_date - article_date).days
            
            if days_ago == 0:
                recency_weight = recency_weights.get('today', 1.00)
            elif days_ago == 1:
                recency_weight = recency_weights.get('yesterday', 0.90)
            elif days_ago == 2:
                recency_weight = recency_weights.get('2_days_ago', 0.75)
            elif days_ago == 3:
                recency_weight = recency_weights.get('3_days_ago', 0.60)
            elif days_ago <= 7:
                recency_weight = recency_weights.get('4_7_days_ago', 0.40)
            elif days_ago <= 14:
                recency_weight = recency_weights.get('8_14_days_ago', 0.20)
            else:
                recency_weight = recency_weights.get('15_plus_days', 0.10)
            
            base_sentiment = analyze_news_sentiment([article])
            
            weighted_sentiment = base_sentiment * recency_weight
            total_weighted_sentiment += weighted_sentiment
            total_weight += recency_weight
            
        except Exception as e:
            logging.warning(f"Error processing news article sentiment: {e}")
            continue
    
    if total_weight > 0:
        avg_sentiment = total_weighted_sentiment / total_weight
        return max(0.0, min(1.0, avg_sentiment))
    
    return 0.5

def calculate_home_advantage_advanced(home_team, away_team, game_date=None):
    """
    Calculate advanced home court advantage considering multiple factors
    
    Args:
        home_team: Name of home team
        away_team: Name of away team
        game_date: Date of game (for seasonal adjustments)
        
    Returns:
        float: Home advantage boost (typically 0.08 to 0.15)
    """
    home_config = get_parameter(ADVANCED_CONFIG, 'home_advantage', default={})
    base_advantage = get_parameter(home_config, 'base_advantage', default=0.10)
    
    home_boost = base_advantage
    
    if game_date:
        if isinstance(game_date, str):
            game_date = datetime.fromisoformat(game_date)
        
        month = game_date.month
        season_config = get_parameter(home_config, 'time_of_season', default={})
        
        if month in [10, 11]:
            season_factor = season_config.get('early_season', 0.08)
        elif month in [12, 1, 2]:
            season_factor = season_config.get('mid_season', 0.10)
        elif month in [3, 4]:
            season_factor = season_config.get('late_season', 0.12)
        else:
            season_factor = base_advantage
        
        home_boost = season_factor
    
    return home_boost

def predict_game_outcome_advanced(home_team, away_team, game_date=None):
    """
    Enhanced game prediction using advanced configuration
    
    Args:
        home_team: Name of home team
        away_team: Name of away team
        game_date: Optional date for backtesting
        
    Returns:
        dict: Comprehensive prediction with scores, confidence, and reasoning
    """
    try:
        home_stats = get_team_stats(home_team, as_of_date=game_date)
        away_stats = get_team_stats(away_team, as_of_date=game_date)
        
        home_recent = get_recent_matches(home_team, days=30, as_of_date=game_date)
        away_recent = get_recent_matches(away_team, days=30, as_of_date=game_date)
        
        home_news = get_team_news(home_team, limit=15, as_of_date=game_date)
        away_news = get_team_news(away_team, limit=15, as_of_date=game_date)
        
        if isinstance(home_recent, pd.DataFrame) and not home_recent.empty:
            home_form_dict = {
                'win_percentage': len(home_recent[home_recent.get('result') == 'W']) / len(home_recent) if len(home_recent) > 0 else 0.5,
                'total_games': len(home_recent)
            }
        else:
            home_form_dict = {'win_percentage': 0.5, 'total_games': 0}
            
        if isinstance(away_recent, pd.DataFrame) and not away_recent.empty:
            away_form_dict = {
                'win_percentage': len(away_recent[away_recent.get('result') == 'W']) / len(away_recent) if len(away_recent) > 0 else 0.5,
                'total_games': len(away_recent)
            }
        else:
            away_form_dict = {'win_percentage': 0.5, 'total_games': 0}
        
        home_context = {
            'team_stats': home_stats if home_stats else {},
            'recent_form': home_form_dict,
            'news': home_news if home_news else []
        }
        
        away_context = {
            'team_stats': away_stats if away_stats else {},
            'recent_form': away_form_dict,
            'news': away_news if away_news else []
        }
        
        home_strength, home_conf = calculate_advanced_team_strength(home_context, away_context)
        away_strength, away_conf = calculate_advanced_team_strength(away_context, home_context)
        
        home_advantage = calculate_home_advantage_advanced(home_team, away_team, game_date)
        home_strength_adjusted = home_strength + home_advantage
        
        prediction_gap = home_strength_adjusted - away_strength
        
        if prediction_gap > 0:
            predicted_winner = home_team
            win_probability = 0.50 + min(0.45, prediction_gap * 1.5)
        else:
            predicted_winner = away_team
            win_probability = 0.50 + min(0.45, abs(prediction_gap) * 1.5)
        
        base_confidence = (home_conf + away_conf) / 2
        
        if abs(prediction_gap) > 0.25:
            confidence = min(0.95, base_confidence * 1.3)
        elif abs(prediction_gap) > 0.15:
            confidence = min(0.85, base_confidence * 1.2)
        else:
            confidence = min(0.75, base_confidence)
        
        score_config = get_parameter(ADVANCED_CONFIG, 'score_prediction', default={})
        league_avg = get_parameter(score_config, 'base_scoring', 'league_average', default=112.0)
        home_court_pts = get_parameter(score_config, 'home_court_points', default=3.0)
        
        home_score = int(league_avg * (1 + (home_strength - 0.5) * 0.4) + home_court_pts)
        away_score = int(league_avg * (1 + (away_strength - 0.5) * 0.4))
        
        result = {
            'home_team': home_team,
            'away_team': away_team,
            'predicted_winner': predicted_winner,
            'win_probability': round(win_probability, 3),
            'confidence': round(confidence, 3),
            'predicted_scores': {
                'home': home_score,
                'away': away_score,
                'spread': home_score - away_score
            },
            'team_strengths': {
                'home': round(home_strength, 3),
                'away': round(away_strength, 3),
                'home_with_advantage': round(home_strength_adjusted, 3)
            },
            'factors': {
                'home_advantage': round(home_advantage, 3),
                'prediction_gap': round(prediction_gap, 3)
            }
        }
        
        return result
        
    except Exception as e:
        logging.error(f"Error in enhanced prediction: {e}")
        raise

if __name__ == '__main__':
    result = predict_game_outcome_advanced('Los Angeles Lakers', 'Boston Celtics')
    print("\nAdvanced Prediction Result:")
    print(f"Winner: {result['predicted_winner']}")
    print(f"Win Probability: {result['win_probability']:.1%}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"\nPredicted Score:")
    print(f"  {result['home_team']}: {result['predicted_scores']['home']}")
    print(f"  {result['away_team']}: {result['predicted_scores']['away']}")
    print(f"  Spread: {result['predicted_scores']['spread']:+d}")

