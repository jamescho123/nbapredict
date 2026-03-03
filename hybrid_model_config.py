"""
Configuration file for NBA Hybrid Model Architecture
Contains all parameters, model configurations, and settings
"""

# Database Configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749',
    'schema': 'NBA'
}

# Ollama Configuration
OLLAMA_CONFIG = {
    'base_url': 'http://localhost:11434',
    'default_model': 'llama2',
    'timeout': 30,
    'max_retries': 3
}

# Time Series Model Configuration
TIMESERIES_CONFIG = {
    'arima_order': (1, 1, 1),
    'seasonal_order': (1, 1, 1, 12),  # For seasonal patterns
    'rolling_window': 5,  # Rolling average window
    'min_periods': 10,    # Minimum periods for analysis
    'stationarity_threshold': 0.05  # ADF test p-value threshold
}

# Statistical Model Configuration
STATISTICAL_CONFIG = {
    'default_model': 'xgboost',
    'models': {
        'xgboost': {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 6,
            'random_state': 42,
            'subsample': 0.8,
            'colsample_bytree': 0.8
        },
        'random_forest': {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42
        },
        'gradient_boosting': {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 6,
            'subsample': 0.8,
            'random_state': 42
        }
    },
    'cross_validation_folds': 5,
    'test_size': 0.2,
    'random_state': 42
}

# Sentiment Model Configuration
SENTIMENT_CONFIG = {
    'textblob_thresholds': {
        'positive': 0.1,
        'negative': -0.1,
        'neutral_lower': -0.1,
        'neutral_upper': 0.1
    },
    'nltk_features': {
        'use_vader': True,
        'use_textblob': True,
        'use_custom_lexicon': False
    },
    'text_preprocessing': {
        'remove_stopwords': True,
        'lemmatize': True,
        'min_text_length': 10
    }
}

# LLM Model Configuration
LLM_CONFIG = {
    'prompts': {
        'injury_analysis': """
        Analyze the potential impact of {player_name}'s injury on their team's performance.
        
        Injury Details: {injury_details}
        Current Team Stats: {team_stats}
        
        Provide:
        1. Short-term impact assessment
        2. Key players who need to step up
        3. Expected performance adjustment
        4. Strategic recommendations
        """,
        
        'game_narrative': """
        Create an engaging narrative for the upcoming game between {team1} and {team2}.
        
        Recent Form:
        {team1}: {recent_form_team1}
        {team2}: {recent_form_team2}
        
        Head-to-Head: {head_to_head}
        
        Focus on:
        1. Key storylines
        2. Player matchups
        3. Strategic considerations
        4. Prediction factors
        """,
        
        'team_analysis': """
        Provide a comprehensive analysis of {team_name} based on the following data:
        
        Team Stats: {team_stats}
        Player Performance: {player_performance}
        Recent Results: {recent_results}
        
        Include:
        1. Strengths and weaknesses
        2. Key players to watch
        3. Recent trends
        4. Future outlook
        """
    },
    'max_tokens': 500,
    'temperature': 0.7,
    'top_p': 0.9
}

# Hybrid Model Ensemble Configuration
ENSEMBLE_CONFIG = {
    'default_weights': {
        'time_series': 0.30,
        'statistical': 0.40,
        'sentiment': 0.20,
        'llm': 0.10
    },
    'adaptive_weights': True,
    'weight_update_frequency': 10,  # Update weights every N predictions
    'performance_threshold': 0.6,   # Minimum performance to consider model
    'ensemble_methods': ['weighted_average', 'stacking', 'voting']
}

# Feature Engineering Configuration
FEATURE_CONFIG = {
    'player_features': {
        'basic_stats': ['points', 'assists', 'rebounds', 'steals', 'blocks'],
        'advanced_stats': ['efficiency', 'usage_rate', 'plus_minus'],
        'derived_features': ['points_per_game', 'assists_per_game', 'rebounds_per_game'],
        'rolling_features': ['rolling_5_avg', 'rolling_10_avg', 'rolling_20_avg']
    },
    'team_features': {
        'basic_stats': ['wins', 'losses', 'points_for', 'points_against'],
        'derived_features': ['win_percentage', 'point_differential', 'pace'],
        'trend_features': ['recent_form', 'home_away_split', 'streak']
    },
    'match_features': {
        'basic_stats': ['home_score', 'away_score', 'total_score', 'margin'],
        'context_features': ['home_advantage', 'rest_days', 'travel_distance'],
        'historical_features': ['head_to_head', 'recent_meetings', 'venue_performance']
    }
}

# Data Preprocessing Configuration
PREPROCESSING_CONFIG = {
    'missing_value_strategy': 'mean',  # 'mean', 'median', 'drop', 'interpolate'
    'outlier_detection': True,
    'outlier_threshold': 3.0,  # Standard deviations
    'scaling_method': 'standard',  # 'standard', 'minmax', 'robust'
    'categorical_encoding': 'label',  # 'label', 'onehot', 'target'
    'feature_selection': True,
    'correlation_threshold': 0.95
}

# Model Evaluation Configuration
EVALUATION_CONFIG = {
    'metrics': ['mse', 'mae', 'r2', 'accuracy', 'precision', 'recall', 'f1'],
    'cross_validation': True,
    'cv_folds': 5,
    'stratified': True,
    'scoring': 'neg_mean_squared_error',
    'test_size': 0.2,
    'validation_split': 0.2
}

# Prediction Configuration
PREDICTION_CONFIG = {
    'confidence_threshold': 0.7,
    'ensemble_size': 3,
    'prediction_horizon': 1,  # Number of games ahead to predict
    'update_frequency': 'daily',  # How often to retrain models
    'feature_importance_threshold': 0.01
}

# Logging and Monitoring Configuration
LOGGING_CONFIG = {
    'log_level': 'INFO',
    'log_file': 'hybrid_model.log',
    'performance_tracking': True,
    'model_versioning': True,
    'experiment_tracking': True
}

# Performance Optimization Configuration
OPTIMIZATION_CONFIG = {
    'parallel_processing': True,
    'batch_size': 1000,
    'memory_limit': '4GB',
    'cache_predictions': True,
    'model_persistence': True,
    'persistence_path': './models/'
}

# Error Handling Configuration
ERROR_CONFIG = {
    'max_retries': 3,
    'retry_delay': 1,  # seconds
    'fallback_strategy': 'ensemble',  # 'ensemble', 'best_model', 'average'
    'graceful_degradation': True,
    'error_logging': True
}

# Model Validation Configuration
VALIDATION_CONFIG = {
    'data_quality_checks': True,
    'model_drift_detection': True,
    'drift_threshold': 0.1,
    'retraining_trigger': 'performance_drop',  # 'performance_drop', 'time_based', 'data_drift'
    'validation_frequency': 'weekly'
}
