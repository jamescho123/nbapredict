import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import os
import requests
from bs4 import BeautifulSoup

# Import calibration system
try:
    from apply_model_calibration import apply_calibration
    CALIBRATION_AVAILABLE = True
except ImportError:
    CALIBRATION_AVAILABLE = False
    logging.warning("Calibration system not available")

# Import model configuration
try:
    from model_config_advanced import load_config, get_parameter
    MODEL_CONFIG = load_config()
    USE_ADVANCED_CONFIG = True
except ImportError:
    try:
        from model_config import load_config
        MODEL_CONFIG = load_config()
        USE_ADVANCED_CONFIG = False
    except ImportError:
        logging.warning("Model config not available, using defaults")
        USE_ADVANCED_CONFIG = False
        MODEL_CONFIG = {
            'home_advantage': 0.1,
            'strength_weights': {
                'win_percentage': 0.30,
                'point_differential': 0.25,
                'offensive_efficiency': 0.15,
                'defensive_efficiency': 0.10,
                'recent_form': 0.10,
                'news_sentiment': 0.10
            },
            'score_prediction': {'home_court_points': 3},
            'calibration': {'smoothing_factor': 0.7, 'min_confidence': 0.15, 'max_confidence': 0.80},
            'confidence_weights': {
                'low_data_quality': {'base_confidence': 0.6, 'data_quality': 0.2, 'head_to_head': 0.1, 'form_consistency': 0.1},
                'high_data_quality': {'base_confidence': 0.4, 'data_quality': 0.3, 'head_to_head': 0.2, 'form_consistency': 0.1}
            }
        }

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

# Model performance tracking
PERFORMANCE_FILE = 'model_performance.json'


def _get_current_season_year():
    """Return the current NBA season end year (e.g. Oct 2024 -> 2025)."""
    now = datetime.now()
    if now.month >= 10:
        return now.year + 1
    return now.year


def fetch_basketball_reference_team_stats(team_name):
    """
    Fetch team statistics from Basketball-Reference standings as a fallback
    when our Matches-based statistics are missing.
    """
    try:
        season_year = _get_current_season_year()
        url = f"https://www.basketball-reference.com/leagues/NBA_{season_year}_standings.html"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        }

        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        tables = []
        for table_id in ["confs_standings_E", "confs_standings_W"]:
            table = soup.find("table", id=table_id)
            if table and table.tbody:
                tables.append(table)

        target_name = team_name.strip().lower()

        for table in tables:
            for row in table.tbody.find_all("tr"):
                # Skip header or separator rows
                if row.get("class") and "thead" in row.get("class", []):
                    continue

                team_link = row.find("a")
                if not team_link:
                    continue

                name = team_link.get_text(strip=True)
                if name.strip().lower() != target_name:
                    continue

                wins_cell = row.find("td", {"data-stat": "wins"})
                losses_cell = row.find("td", {"data-stat": "losses"})
                pts_cell = row.find("td", {"data-stat": "pts"})
                opp_pts_cell = row.find("td", {"data-stat": "opp_pts"})

                if not wins_cell or not losses_cell:
                    continue

                try:
                    wins = int(wins_cell.get_text(strip=True))
                    losses = int(losses_cell.get_text(strip=True))
                except ValueError:
                    continue

                games = wins + losses

                points_for = 0
                points_against = 0

                try:
                    if pts_cell and opp_pts_cell and games > 0:
                        pts_ppg = float(pts_cell.get_text(strip=True))
                        opp_ppg = float(opp_pts_cell.get_text(strip=True))
                        points_for = int(round(pts_ppg * games))
                        points_against = int(round(opp_ppg * games))
                except ValueError:
                    points_for = 0
                    points_against = 0

                logging.info(
                    "Fetched Basketball-Reference fallback stats for %s: %s-%s",
                    name,
                    wins,
                    losses,
                )

                return {
                    "TeamName": name,
                    "Wins": wins,
                    "Losses": losses,
                    "PointsFor": points_for,
                    "PointsAgainst": points_against,
                }

        logging.warning(
            "Basketball-Reference fallback stats not found for team: %s", team_name
        )
        return None
    except Exception as exc:
        logging.error(
            "Failed to fetch Basketball-Reference team stats for %s: %s",
            team_name,
            exc,
        )
        return None


def load_model_performance():
    """Load historical model performance data"""
    if os.path.exists(PERFORMANCE_FILE):
        try:
            with open(PERFORMANCE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        'predictions': [],
        'accuracy_by_confidence': {},
        'total_predictions': 0,
        'correct_predictions': 0
    }

def save_model_performance(performance_data):
    """Save model performance data"""
    try:
        with open(PERFORMANCE_FILE, 'w') as f:
            json.dump(performance_data, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save performance data: {e}")

def record_prediction(prediction_data, actual_winner=None):
    """Record a prediction for later accuracy tracking"""
    performance = load_model_performance()
    
    prediction_record = {
        'timestamp': datetime.now().isoformat(),
        'home_team': prediction_data['home_team'],
        'away_team': prediction_data['away_team'],
        'predicted_winner': prediction_data['predicted_winner'],
        'confidence': prediction_data['confidence'],
        'actual_winner': actual_winner,
        'is_correct': actual_winner == prediction_data['predicted_winner'] if actual_winner else None
    }
    
    performance['predictions'].append(prediction_record)
    
    # Keep only last 1000 predictions to avoid file bloat
    if len(performance['predictions']) > 1000:
        performance['predictions'] = performance['predictions'][-1000:]
    
    # Update accuracy statistics
    if actual_winner:
        performance['total_predictions'] += 1
        if prediction_record['is_correct']:
            performance['correct_predictions'] += 1
        
        # Update average confidence
        if 'avg_confidence' not in performance:
            performance['avg_confidence'] = prediction_data['confidence']
        else:
            # Running average
            n = performance['total_predictions']
            performance['avg_confidence'] = ((n - 1) * performance['avg_confidence'] + prediction_data['confidence']) / n
        
        # Update accuracy by confidence level
        conf_level = round(prediction_data['confidence'], 1)
        if conf_level not in performance['accuracy_by_confidence']:
            performance['accuracy_by_confidence'][conf_level] = {'correct': 0, 'total': 0}
        
        performance['accuracy_by_confidence'][conf_level]['total'] += 1
        if prediction_record['is_correct']:
            performance['accuracy_by_confidence'][conf_level]['correct'] += 1
    
    save_model_performance(performance)
    return performance

def calibrate_confidence(base_confidence, performance_data):
    """Calibrate confidence based on historical accuracy"""
    if not performance_data['accuracy_by_confidence']:
        return base_confidence
    
    # Find the closest confidence level in historical data
    conf_levels = list(performance_data['accuracy_by_confidence'].keys())
    closest_level = min(conf_levels, key=lambda x: abs(x - base_confidence))
    
    historical_data = performance_data['accuracy_by_confidence'][closest_level]
    if historical_data['total'] >= 5:  # Minimum sample size
        historical_accuracy = historical_data['correct'] / historical_data['total']
        
        # Calibrate confidence based on historical accuracy
        # If historical accuracy is lower than confidence, reduce confidence
        # If historical accuracy is higher than confidence, increase confidence
        calibration_factor = historical_accuracy / closest_level if closest_level > 0 else 1.0
        calibrated_confidence = base_confidence * calibration_factor
        
        # Ensure calibrated confidence is within reasonable bounds
        return max(0.1, min(0.95, calibrated_confidence))
    
    return base_confidence

def get_model_performance_stats():
    """Get comprehensive model performance statistics"""
    performance = load_model_performance()
    
    if performance['total_predictions'] == 0:
        return {
            'overall_accuracy': 0.0,
            'total_predictions': 0,
            'confidence_accuracy': {},
            'recent_accuracy': 0.0,
            'model_reliability': 'No data available'
        }
    
    overall_accuracy = performance['correct_predictions'] / performance['total_predictions']
    
    # Calculate accuracy by confidence level
    confidence_accuracy = {}
    for conf_level, data in performance['accuracy_by_confidence'].items():
        if data['total'] >= 3:  # Minimum sample size
            confidence_accuracy[conf_level] = {
                'accuracy': data['correct'] / data['total'],
                'total_predictions': data['total']
            }
    
    # Calculate recent accuracy (last 50 predictions)
    recent_predictions = [p for p in performance['predictions'] if p.get('is_correct') is not None][-50:]
    if recent_predictions:
        recent_correct = sum(1 for p in recent_predictions if p['is_correct'])
        recent_accuracy = recent_correct / len(recent_predictions)
    else:
        recent_accuracy = 0.0
    
    # Determine model reliability
    if overall_accuracy >= 0.7:
        reliability = 'High'
    elif overall_accuracy >= 0.6:
        reliability = 'Medium'
    else:
        reliability = 'Low'
    
    return {
        'overall_accuracy': overall_accuracy,
        'total_predictions': performance['total_predictions'],
        'confidence_accuracy': confidence_accuracy,
        'recent_accuracy': recent_accuracy,
        'model_reliability': reliability
    }

def get_upcoming_games(limit=50):
    """Get upcoming games from the schedule"""
    conn = connect_to_database()
    if not conn:
        return []
    
    try:
        query = f'''
        SELECT "GameID", "Date", "Time", "HomeTeam", "AwayTeam", "Venue", "City", "State"
        FROM "{DB_SCHEMA}"."Schedule"
        WHERE "Date" >= CURRENT_DATE
        AND "Status" = 'Scheduled'
        ORDER BY "Date", "Time"
        LIMIT %s
        '''
        
        df = pd.read_sql_query(query, conn, params=[limit])
        conn.close()
        
        return df.to_dict('records')
        
    except Exception as e:
        logging.error(f"Error fetching upcoming games: {e}")
        conn.close()
        return []

def get_games_by_date_range(start_date, end_date):
    """Get games within a date range"""
    conn = connect_to_database()
    if not conn:
        return []
    
    try:
        query = f'''
        SELECT "GameID", "Date", "Time", "HomeTeam", "AwayTeam", "Venue", "City", "State"
        FROM "{DB_SCHEMA}"."Schedule"
        WHERE "Date" BETWEEN %s AND %s
        ORDER BY "Date", "Time"
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        
        return df.to_dict('records')
        
    except Exception as e:
        logging.error(f"Error fetching games by date range: {e}")
        conn.close()
        return []

def get_games_today():
    """Get games scheduled for today"""
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    return get_games_by_date_range(today, today)

def get_games_this_week():
    """Get games scheduled for this week"""
    from datetime import date, timedelta
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    return get_games_by_date_range(
        week_start.strftime('%Y-%m-%d'),
        week_end.strftime('%Y-%m-%d')
    )

def predict_game_scores(home_team, away_team, home_context, away_context, h2h_data):
    """Predict final scores for both teams"""
    try:
        # Import the score prediction model
        from score_prediction_model import ScorePredictionModel
        
        # Initialize model
        model = ScorePredictionModel()
        
        # Predict scores
        home_score, away_score = model.predict_scores(
            home_team, away_team, home_context, away_context, h2h_data
        )
        
        return {
            'home_score': home_score,
            'away_score': away_score,
            'total_points': home_score + away_score,
            'point_spread': home_score - away_score,
            'margin_of_victory': abs(home_score - away_score)
        }
        
    except Exception as e:
        logging.error(f"Score prediction failed: {e}")
        # Fallback to simple prediction
        return predict_simple_scores(home_team, away_team, home_context, away_context)

def predict_simple_scores(home_team, away_team, home_context, away_context):
    """Simple score prediction as fallback"""
    # Base scores
    home_base = 110
    away_base = 110
    
    # Adjust based on team strength
    home_strength = calculate_team_strength(home_context)[0] if home_context else 0.5
    away_strength = calculate_team_strength(away_context)[0] if away_context else 0.5
    
    # Home court advantage from config
    home_advantage = MODEL_CONFIG.get('score_prediction', {}).get('home_court_points', 3)
    
    # Calculate final scores
    home_score = int(home_base + (home_strength - 0.5) * 20 + home_advantage)
    away_score = int(away_base + (away_strength - 0.5) * 20)
    
    # Add some randomness
    import random
    home_score += random.randint(-5, 6)
    away_score += random.randint(-5, 6)
    
    # Ensure realistic bounds
    home_score = max(80, min(150, home_score))
    away_score = max(80, min(150, away_score))
    
    return {
        'home_score': home_score,
        'away_score': away_score,
        'total_points': home_score + away_score,
        'point_spread': home_score - away_score,
        'margin_of_victory': abs(home_score - away_score)
    }

def predict_gambling_statistics(score_predictions, home_team, away_team):
    """Predict gambling-relevant statistics"""
    try:
        # Import the score prediction model
        from score_prediction_model import ScorePredictionModel
        
        # Initialize model
        model = ScorePredictionModel()
        
        # Get scores
        home_score = score_predictions['home_score']
        away_score = score_predictions['away_score']
        
        # Predict gambling stats
        gambling_stats = model.predict_gambling_stats(
            home_score, away_score, home_team, away_team, {}, {}
        )
        
        return gambling_stats
        
    except Exception as e:
        logging.error(f"Gambling stats prediction failed: {e}")
        # Fallback to simple gambling stats
        return predict_simple_gambling_stats(score_predictions)

def predict_simple_gambling_stats(score_predictions):
    """Simple gambling statistics prediction as fallback"""
    home_score = score_predictions['home_score']
    away_score = score_predictions['away_score']
    
    # First half predictions (typically 45-50% of total)
    first_half_factor = 0.47
    home_first_half = int(home_score * first_half_factor)
    away_first_half = int(away_score * first_half_factor)
    
    # Quarters
    home_q1 = int(home_first_half / 2)
    away_q1 = int(away_first_half / 2)
    home_q2 = home_first_half - home_q1
    away_q2 = away_first_half - away_q1
    
    # Third quarter
    third_q_factor = 0.26
    home_q3 = int(home_score * third_q_factor)
    away_q3 = int(away_score * third_q_factor)
    
    # Fourth quarter
    home_q4 = home_score - home_first_half - home_q3
    away_q4 = away_score - away_first_half - away_q3
    
    return {
        'home_score': home_score,
        'away_score': away_score,
        'total_points': home_score + away_score,
        'point_spread': home_score - away_score,
        'home_first_half': home_first_half,
        'away_first_half': away_first_half,
        'first_half_total': home_first_half + away_first_half,
        'home_second_half': home_score - home_first_half,
        'away_second_half': away_score - away_first_half,
        'second_half_total': (home_score - home_first_half) + (away_score - away_first_half),
        'home_q1': home_q1,
        'away_q1': away_q1,
        'q1_total': home_q1 + away_q1,
        'home_q2': home_q2,
        'away_q2': away_q2,
        'q2_total': home_q2 + away_q2,
        'home_q3': home_q3,
        'away_q3': away_q3,
        'q3_total': home_q3 + away_q3,
        'home_q4': home_q4,
        'away_q4': away_q4,
        'q4_total': home_q4 + away_q4,
        'home_team_total': home_score,
        'away_team_total': away_score,
        'margin_of_victory': abs(home_score - away_score),
        'overtime_probability': 0.05 if abs(home_score - away_score) <= 3 else 0.01,
        'confidence': {
            'moneyline': min(0.95, 0.5 + abs(score_predictions['point_spread']) / 20),
            'spread': min(0.95, 0.6 + abs(score_predictions['point_spread']) / 15),
            'total': min(0.95, 0.7 - abs(score_predictions['total_points'] - 220) / 100),
            'first_half': min(0.95, 0.65 - abs((home_first_half + away_first_half) - 110) / 80)
        }
    }

def connect_to_database():
    """Connect to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

def get_team_list():
    """Get list of all teams from database"""
    conn = connect_to_database()
    if not conn:
        return []
    
    try:
        query = f'SELECT "TeamName" FROM "{DB_SCHEMA}"."Teams" ORDER BY "TeamName"'
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df['TeamName'].tolist()
    except Exception as e:
        logging.error(f"Error fetching teams: {e}")
        conn.close()
        return []

def get_team_stats(team_name, as_of_date=None):
    """Get team statistics calculated from Matches table up to a specific date"""
    conn = connect_to_database()
    if not conn:
        return None
    
    try:
        # Calculate stats from Matches table, only including games before as_of_date
        query = f'''
        WITH team_matches AS (
            SELECT 
                CASE 
                    WHEN "HomeTeamName" = %s THEN "HomeTeamScore"
                    ELSE "VisitorPoints"
                END as points_for,
                CASE 
                    WHEN "HomeTeamName" = %s THEN "VisitorPoints"
                    ELSE "HomeTeamScore"
                END as points_against,
                CASE 
                    WHEN "HomeTeamName" = %s AND "HomeTeamScore" > "VisitorPoints" THEN 1
                    WHEN "VisitorTeamName" = %s AND "VisitorPoints" > "HomeTeamScore" THEN 1
                    ELSE 0
                END as is_win,
                CASE 
                    WHEN "HomeTeamName" = %s AND "HomeTeamScore" < "VisitorPoints" THEN 1
                    WHEN "VisitorTeamName" = %s AND "VisitorPoints" < "HomeTeamScore" THEN 1
                    ELSE 0
                END as is_loss
            FROM "{DB_SCHEMA}"."Matches"
            WHERE ("HomeTeamName" = %s OR "VisitorTeamName" = %s)
        '''
        
        params = [team_name] * 8
        
        # Add date filter if as_of_date is provided
        if as_of_date:
            query += ' AND "Date" < %s'
            params.append(as_of_date)
        
        query += '''
        )
        SELECT 
            SUM(is_win) as "Wins",
            SUM(is_loss) as "Losses",
            SUM(points_for) as "PointsFor",
            SUM(points_against) as "PointsAgainst"
        FROM team_matches
        '''
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if len(df) > 0 and df.iloc[0]['Wins'] is not None:
            stats = df.iloc[0].to_dict()
            stats['TeamName'] = team_name
            # Convert to int if they're not None
            for key in ['Wins', 'Losses', 'PointsFor', 'PointsAgainst']:
                if stats[key] is not None:
                    stats[key] = int(stats[key])
                else:
                    stats[key] = 0
            return stats
        return None
    except Exception as e:
        logging.error(f"Error calculating team stats from Matches: {e}")
        if conn:
            conn.close()
        return None

def get_recent_matches(team_name, days=30, as_of_date=None):
    """Get recent matches for a team up to a specific date"""
    conn = connect_to_database()
    if not conn:
        return pd.DataFrame()
    
    try:
        # Get matches from the last N days before as_of_date
        if as_of_date:
            if isinstance(as_of_date, str):
                reference_date = datetime.strptime(as_of_date, '%Y-%m-%d')
            else:
                reference_date = as_of_date
        else:
            reference_date = datetime.now()
        
        cutoff_date = (reference_date - timedelta(days=days)).strftime('%Y-%m-%d')
        
        query = f'''
        SELECT "Date", "HomeTeamName", "VisitorTeamName", "HomeTeamScore", "VisitorPoints"
        FROM "{DB_SCHEMA}"."Matches"
        WHERE ("HomeTeamName" = %s OR "VisitorTeamName" = %s)
        AND "Date" >= %s
        '''
        
        params = [team_name, team_name, cutoff_date]
        
        # Add upper bound date filter
        if as_of_date:
            query += ' AND "Date" < %s'
            params.append(as_of_date)
        
        query += ' ORDER BY "Date" DESC'
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        logging.error(f"Error fetching recent matches: {e}")
        conn.close()
        return pd.DataFrame()

def get_team_news(team_name, limit=15, as_of_date=None):
    """Get recent news about a team by searching in Title and Content, up to a specific date"""
    conn = connect_to_database()
    if not conn:
        return []
    
    try:
        # Get news for the team by searching in Title and Content
        query = f'''
        SELECT n."NewsID", n."Title", n."Content", n."Date", n."URL"
        FROM "{DB_SCHEMA}"."News" n
        WHERE (n."Title" ILIKE %s OR n."Content" ILIKE %s)
        '''
        
        team_pattern = f'%{team_name}%'
        params = [team_pattern, team_pattern]
        
        # Add date filter if as_of_date is provided
        if as_of_date:
            query += ' AND n."Date" < %s'
            params.append(as_of_date)
        
        query += ' ORDER BY n."Date" DESC LIMIT %s'
        params.append(limit)
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df.to_dict('records')
    except Exception as e:
        logging.error(f"Error fetching team news: {e}")
        if conn:
            conn.close()
        return []

def get_time_weighted_team_news(team_name, days_back=30, limit=20, as_of_date=None):
    """Get time-weighted news for a team by searching in Title and Content, up to a specific date"""
    conn = connect_to_database()
    if not conn:
        return []
    
    try:
        from datetime import datetime, timedelta
        
        # Determine reference date
        if as_of_date:
            if isinstance(as_of_date, str):
                reference_date = datetime.strptime(as_of_date, '%Y-%m-%d')
            else:
                reference_date = as_of_date
        else:
            reference_date = datetime.now()
        
        cutoff_date = (reference_date - timedelta(days=days_back)).strftime('%Y-%m-%d')
        reference_date_str = reference_date.strftime('%Y-%m-%d')
        
        # Get recent news with time-based scoring relative to as_of_date
        query = f'''
        SELECT n."NewsID", n."Title", n."Content", n."Date", n."URL",
               CASE 
                   WHEN n."Date" >= (%s::date - INTERVAL '1 day') THEN 1.0
                   WHEN n."Date" >= (%s::date - INTERVAL '7 days') THEN 0.8
                   WHEN n."Date" >= (%s::date - INTERVAL '30 days') THEN 0.6
                   ELSE 0.3
               END as time_weight
        FROM "{DB_SCHEMA}"."News" n
        WHERE (n."Title" ILIKE %s OR n."Content" ILIKE %s)
           AND n."Date" >= %s
           AND n."Date" < %s
        ORDER BY n."Date" DESC, time_weight DESC
        LIMIT %s
        '''
        
        team_pattern = f'%{team_name}%'
        df = pd.read_sql_query(query, conn, params=[
            reference_date_str, reference_date_str, reference_date_str,
            team_pattern, team_pattern, cutoff_date, reference_date_str, limit
        ])
        conn.close()
        
        return df.to_dict('records')
    except Exception as e:
        logging.error(f"Error fetching time-weighted team news: {e}")
        if conn:
            conn.close()
        return df.to_dict('records')
    except Exception as e:
        logging.error(f"Error fetching time-weighted team news: {e}")
        if conn:
            conn.close()
        return []

def get_general_news_search(query_text, limit=15, days_back=60):
    """Get news by searching for keywords in Title and Content"""
    conn = connect_to_database()
    if not conn:
        return []
    
    try:
        from datetime import datetime, timedelta
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        query = f'''
        SELECT n."NewsID", n."Title", n."Content", n."Date", n."Source", n."URL"
        FROM "{DB_SCHEMA}"."News" n
        WHERE (n."Title" ILIKE %s OR n."Content" ILIKE %s)
           AND n."Date" >= %s
        ORDER BY n."Date" DESC
        LIMIT %s
        '''
        
        search_pattern = f'%{query_text}%'
        df = pd.read_sql_query(query, conn, params=[search_pattern, search_pattern, cutoff_date, limit])
        conn.close()
        
        return df.to_dict('records')
    except Exception as e:
        logging.error(f"Error searching general news: {e}")
        if conn:
            conn.close()
        return []

def get_vector_news_search(query_vector, limit=10, days_back=90):
    """Search news using vector similarity (pgvector)"""
    conn = connect_to_database()
    if not conn:
        return []
        
    try:
        from datetime import datetime, timedelta
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # pgvector usage: <=> for cosine distance, <-> for Euclidean
        # We use cosine similarity (1 - distance)
        query = f'''
        SELECT n."NewsID", n."Title", n."Content", n."Date", n."Source", n."URL",
               1 - (vn."NewsVector" <=> %s::vector) as similarity
        FROM "{DB_SCHEMA}"."News" n
        JOIN "{DB_SCHEMA}"."VectorNews" vn ON n."NewsID" = vn."NewsID"
        WHERE n."Date" >= %s
        ORDER BY similarity DESC
        LIMIT %s
        '''
        
        df = pd.read_sql_query(query, conn, params=[query_vector, cutoff_date, limit])
        conn.close()
        return df.to_dict('records')
    except Exception as e:
        logging.error(f"Error in vector news search: {e}")
        if conn:
            conn.close()
        return []

def get_player_stats(team_name, limit=10):
    """Get player statistics for a team using TeamPlayer relationship"""
    conn = connect_to_database()
    if not conn:
        return pd.DataFrame()
    
    try:
        # Join Players with TeamPlayer to get current team roster
        # Cast PlayerID to match types
        query = f'''
        SELECT p."PlayerName", p."Position", p."Height", p."Weight"
        FROM "{DB_SCHEMA}"."Players" p
        INNER JOIN "{DB_SCHEMA}"."TeamPlayer" tp 
            ON p."PlayerID"::varchar = tp."PlayerID"
        WHERE tp."TeamName" = %s
        ORDER BY tp."From" DESC
        LIMIT %s
        '''
        
        df = pd.read_sql_query(query, conn, params=[team_name, limit])
        conn.close()
        return df
    except Exception as e:
        logging.error(f"Error fetching player stats: {e}")
        if conn:
            conn.close()
        return pd.DataFrame()

def get_specific_player_stats(player_name_query):
    """Get statistics for a specific player by name search"""
    conn = connect_to_database()
    if not conn:
        return None
    
    try:
        # Search for player
        query = f'''
        SELECT p."PlayerID", p."PlayerName", p."Position", p."Height", p."Weight", p."BirthDate", 
               tp."TeamName"
        FROM "{DB_SCHEMA}"."Players" p
        LEFT JOIN "{DB_SCHEMA}"."TeamPlayer" tp 
            ON p."PlayerID"::varchar = tp."PlayerID" 
            AND tp."To" IS NULL -- Currenlty active team
        WHERE p."PlayerName" ILIKE %s
        LIMIT 1
        '''
        
        search_pattern = f'%{player_name_query}%'
        df = pd.read_sql_query(query, conn, params=[search_pattern])
        conn.close()
        
        if not df.empty:
            return df.iloc[0].to_dict()
        return None
        
    except Exception as e:
        logging.error(f"Error searching for player: {e}")
        if conn:
            conn.close()
        return None

def calculate_team_form(team_name, days=10, as_of_date=None):
    """Calculate recent form (wins/losses) for a team up to a specific date"""
    recent_matches = get_recent_matches(team_name, days, as_of_date=as_of_date)
    
    if recent_matches.empty:
        return {'wins': 0, 'losses': 0, 'win_percentage': 0.0}
    
    wins = 0
    losses = 0
    
    for _, match in recent_matches.iterrows():
        if match['HomeTeamName'] == team_name:
            if match['HomeTeamScore'] > match['VisitorPoints']:
                wins += 1
            else:
                losses += 1
        else:  # Away team
            if match['VisitorPoints'] > match['HomeTeamScore']:
                wins += 1
            else:
                losses += 1
    
    total_games = wins + losses
    win_percentage = wins / total_games if total_games > 0 else 0.0
    
    return {
        'wins': wins,
        'losses': losses,
        'win_percentage': win_percentage,
        'total_games': total_games
    }

def get_head_to_head_record(team1, team2, limit=10, as_of_date=None):
    """Get head-to-head record between two teams up to a specific date"""
    conn = connect_to_database()
    if not conn:
        return {'team1_wins': 0, 'team2_wins': 0, 'total_games': 0}
    
    try:
        query = f'''
        SELECT "HomeTeamName", "VisitorTeamName", "HomeTeamScore", "VisitorPoints"
        FROM "{DB_SCHEMA}"."Matches"
        WHERE (("HomeTeamName" = %s AND "VisitorTeamName" = %s)
           OR ("HomeTeamName" = %s AND "VisitorTeamName" = %s))
        '''
        
        params = [team1, team2, team2, team1]
        
        # Add date filter if as_of_date is provided
        if as_of_date:
            query += ' AND "Date" < %s'
            params.append(as_of_date)
        
        query += ' ORDER BY "Date" DESC LIMIT %s'
        params.append(limit)
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        team1_wins = 0
        team2_wins = 0
        
        for _, match in df.iterrows():
            if match['HomeTeamName'] == team1:
                if match['HomeTeamScore'] > match['VisitorPoints']:
                    team1_wins += 1
                else:
                    team2_wins += 1
            else:  # team1 is away
                if match['VisitorPoints'] > match['HomeTeamScore']:
                    team1_wins += 1
                else:
                    team2_wins += 1
        
        return {
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'total_games': len(df)
        }
    except Exception as e:
        logging.error(f"Error fetching head-to-head record: {e}")
        conn.close()
        return {'team1_wins': 0, 'team2_wins': 0, 'total_games': 0}

def get_team_context_data(team_name, as_of_date=None):
    """Get comprehensive context data for a team with fallback data, optionally filtered to a specific date"""
    print(f"🔍 Getting context data for {team_name}" + (f" (as of {as_of_date})" if as_of_date else ""))
    
    # Get basic team stats
    team_stats = get_team_stats(team_name, as_of_date=as_of_date)
    if team_stats is None:
        print(f"   ⚠️ No team stats found in Matches, trying Basketball-Reference fallback")
        bbr_stats = fetch_basketball_reference_team_stats(team_name)
        if bbr_stats is not None:
            team_stats = {
                'Wins': int(bbr_stats.get('Wins', 0)),
                'Losses': int(bbr_stats.get('Losses', 0)),
                'PointsFor': int(bbr_stats.get('PointsFor', 0)),
                'PointsAgainst': int(bbr_stats.get('PointsAgainst', 0)),
                'TeamName': bbr_stats.get('TeamName', team_name),
            }
            print(f"   ✅ Using Basketball-Reference stats: {team_stats['Wins']}W-{team_stats['Losses']}L")
        else:
            print(f"   ⚠️ Basketball-Reference fallback failed, using neutral 0-0 stats")
            team_stats = {'Wins': 0, 'Losses': 0, 'PointsFor': 0, 'PointsAgainst': 0}
    else:
        print(f"   ✅ Team stats found: {team_stats.get('Wins', 0)}W-{team_stats.get('Losses', 0)}L")
    
    # Get recent form
    recent_form = calculate_team_form(team_name, as_of_date=as_of_date)
    if recent_form is None or recent_form.get('total_games', 0) == 0:
        print(f"   ⚠️ No recent form found, using team stats")
        # Use team stats to simulate recent form
        wins = team_stats.get('Wins', 41)
        losses = team_stats.get('Losses', 41)
        total = wins + losses
        recent_form = {
            'wins': max(0, wins - 5),  # Simulate recent form
            'losses': max(0, losses - 5),
            'win_percentage': (wins - 5) / max(1, total - 10) if total > 10 else wins / max(1, total),
            'total_games': max(0, total - 10)
        }
    else:
        print(f"   ✅ Recent form found: {recent_form.get('wins', 0)}W-{recent_form.get('losses', 0)}L")
    
    # Get time-weighted recent news for better sentiment analysis
    team_news = get_time_weighted_team_news(team_name, days_back=30, limit=20, as_of_date=as_of_date)
    if not team_news:
        print(f"   ⚠️ No recent news found, trying broader search")
        # Try getting any news for this team
        team_news = get_team_news(team_name, limit=10, as_of_date=as_of_date)
        if not team_news:
            print(f"   ⚠️ No news found at all, using empty list")
            team_news = []
        else:
            print(f"   ✅ Found {len(team_news)} news articles")
    else:
        print(f"   ✅ Found {len(team_news)} recent news articles")
    
    # Get player stats
    player_stats = get_player_stats(team_name)
    if player_stats is None or player_stats.empty:
        print(f"   ⚠️ No player stats found")
        player_stats = pd.DataFrame()
    else:
        print(f"   ✅ Found {len(player_stats)} players")
    
    if team_news is None:
        team_news = []
    
    if player_stats is None or player_stats.empty:
        players = []
    else:
        players = player_stats.to_dict('records')
    
    return {
        'team_stats': team_stats,
        'recent_form': recent_form,
        'news': team_news,
        'players': players
    }

def prepare_prediction_data(home_team, away_team, as_of_date=None):
    """Prepare all data needed for prediction, optionally filtered to a specific date"""
    # Get context data for both teams
    home_context = get_team_context_data(home_team, as_of_date=as_of_date)
    away_context = get_team_context_data(away_team, as_of_date=as_of_date)
    
    # Get head-to-head record
    h2h_record = get_head_to_head_record(home_team, away_team, as_of_date=as_of_date)
    
    # Ensure h2h_record is not None
    if h2h_record is None:
        h2h_record = {'team1_wins': 0, 'team2_wins': 0, 'total_games': 0}
    
    # Calculate home advantage from config
    home_advantage = MODEL_CONFIG.get('home_advantage', 0.1)
    
    # Calculate rest days (simplified - would need actual schedule data)
    rest_days_home = 1  # Default
    rest_days_away = 1  # Default
    
    return {
        'home_team': home_team,
        'away_team': away_team,
        'home_context': home_context,
        'away_context': away_context,
        'head_to_head': h2h_record,
        'home_advantage': home_advantage,
        'rest_days': {
            'home': rest_days_home,
            'away': rest_days_away
        }
    }

def analyze_news_sentiment(team_news):
    """Time-weighted sentiment analysis of team news with recency bias"""
    if not team_news:
        return 0.0
    
    positive_keywords = ['win', 'victory', 'excellent', 'outstanding', 'strong', 'impressive', 'dominate', 
                        'breakthrough', 'stellar', 'exceptional', 'dominant', 'unbeaten', 'triumph', 'success']
    negative_keywords = ['loss', 'defeat', 'struggle', 'weak', 'poor', 'injury', 'suspended', 
                        'disappointing', 'struggling', 'slump', 'decline', 'concern', 'problem', 'issue']
    
    # Enhanced keywords for better sentiment detection
    very_positive_keywords = ['championship', 'playoff', 'all-star', 'mvp', 'record-breaking', 'historic']
    very_negative_keywords = ['eliminated', 'out', 'season-ending', 'serious', 'major', 'critical']
    
    from datetime import datetime, timedelta, date
    current_date = datetime.now().date()  # Use date() to match database date type
    
    weighted_sentiment = 0.0
    total_weight = 0.0
    
    for news in team_news:
        # Calculate time-based weight (more recent = higher weight)
        news_date = news.get('Date')
        if isinstance(news_date, str):
            try:
                news_date = datetime.strptime(news_date, '%Y-%m-%d').date()
            except:
                news_date = current_date - timedelta(days=30)  # Default to 30 days ago if parsing fails
        elif isinstance(news_date, datetime):
            news_date = news_date.date()  # Convert datetime to date
        elif news_date is None:
            news_date = current_date - timedelta(days=30)
        
        # Calculate days since news
        days_ago = (current_date - news_date).days
        
        # Time-based weight: exponential decay with recency bias
        # Recent news (0-7 days) gets full weight, older news gets exponentially less
        if days_ago <= 1:  # Today or yesterday
            time_weight = 1.0
        elif days_ago <= 7:  # Within a week
            time_weight = 0.8 + (0.2 * (7 - days_ago) / 7)
        elif days_ago <= 30:  # Within a month
            time_weight = 0.5 + (0.3 * (30 - days_ago) / 30)
        else:  # Older than a month
            time_weight = max(0.1, 0.5 * (0.9 ** (days_ago - 30)))  # Exponential decay
        
        # Analyze sentiment
        text = (news.get('Title', '') + ' ' + news.get('Content', '')).lower()
        
        positive_count = sum(1 for word in positive_keywords if word in text)
        negative_count = sum(1 for word in negative_keywords if word in text)
        very_positive_count = sum(1 for word in very_positive_keywords if word in text)
        very_negative_count = sum(1 for word in very_negative_keywords if word in text)
        
        if positive_count + negative_count + very_positive_count + very_negative_count > 0:
            # Calculate base sentiment
            base_sentiment = (positive_count - negative_count) / (positive_count + negative_count + very_positive_count + very_negative_count)
            
            # Apply multipliers for very positive/negative keywords
            if very_positive_count > 0:
                base_sentiment += 0.3 * (very_positive_count / (very_positive_count + 1))
            if very_negative_count > 0:
                base_sentiment -= 0.3 * (very_negative_count / (very_negative_count + 1))
            
            # Apply time weight
            weighted_sentiment += base_sentiment * time_weight
            total_weight += time_weight
    
    # Return weighted average sentiment
    return weighted_sentiment / total_weight if total_weight > 0 else 0.0

def get_news_recency_impact(team_news):
    """Calculate the recency impact factor for news"""
    if not team_news:
        return 1.0  # No impact if no news
    
    from datetime import datetime, timedelta, date
    current_date = datetime.now().date()  # Use date() to match database date type
    
    # Calculate recency impact based on how recent the news is
    most_recent_days = float('inf')
    recent_news_count = 0
    
    for news in team_news:
        news_date = news.get('Date')
        if isinstance(news_date, str):
            try:
                news_date = datetime.strptime(news_date, '%Y-%m-%d').date()
            except:
                continue
        elif isinstance(news_date, datetime):
            news_date = news_date.date()  # Convert datetime to date
        elif news_date is None:
            continue
        
        days_ago = (current_date - news_date).days
        most_recent_days = min(most_recent_days, days_ago)
        
        if days_ago <= 7:  # Recent news within a week
            recent_news_count += 1
    
    # Calculate recency impact factor
    if most_recent_days == float('inf'):
        return 1.0  # No recent news
    
    # Higher impact for more recent news and more recent news articles
    recency_factor = max(0.5, 1.0 - (most_recent_days / 30))  # Decay over 30 days
    volume_factor = min(1.5, 1.0 + (recent_news_count / 10))  # Boost for multiple recent articles
    
    return recency_factor * volume_factor

def calculate_team_strength(team_context):
    """Calculate realistic team strength based on actual database data"""
    if not team_context:
        return 0.5, 0.1  # Default neutral strength with low confidence
    
    team_stats = team_context.get('team_stats', {})
    recent_form = team_context.get('recent_form', {})
    news_sentiment = analyze_news_sentiment(team_context.get('news', []))
    
    # Get actual team performance data
    wins = team_stats.get('Wins', 0)
    losses = team_stats.get('Losses', 0)
    total_games = wins + losses
    win_percentage = wins / total_games if total_games > 0 else 0.5
    
    # Get actual scoring data
    points_for = team_stats.get('PointsFor', 0)
    points_against = team_stats.get('PointsAgainst', 0)
    
    # Calculate realistic metrics based on actual data
    if total_games > 0:
        points_per_game = points_for / total_games
        points_allowed_per_game = points_against / total_games
        point_differential = points_per_game - points_allowed_per_game
        
        # More realistic point differential normalization
        # NBA teams typically range from -10 to +10 points per game
        normalized_differential = max(0, min(1, (point_differential + 10) / 20))
        
        # Calculate offensive and defensive efficiency
        offensive_efficiency = min(1.0, points_per_game / 120)  # Normalize to 120 PPG baseline
        defensive_efficiency = max(0, 1 - (points_allowed_per_game / 120))  # Lower is better for defense
    else:
        normalized_differential = 0.5
        offensive_efficiency = 0.5
        defensive_efficiency = 0.5
    
    # Recent form with realistic variation
    recent_win_pct = recent_form.get('win_percentage', win_percentage)
    recent_games = recent_form.get('total_games', 0)
    
    # Add realistic recent form variation based on actual performance
    if recent_games > 0:
        # Recent form should vary from overall record but not too drastically
        form_variation = np.random.uniform(-0.1, 0.1)  # ±10% variation
        recent_win_pct = max(0.1, min(0.9, recent_win_pct + form_variation))
    
    # News sentiment with realistic impact
    news_recency_impact = get_news_recency_impact(team_context.get('news', []))
    sentiment_factor = ((news_sentiment + 1) / 2) * news_recency_impact
    sentiment_factor = min(1.0, max(0.0, sentiment_factor))
    
    # Calculate data quality based on actual data availability
    data_quality_score = 0.0
    
    # Game count quality (more realistic)
    if total_games >= 20:  # Good sample size
        data_quality_score += 0.4
    elif total_games >= 10:  # Moderate sample
        data_quality_score += 0.3
    elif total_games > 0:  # Limited sample
        data_quality_score += 0.2
    else:
        data_quality_score += 0.1
    
    # Recent form quality
    if recent_games >= 5:
        data_quality_score += 0.2
    elif recent_games > 0:
        data_quality_score += 0.1
    
    # News data quality
    news_count = len(team_context.get('news', []))
    if news_count >= 5:
        data_quality_score += 0.2
    elif news_count > 0:
        data_quality_score += 0.1
    
    # Scoring data quality
    if points_for > 0 and points_against > 0:
        data_quality_score += 0.2
    
    # Ensure minimum data quality
    data_quality_score = max(0.2, data_quality_score)
    
    # Calculate realistic team strength with proper weighting from config
    weights = MODEL_CONFIG.get('strength_weights', {})
    overall_strength = (
        weights.get('win_percentage', 0.30) * win_percentage +
        weights.get('recent_form', 0.20) * recent_win_pct +
        weights.get('point_differential', 0.15) * normalized_differential +
        weights.get('offensive_efficiency', 0.15) * offensive_efficiency +
        weights.get('defensive_efficiency', 0.10) * defensive_efficiency +
        weights.get('news_sentiment', 0.10) * sentiment_factor
    )
    
    # Ensure realistic strength bounds
    overall_strength = max(0.1, min(0.9, overall_strength))
    
    # Calculate confidence based on data quality and sample size
    confidence = min(0.95, data_quality_score + (min(total_games, 82) / 82) * 0.3)
    
    return overall_strength, confidence

def predict_game_outcome(home_team, away_team, game_date=None):
    """Predict game outcome using database data with enhanced confidence calculation and score prediction
    
    Args:
        home_team: Name of the home team
        away_team: Name of the away team
        game_date: Optional date of the game for backtesting (only use data before this date)
    """
    try:
        # Prepare all data (for backtesting, only use data before game_date)
        prediction_data = prepare_prediction_data(home_team, away_team, as_of_date=game_date)
        
        # Calculate team strengths with confidence
        home_strength, home_confidence = calculate_team_strength(prediction_data['home_context'])
        away_strength, away_confidence = calculate_team_strength(prediction_data['away_context'])
        
        # Apply home advantage
        home_advantage = prediction_data['home_advantage']
        home_strength += home_advantage
        
        # Calculate prediction score
        prediction_score = home_strength - away_strength
        
        # Realistic confidence calculation based on prediction strength
        prediction_strength = abs(prediction_score)
        
        # Improved confidence scaling - less conservative, more realistic
        if prediction_strength > 0.4:  # Very strong prediction
            base_confidence = min(0.90, prediction_strength * 2.0 + 0.50)
        elif prediction_strength > 0.2:  # Strong prediction
            base_confidence = min(0.85, prediction_strength * 2.5 + 0.45)
        elif prediction_strength > 0.1:  # Moderate prediction
            base_confidence = min(0.75, prediction_strength * 3.0 + 0.40)
        else:  # Weak prediction
            base_confidence = min(0.65, prediction_strength * 3.5 + 0.35)
        
        # Data quality factor
        data_quality_factor = (home_confidence + away_confidence) / 2
        
        # Head-to-head factor
        h2h = prediction_data['head_to_head']
        h2h_games = h2h.get('total_games', 0)
        h2h_factor = min(1.0, h2h_games / 10)  # More H2H data = higher confidence
        
        # Recent form consistency factor
        home_form = prediction_data['home_context']['recent_form']
        away_form = prediction_data['away_context']['recent_form']
        
        home_form_games = home_form.get('total_games', 0)
        away_form_games = away_form.get('total_games', 0)
        form_consistency = min(1.0, (home_form_games + away_form_games) / 20)
        
        # Improved confidence calculation based on data quality from config
        conf_weights = MODEL_CONFIG.get('confidence_weights', {})
        
        if data_quality_factor < 0.3:  # Low data quality
            # Less conservative confidence for limited data
            low_weights = conf_weights.get('low_data_quality', {})
            confidence = (
                low_weights.get('base_confidence', 0.7) * base_confidence +
                low_weights.get('data_quality', 0.15) * data_quality_factor +
                low_weights.get('head_to_head', 0.08) * h2h_factor +
                low_weights.get('form_consistency', 0.07) * form_consistency
            )
            # Moderate boost for having any data
            confidence += 0.10
        else:
            # Standard calculation for good data quality - more weight on base confidence
            high_weights = conf_weights.get('high_data_quality', {})
            confidence = (
                high_weights.get('base_confidence', 0.6) * base_confidence +
                high_weights.get('data_quality', 0.20) * data_quality_factor +
                high_weights.get('head_to_head', 0.12) * h2h_factor +
                high_weights.get('form_consistency', 0.08) * form_consistency
            )
        
        # Add moderate confidence boost based on prediction strength
        if prediction_strength > 0.3:
            confidence += 0.08  # 8% boost for very strong predictions
        elif prediction_strength > 0.2:
            confidence += 0.06  # 6% boost for strong predictions
        elif prediction_strength > 0.1:
            confidence += 0.04  # 4% boost for moderate predictions
        
        # Add vector enhancement boost if available (smaller)
        try:
            from vector_enhanced_prediction import VectorEnhancedPredictionSystem
            vector_system = VectorEnhancedPredictionSystem()
            if vector_system.connect_to_database() and vector_system.load_embeddings():
                # Add small confidence boost for vector-enhanced predictions
                vector_boost = min(0.05, confidence * 0.1)  # Up to 5% boost
                confidence += vector_boost
        except:
            pass  # Continue without vector enhancement if not available
        
        # Load historical performance and calibrate confidence
        performance_data = load_model_performance()
        
        # Apply adaptive calibration based on historical accuracy
        if performance_data.get('total_predictions', 0) > 20:  # Need at least 20 predictions
            historical_accuracy = performance_data.get('correct_predictions', 0) / performance_data.get('total_predictions', 1)
            historical_avg_confidence = performance_data.get('avg_confidence', confidence)
            
            # Calculate calibration factor
            if historical_avg_confidence > 0:
                calibration_factor = historical_accuracy / historical_avg_confidence
                # Apply calibration with smoothing (don't overcorrect) from config
                smoothing = MODEL_CONFIG.get('calibration', {}).get('smoothing_factor', 0.7)
                calibration_factor = smoothing * calibration_factor + (1.0 - smoothing) * 1.0
                confidence = confidence * calibration_factor
        
        # Additional calibration using calibrate_confidence function
        calibrated_confidence = calibrate_confidence(confidence, performance_data)
        
        # Ensure confidence is within realistic bounds from config
        cal_config = MODEL_CONFIG.get('calibration', {})
        min_conf = cal_config.get('min_confidence', 0.45)  # Raised from 0.15 to 0.45
        max_conf = cal_config.get('max_confidence', 0.95)  # Raised from 0.80 to 0.95
        confidence = max(min_conf, min(max_conf, calibrated_confidence))
        
        # Add score predictions FIRST
        score_predictions = predict_game_scores(
            home_team, away_team, 
            prediction_data['home_context'], 
            prediction_data['away_context'], 
            h2h
        )
        
        # Determine winner based on predicted scores (not just probability)
        home_score = score_predictions.get('home_score', 110)
        away_score = score_predictions.get('away_score', 110)
        
        if home_score > away_score:
            predicted_winner = home_team
        else:
            predicted_winner = away_team
        
        # Calculate realistic win probabilities based on team strengths
        total_strength = home_strength + away_strength
        home_win_probability = home_strength / total_strength
        away_win_probability = away_strength / total_strength
        
        # Add gambling statistics
        gambling_stats = predict_gambling_statistics(score_predictions, home_team, away_team)
        
        # Add uncertainty quantification
        uncertainty = 1 - confidence
        confidence_interval = {
            'lower': max(0.1, confidence - uncertainty/2),
            'upper': min(0.95, confidence + uncertainty/2)
        }
        
        result = {
            'predicted_winner': predicted_winner,
            'confidence': confidence,
            'prediction_score': prediction_score,
            'home_strength': home_strength,
            'away_strength': away_strength,
            'home_win_probability': home_win_probability,
            'away_win_probability': away_win_probability,
            'home_confidence': home_confidence,
            'away_confidence': away_confidence,
            'head_to_head': h2h,
            'home_form': home_form,
            'away_form': away_form,
            'home_team': home_team,
            'away_team': away_team,
            'confidence_interval': confidence_interval,
            'data_quality_factors': {
                'home_data_quality': home_confidence,
                'away_data_quality': away_confidence,
                'h2h_games': h2h_games,
                'form_consistency': form_consistency
            },
            'score_predictions': score_predictions,
            'gambling_stats': gambling_stats
        }
        
        # Apply automatic calibration adjustments
        if CALIBRATION_AVAILABLE:
            try:
                result = apply_calibration(result)
            except Exception as e:
                logging.warning(f"Calibration failed: {e}")
        
        # Record prediction for future accuracy tracking
        record_prediction(result)
        
        return result
    except Exception as e:
        logging.error(f"Prediction failed: {e}")
        # Return a fallback prediction with low confidence
        return {
            'predicted_winner': home_team,  # Default to home team
            'confidence': 0.1,  # Very low confidence for fallback
            'prediction_score': 0.1,
            'home_strength': 0.6,
            'away_strength': 0.5,
            'home_confidence': 0.1,
            'away_confidence': 0.1,
            'head_to_head': {'team1_wins': 0, 'team2_wins': 0, 'total_games': 0},
            'home_form': {'wins': 0, 'losses': 0, 'win_percentage': 0.5},
            'away_form': {'wins': 0, 'losses': 0, 'win_percentage': 0.5},
            'home_team': home_team,
            'away_team': away_team,
            'confidence_interval': {'lower': 0.05, 'upper': 0.15},
            'data_quality_factors': {
                'home_data_quality': 0.1,
                'away_data_quality': 0.1,
                'h2h_games': 0,
                'form_consistency': 0.1
            },
            'score_predictions': {'home_score': 110, 'away_score': 108, 'total_points': 218},
            'gambling_stats': {}
        }

def get_last_match_result(team1, team2=None):
    """Get the most recent match result for one team or a matchup between two teams"""
    conn = connect_to_database()
    if not conn:
        return None
    
    try:
        if team2:
            # Matchup specific
            query = f'''
            SELECT "Date", "HomeTeamName", "VisitorTeamName", "HomeTeamScore", "VisitorPoints", "Venue"
            FROM "{DB_SCHEMA}"."Matches"
            WHERE (("HomeTeamName" = %s AND "VisitorTeamName" = %s)
               OR ("HomeTeamName" = %s AND "VisitorTeamName" = %s))
            ORDER BY "Date" DESC
            LIMIT 1
            '''
            params = [team1, team2, team2, team1]
        else:
            # Single team last game
            query = f'''
            SELECT "Date", "HomeTeamName", "VisitorTeamName", "HomeTeamScore", "VisitorPoints", "Venue"
            FROM "{DB_SCHEMA}"."Matches"
            WHERE ("HomeTeamName" = %s OR "VisitorTeamName" = %s)
            ORDER BY "Date" DESC
            LIMIT 1
            '''
            params = [team1, team1]
            
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if not df.empty:
            match = df.iloc[0].to_dict()
            # Determine winner
            if match['HomeTeamScore'] > match['VisitorPoints']:
                match['winner'] = match['HomeTeamName']
                match['loser'] = match['VisitorTeamName']
                match['margin'] = match['HomeTeamScore'] - match['VisitorPoints']
            else:
                match['winner'] = match['VisitorTeamName']
                match['loser'] = match['HomeTeamName']
                match['margin'] = match['VisitorPoints'] - match['HomeTeamScore']
            
            # Format date
            if hasattr(match['Date'], 'strftime'):
                match['Date'] = match['Date'].strftime('%Y-%m-%d')
            else:
                match['Date'] = str(match['Date'])
                
            return match
        return None
    except Exception as e:
        logging.error(f"Error fetching last match result: {e}")
        if conn:
            conn.close()
        return None

if __name__ == "__main__":
    # Test the prediction system
    teams = get_team_list()
    if teams:
        print(f"Available teams: {teams[:5]}...")
        
        if len(teams) >= 2:
            home_team = teams[0]
            away_team = teams[1]
            
            print(f"\nPredicting: {home_team} vs {away_team}")
            prediction = predict_game_outcome(home_team, away_team)
            
            print(f"Predicted winner: {prediction['predicted_winner']}")
            print(f"Confidence: {prediction['confidence']:.1%}")
            print(f"Home strength: {prediction['home_strength']:.3f}")
            print(f"Away strength: {prediction['away_strength']:.3f}")
    else:
        print("No teams found in database")
