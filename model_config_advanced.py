"""
Advanced Model Configuration for NBA Predictions

Enhanced configuration with extensive parameters for fine-tuning prediction accuracy.
Includes dynamic adjustments, situational factors, and detailed weight breakdowns.
"""

import json
import os
from datetime import datetime

# Default advanced configuration
DEFAULT_ADVANCED_CONFIG = {
    # Version tracking
    "version": "2.0",
    "last_updated": datetime.now().isoformat(),
    
    # ============================================
    # CORE STRENGTH CALCULATION WEIGHTS
    # ============================================
    "strength_weights": {
        # Team performance metrics (Total: 1.0)
        "win_percentage": 0.25,              # Overall W-L record
        "point_differential": 0.20,          # Avg point differential
        "offensive_efficiency": 0.15,        # Points per 100 possessions
        "defensive_efficiency": 0.15,        # Opponent points per 100 possessions
        "recent_form": 0.15,                 # Last N games performance
        "news_sentiment": 0.10,              # News sentiment analysis
    },
    
    # ============================================
    # HOME COURT ADVANTAGE
    # ============================================
    "home_advantage": {
        "base_advantage": 0.10,              # Base home court boost
        "venue_specific": {
            "altitude": 0.02,                # Denver, Utah (high altitude)
            "crowd_intensity": 0.01,         # Known loud arenas
            "travel_distance": 0.01,         # Coast-to-coast travel penalty
        },
        "time_of_season": {
            "early_season": 0.08,            # Oct-Nov (less advantage)
            "mid_season": 0.10,              # Dec-Feb (normal)
            "late_season": 0.12,             # Mar-Apr (more advantage)
            "playoffs": 0.15,                # Playoffs (maximum)
        },
        "back_to_back": {
            "home_b2b": -0.03,               # Home team on back-to-back
            "away_b2b": -0.05,               # Away team on back-to-back
        }
    },
    
    # ============================================
    # RECENT FORM ANALYSIS
    # ============================================
    "recent_form": {
        "windows": {
            "last_3_games": 0.40,            # Very recent (highest weight)
            "last_5_games": 0.30,            # Recent
            "last_10_games": 0.20,           # Medium term
            "last_15_games": 0.10,           # Longer term
        },
        "time_decay": {
            "enabled": True,
            "decay_rate": 0.95,              # Each day older = 95% weight
            "max_days": 30,                  # Don't look beyond 30 days
        },
        "streak_bonus": {
            "win_streak_3": 0.02,            # 3+ game win streak bonus
            "win_streak_5": 0.04,            # 5+ game win streak bonus
            "win_streak_10": 0.06,           # 10+ game win streak bonus
            "loss_streak_penalty": -0.02,    # Losing streak penalty
        }
    },
    
    # ============================================
    # HEAD-TO-HEAD FACTORS
    # ============================================
    "head_to_head": {
        "base_weight": 0.15,                 # H2H impact on prediction
        "recent_h2h": {
            "last_1_meeting": 0.50,          # Most recent meeting
            "last_3_meetings": 0.30,         # Recent meetings
            "last_5_meetings": 0.20,         # Longer history
        },
        "season_h2h": {
            "current_season": 0.60,          # This season H2H
            "last_season": 0.25,             # Last season H2H
            "two_seasons_ago": 0.15,         # Two seasons ago
        },
        "blowout_discount": {
            "enabled": True,
            "threshold": 20,                 # Margin > 20 points
            "discount_factor": 0.5,          # Weight blowouts 50% less
        }
    },
    
    # ============================================
    # REST & SCHEDULE FACTORS
    # ============================================
    "rest_schedule": {
        "rest_days_impact": {
            "0_days": -0.08,                 # Back-to-back (tired)
            "1_day": -0.03,                  # One day rest (slight fatigue)
            "2_days": 0.00,                  # Normal rest (baseline)
            "3_days": 0.02,                  # Extra rest (slight boost)
            "4_plus_days": 0.03,             # Extended rest (rested)
            "7_plus_days": -0.01,            # Too much rest (rust)
        },
        "travel_fatigue": {
            "short_distance": 0.00,          # <500 miles
            "medium_distance": -0.01,        # 500-1500 miles
            "long_distance": -0.02,          # 1500-2500 miles
            "coast_to_coast": -0.03,         # >2500 miles
            "time_zone_penalty": -0.01,      # Per time zone crossed
        },
        "schedule_difficulty": {
            "games_in_7_days": {
                "2_games": 0.00,             # Normal
                "3_games": -0.01,            # Busy
                "4_games": -0.03,            # Very busy
                "5_plus_games": -0.05,       # Exhausting
            },
            "road_trip": {
                "game_1": 0.00,              # First game (fresh)
                "game_2": -0.01,             # Second game
                "game_3": -0.02,             # Third game
                "game_4_plus": -0.04,        # Extended road trip
            }
        }
    },
    
    # ============================================
    # INJURY & ROSTER IMPACT
    # ============================================
    "injury_impact": {
        "star_player": {
            "mvp_candidate": -0.15,          # MVP-level player out
            "all_star": -0.10,               # All-star out
            "starter": -0.05,                # Regular starter out
            "key_rotation": -0.02,           # Important bench player
            "role_player": -0.01,            # Role player out
        },
        "multiple_injuries": {
            "2_starters": -0.12,             # Two starters out
            "3_starters": -0.18,             # Three starters out
            "4_plus_starters": -0.25,        # Four+ starters out
        },
        "injury_duration": {
            "questionable": -0.02,           # Game-time decision
            "out_1_game": -0.05,             # Confirmed out
            "week_to_week": -0.03,           # Return soon (less impact)
            "long_term": -0.08,              # Extended absence
        },
        "return_from_injury": {
            "first_game_back": -0.03,        # Rust factor
            "second_game_back": -0.01,       # Still adjusting
            "third_plus_game": 0.00,         # Back to normal
        }
    },
    
    # ============================================
    # NEWS SENTIMENT ANALYSIS
    # ============================================
    "news_sentiment": {
        "weight_by_recency": {
            "today": 1.00,                   # Today's news (full weight)
            "yesterday": 0.90,               # Yesterday
            "2_days_ago": 0.75,              # 2 days ago
            "3_days_ago": 0.60,              # 3 days ago
            "4_7_days_ago": 0.40,            # Last week
            "8_14_days_ago": 0.20,           # 1-2 weeks ago
            "15_plus_days": 0.10,            # Older news
        },
        "sentiment_multiplier": {
            "very_positive": 0.10,           # Championship talk, hot streak
            "positive": 0.05,                # Good vibes
            "neutral": 0.00,                 # No impact
            "negative": -0.05,               # Struggles, issues
            "very_negative": -0.10,          # Crisis, major problems
        },
        "topic_weights": {
            "injuries": 1.50,                # Injury news = most important
            "trades": 1.30,                  # Trade news
            "coaching": 1.20,                # Coaching changes
            "chemistry": 1.10,               # Team chemistry
            "general_performance": 1.00,     # Standard news
        },
        "source_reliability": {
            "official": 1.00,                # Team official sources
            "major_media": 0.90,             # ESPN, NBA.com
            "beat_writers": 0.80,            # Local beat writers
            "social_media": 0.50,            # Twitter/social
            "rumors": 0.30,                  # Unverified rumors
        }
    },
    
    # ============================================
    # OFFENSIVE & DEFENSIVE RATINGS
    # ============================================
    "offensive_metrics": {
        "pace_adjustment": {
            "enabled": True,
            "fast_pace_bonus": 0.02,         # Fast-paced teams
            "slow_pace_penalty": -0.01,      # Slow-paced teams
        },
        "scoring_metrics": {
            "points_per_game": 0.30,         # Raw scoring
            "true_shooting": 0.25,           # TS% efficiency
            "effective_fg": 0.20,            # eFG%
            "three_point_rate": 0.15,        # 3PA rate
            "free_throw_rate": 0.10,         # FTA rate
        },
        "ball_movement": {
            "assists_per_game": 0.40,        # Team assists
            "assist_to_turnover": 0.35,      # AST/TO ratio
            "turnovers_per_game": 0.25,      # Turnovers (negative)
        }
    },
    
    "defensive_metrics": {
        "opponent_scoring": {
            "opp_points_per_game": 0.35,     # Points allowed
            "opp_fg_percentage": 0.30,       # Opponent FG%
            "opp_three_point": 0.20,         # Opponent 3P%
            "opp_free_throws": 0.15,         # Opponent FT attempts
        },
        "defensive_activity": {
            "blocks_per_game": 0.25,         # Shot blocking
            "steals_per_game": 0.30,         # Steals/pressure
            "defensive_rebounds": 0.25,      # DREB%
            "fouls_per_game": 0.20,          # Foul rate (negative)
        }
    },
    
    # ============================================
    # SITUATIONAL ADJUSTMENTS
    # ============================================
    "situational_factors": {
        "time_of_season": {
            "october": 0.85,                 # Early season (less reliable)
            "november": 0.90,                # Still finding form
            "december": 0.95,                # Getting settled
            "january_february": 1.00,        # Full season mode
            "march": 1.05,                   # Playoff push
            "april": 1.10,                   # Critical games
        },
        "game_importance": {
            "regular_season": 1.00,          # Standard game
            "rivalry": 1.05,                 # Rivalry games
            "division": 1.08,                # Division games
            "conference": 1.03,              # Conference games
            "playoff_race": 1.15,            # Playoff implications
            "playoffs": 1.25,                # Playoff games
        },
        "special_circumstances": {
            "revenge_game": 0.02,            # Revenge factor
            "coach_return": 0.01,            # Coach vs old team
            "player_return": 0.02,           # Player vs old team
            "season_opener": -0.02,          # Season opener uncertainty
            "post_all_star": 0.00,           # Post all-star break
            "day_game": -0.01,               # Day games (unusual)
        }
    },
    
    # ============================================
    # CONFIDENCE CALCULATION
    # ============================================
    "confidence_factors": {
        "base_confidence": {
            "low_data_quality": {
                "base": 0.50,                # Starting confidence (low data)
                "data_availability": 0.20,   # Data quality boost
                "sample_size": 0.15,         # More games = more confidence
                "head_to_head": 0.10,        # H2H history
                "recency": 0.05,             # Recent data quality
            },
            "high_data_quality": {
                "base": 0.40,                # Starting confidence (good data)
                "model_agreement": 0.25,     # Multiple models agree
                "data_availability": 0.15,   # Data quality
                "sample_size": 0.10,         # Sample size
                "historical_accuracy": 0.10, # Model's past accuracy
            }
        },
        "prediction_strength": {
            "very_strong": {                 # >30% win probability gap
                "min_confidence": 0.75,
                "max_confidence": 0.95,
            },
            "strong": {                      # 20-30% gap
                "min_confidence": 0.65,
                "max_confidence": 0.85,
            },
            "moderate": {                    # 10-20% gap
                "min_confidence": 0.55,
                "max_confidence": 0.75,
            },
            "weak": {                        # <10% gap
                "min_confidence": 0.45,
                "max_confidence": 0.65,
            }
        },
        "uncertainty_factors": {
            "injury_uncertainty": -0.10,     # Key injuries unknown
            "new_roster": -0.08,             # Major roster changes
            "new_coach": -0.05,              # New coaching staff
            "long_layoff": -0.05,            # Extended break
            "playoff_pressure": -0.03,       # Playoff unpredictability
        }
    },
    
    # ============================================
    # SCORE PREDICTION
    # ============================================
    "score_prediction": {
        "base_scoring": {
            "league_average": 112.0,         # Current NBA average
            "std_deviation": 12.0,           # Typical variation
        },
        "pace_adjustment": {
            "enabled": True,
            "fast_pace_multiplier": 1.08,    # 8% more possessions
            "slow_pace_multiplier": 0.92,    # 8% fewer possessions
        },
        "home_court_points": 3.0,            # Average home court boost
        "matchup_adjustment": {
            "strong_offense_vs_weak_defense": 5.0,
            "strong_defense_vs_weak_offense": -5.0,
            "pace_mismatch": 3.0,            # Fast vs slow or vice versa
        },
        "variance": {
            "typical_game": 8.0,             # Normal variance
            "high_variance": 12.0,           # Blowout potential
            "low_variance": 5.0,             # Close game expected
        }
    },
    
    # ============================================
    # GAMBLING PREDICTIONS
    # ============================================
    "gambling_metrics": {
        "spread_confidence": {
            "high": 0.70,                    # >7 point spread
            "medium": 0.60,                  # 3-7 point spread
            "low": 0.50,                     # <3 point spread
        },
        "over_under_factors": {
            "pace_weight": 0.35,             # Pace impact on total
            "defense_weight": 0.30,          # Defense impact
            "recent_scoring": 0.20,          # Recent trends
            "weather_indoor": 0.00,          # NBA is always indoor
            "motivation": 0.15,              # Playoff race, etc.
        },
        "quarter_predictions": {
            "first_quarter": {
                "feeling_out": 0.90,         # Teams feeling each other
                "energy_high": 1.00,
            },
            "second_quarter": {
                "rotation_heavy": 0.95,      # Bench players
                "adjustment_period": 1.00,
            },
            "third_quarter": {
                "halftime_adjustments": 1.05, # Coaching impact
                "renewed_energy": 1.02,
            },
            "fourth_quarter": {
                "close_game_variance": 1.10, # High variance if close
                "blowout_discount": 0.80,    # Garbage time
                "clutch_factor": 1.05,       # Clutch players
            }
        }
    },
    
    # ============================================
    # CALIBRATION SETTINGS
    # ============================================
    "calibration": {
        "enabled": True,
        "smoothing_factor": 0.75,            # How much to smooth calibration
        "min_confidence": 0.45,              # Never go below this
        "max_confidence": 0.95,              # Never go above this
        "sample_size_threshold": 20,         # Min games for calibration
        "recalibration_frequency": "weekly", # How often to recalibrate
    },
    
    # ============================================
    # ADVANCED FEATURES
    # ============================================
    "advanced_features": {
        "momentum_tracking": {
            "enabled": True,
            "lookback_games": 5,
            "weight": 0.05,
        },
        "clutch_performance": {
            "enabled": True,
            "last_5_minutes": 0.10,          # Close game performance
            "overtime_record": 0.05,
        },
        "coaching_impact": {
            "enabled": True,
            "ato_plays": 0.03,               # After timeout plays
            "adjustment_rating": 0.04,       # In-game adjustments
        },
        "player_matchups": {
            "enabled": False,                # Requires player-level data
            "star_vs_star": 0.05,
            "mismatch_advantage": 0.03,
        }
    },
    
    # ============================================
    # MODEL ENSEMBLE WEIGHTS
    # ============================================
    "ensemble_weights": {
        "statistical_model": 0.35,           # Pure stats-based
        "form_based_model": 0.25,            # Recent form focus
        "matchup_model": 0.20,               # Head-to-head focus
        "sentiment_model": 0.10,             # News sentiment
        "hybrid_model": 0.10,                # Combined approach
    }
}

def load_config(config_file='model_config_advanced.json'):
    """Load configuration from file or use defaults"""
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                print(f"Loaded advanced configuration from {config_file}")
                return config
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return DEFAULT_ADVANCED_CONFIG
    else:
        print("No config file found. Using default advanced configuration.")
        return DEFAULT_ADVANCED_CONFIG

def save_config(config, config_file='model_config_advanced.json'):
    """Save configuration to file"""
    try:
        config['last_updated'] = datetime.now().isoformat()
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {config_file}")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_parameter(config, *keys, default=None):
    """Safely get nested configuration parameter"""
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value

def update_parameter(config, value, *keys):
    """Safely update nested configuration parameter"""
    if len(keys) == 0:
        return False
    
    target = config
    for key in keys[:-1]:
        if key not in target:
            target[key] = {}
        target = target[key]
    
    target[keys[-1]] = value
    return True

def validate_weights(weights_dict):
    """Validate that weights sum to approximately 1.0"""
    total = sum(weights_dict.values())
    if abs(total - 1.0) > 0.01:
        print(f"Warning: Weights sum to {total:.3f}, not 1.0")
        return False
    return True

def normalize_weights(weights_dict):
    """Normalize weights to sum to 1.0"""
    total = sum(weights_dict.values())
    if total == 0:
        return weights_dict
    return {k: v/total for k, v in weights_dict.items()}

def count_parameters(config, prefix=''):
    """Count total number of parameters in config"""
    count = 0
    for key, value in config.items():
        if isinstance(value, dict):
            count += count_parameters(value, f"{prefix}{key}.")
        else:
            count += 1
    return count

# Initialize and save default config if it doesn't exist
if __name__ == "__main__":
    config = load_config()
    
    # Validate key weight sections
    print("\nValidating weight configurations...")
    
    strength_weights = config['strength_weights']
    if validate_weights(strength_weights):
        print("[OK] Strength weights valid")
    
    ensemble_weights = config['ensemble_weights']
    if validate_weights(ensemble_weights):
        print("[OK] Ensemble weights valid")
    
    # Save config
    save_config(config)
    print("\nAdvanced configuration initialized!")
    print(f"Total parameters: {count_parameters(config)}")

