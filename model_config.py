"""
Model Configuration for NBA Prediction Model
Stores tunable hyperparameters that can be optimized
"""

import json
import os
from datetime import datetime

CONFIG_FILE = 'model_config.json'

# Default configuration
DEFAULT_CONFIG = {
    'version': '1.0',
    'last_updated': None,
    'optimization_history': [],
    
    # Home advantage
    'home_advantage': 0.1,  # 10% boost for home team
    
    # Team strength calculation weights (should sum to 1.0)
    'strength_weights': {
        'win_percentage': 0.30,
        'point_differential': 0.25,
        'offensive_efficiency': 0.15,
        'defensive_efficiency': 0.10,
        'recent_form': 0.10,
        'news_sentiment': 0.10
    },
    
    # Confidence calculation weights
    'confidence_weights': {
        'low_data_quality': {
            'base_confidence': 0.7,
            'data_quality': 0.15,
            'head_to_head': 0.08,
            'form_consistency': 0.07
        },
        'high_data_quality': {
            'base_confidence': 0.6,
            'data_quality': 0.20,
            'head_to_head': 0.12,
            'form_consistency': 0.08
        }
    },
    
    # News time-weighting factors
    'news_time_weights': {
        '1_day': 1.0,
        '7_days': 0.8,
        '30_days': 0.6,
        'older': 0.3
    },
    
    # News recency impact parameters
    'news_recency': {
        'decay_days': 30,  # Days for recency to decay
        'volume_factor_divisor': 10  # recent_news_count / this
    },
    
    # Score prediction parameters
    'score_prediction': {
        'base_score_home': 110,
        'base_score_away': 110,
        'strength_multiplier': 20,  # (strength - 0.5) * this
        'home_court_points': 3,
        'first_half_factor': 0.47,
        'third_quarter_factor': 0.26
    },
    
    # Calibration parameters
    'calibration': {
        'smoothing_factor': 0.5,  # 0.5 * calibration + 0.5 * 1.0
        'min_confidence': 0.45,
        'max_confidence': 0.95
    }
}

def load_config():
    """Load configuration from file or create default"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file with complete parameter validation"""
    # Ensure we have a complete configuration
    complete_config = DEFAULT_CONFIG.copy()
    
    # Deep merge the provided config into defaults
    def deep_merge(base, update):
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                deep_merge(base[key], value)
            else:
                base[key] = value
    
    deep_merge(complete_config, config)
    
    # Normalize strength_weights to ensure they sum to 1.0
    if 'strength_weights' in complete_config:
        weights = complete_config['strength_weights']
        total = sum(weights.values())
        if total > 0:
            for key in weights:
                weights[key] = weights[key] / total
    
    complete_config['last_updated'] = datetime.now().isoformat()
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(complete_config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def update_config(updates):
    """Update configuration with new values"""
    config = load_config()
    
    # Deep update
    def deep_update(base, updates):
        for key, value in updates.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                deep_update(base[key], value)
            else:
                base[key] = value
    
    deep_update(config, updates)
    save_config(config)
    return config

def add_optimization_result(accuracy, confidence, avg_score_error, config_used):
    """Add an optimization result to history"""
    config = load_config()
    
    if 'optimization_history' not in config:
        config['optimization_history'] = []
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'accuracy': accuracy,
        'confidence': confidence,
        'avg_score_error': avg_score_error,
        'config': config_used
    }
    
    config['optimization_history'].append(result)
    
    # Keep only last 50 results
    if len(config['optimization_history']) > 50:
        config['optimization_history'] = config['optimization_history'][-50:]
    
    save_config(config)
    return result

def get_best_config():
    """Get the configuration with best historical accuracy"""
    config = load_config()
    history = config.get('optimization_history', [])
    
    if not history:
        return None
    
    # Find config with best accuracy
    best = max(history, key=lambda x: x.get('accuracy', 0))
    return best['config']

def reset_config():
    """Reset configuration to defaults"""
    save_config(DEFAULT_CONFIG.copy())
    return DEFAULT_CONFIG.copy()

if __name__ == '__main__':
    # Initialize with default config
    config = load_config()
    save_config(config)
    print("Model configuration initialized")
    print(json.dumps(config, indent=2))


