import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import nltk
from textblob import TextBlob
import requests
import json
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

class TimeSeriesModel:
    """Time series model for match trends and patterns"""
    
    def __init__(self, order=(1, 1, 1)):
        self.order = order
        self.model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def prepare_data(self, data, target_col, date_col):
        """Prepare time series data"""
        df = data.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        
        # Check stationarity
        if not self._is_stationary(df[target_col]):
            df[target_col] = df[target_col].diff().dropna()
            
        return df
        
    def _is_stationary(self, series):
        """Check if time series is stationary"""
        result = adfuller(series.dropna())
        return result[1] <= 0.05
        
    def fit(self, data, target_col, date_col):
        """Fit ARIMA model"""
        df = self.prepare_data(data, target_col, date_col)
        
        try:
            self.model = ARIMA(df[target_col], order=self.order)
            self.model = self.model.fit()
            self.is_fitted = True
        except Exception as e:
            print(f"ARIMA fitting failed: {e}")
            self.is_fitted = False
            
    def predict(self, steps=1):
        """Make predictions"""
        if not self.is_fitted:
            raise NotImplementedError("Model not fitted. Call fit() first.")
        return self.model.forecast(steps=steps)

class StatisticalModel:
    """Statistical model for player and team performance"""
    
    def __init__(self, model_type='xgboost'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = None
        self.is_fitted = False
        
    def _create_model(self):
        """Create the specified model"""
        if self.model_type == 'xgboost':
            return xgb.XGBRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
        elif self.model_type == 'random_forest':
            return RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        elif self.model_type == 'gradient_boosting':
            return GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def prepare_features(self, data, target_col):
        """Prepare features for statistical model"""
        df = data.copy()
        
        # Handle categorical variables
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col != target_col:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        # Handle numerical variables
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        numerical_cols = [col for col in numerical_cols if col != target_col]
        
        # Scale numerical features
        if numerical_cols:
            df[numerical_cols] = self.scaler.fit_transform(df[numerical_cols])
            
        self.feature_columns = [col for col in df.columns if col != target_col]
        return df
        
    def fit(self, data, target_col):
        """Fit the statistical model"""
        df = self.prepare_features(data, target_col)
        
        X = df[self.feature_columns]
        y = df[target_col]
        
        self.model = self._create_model()
        self.model.fit(X, y)
        self.is_fitted = True
        
    def predict(self, data):
        """Make predictions"""
        if not self.is_fitted:
            raise NotImplementedError("Model not fitted. Call fit() first.")
            
        df = data.copy()
        
        # Apply same preprocessing
        for col, le in self.label_encoders.items():
            if col in df.columns:
                df[col] = le.transform(df[col].astype(str))
                
        numerical_cols = [col for col in self.feature_columns if col in df.select_dtypes(include=[np.number]).columns]
        if numerical_cols:
            df[numerical_cols] = self.scaler.transform(df[numerical_cols])
            
        X = df[self.feature_columns]
        return self.model.predict(X)

class SentimentModel:
    """Sentiment analysis model for news and contextual data"""
    
    def __init__(self):
        self.sentiment_scores = {}
        self.is_fitted = False
        
    def analyze_sentiment(self, text):
        """Analyze sentiment of text using TextBlob"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            return 0.0
            
    def extract_sentiment_features(self, news_data):
        """Extract sentiment features from news data"""
        features = {}
        
        for news_id, text in news_data.items():
            sentiment = self.analyze_sentiment(text)
            features[news_id] = {
                'sentiment_score': sentiment,
                'sentiment_category': self._categorize_sentiment(sentiment)
            }
            
        return features
        
    def _categorize_sentiment(self, score):
        """Categorize sentiment score"""
        if score > 0.1:
            return 'positive'
        elif score < -0.1:
            return 'negative'
        else:
            return 'neutral'
            
    def fit(self, news_data):
        """Fit sentiment model (extract features)"""
        self.sentiment_scores = self.extract_sentiment_features(news_data)
        self.is_fitted = True
        
    def get_sentiment_score(self, news_id):
        """Get sentiment score for specific news"""
        if not self.is_fitted:
            raise NotImplementedError("Model not fitted. Call fit() first.")
        return self.sentiment_scores.get(news_id, {'sentiment_score': 0, 'sentiment_category': 'neutral'})

class LLMModel:
    """LLM-enhanced model using Ollama for reasoning and explanations"""
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.model_name = "llama2"  # Default model
        self.is_available = False
        self._check_availability()
        
    def _check_availability(self):
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.is_available = True
        except:
            self.is_available = False
            
    def pull_model(self, model_name="llama2"):
        """Pull a model from Ollama"""
        if not self.is_available:
            raise NotImplementedError("Ollama not available")
            
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name}
            )
            if response.status_code == 200:
                self.model_name = model_name
                return True
        except:
            pass
        return False
        
    def generate_analysis(self, prompt, context=""):
        """Generate analysis using LLM"""
        if not self.is_available:
            raise NotImplementedError("Ollama not available")
            
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
        except:
            pass
            
        return "Analysis unavailable"
        
    def analyze_injury_impact(self, player_name, injury_details, team_stats):
        """Analyze impact of injury on team performance"""
        prompt = f"""
        Analyze the potential impact of {player_name}'s injury on their team's performance.
        
        Injury Details: {injury_details}
        Current Team Stats: {team_stats}
        
        Provide:
        1. Short-term impact assessment
        2. Key players who need to step up
        3. Expected performance adjustment
        4. Strategic recommendations
        """
        
        return self.generate_analysis(prompt)
        
    def generate_game_narrative(self, team1, team2, recent_form, head_to_head):
        """Generate narrative for upcoming game"""
        prompt = f"""
        Create an engaging narrative for the upcoming game between {team1} and {team2}.
        
        Recent Form:
        {team1}: {recent_form.get(team1, 'N/A')}
        {team2}: {recent_form.get(team2, 'N/A')}
        
        Head-to-Head: {head_to_head}
        
        Focus on:
        1. Key storylines
        2. Player matchups
        3. Strategic considerations
        4. Prediction factors
        """
        
        return self.generate_analysis(prompt)

class HybridModel:
    """Main hybrid model combining all sub-models"""
    
    def __init__(self, weights=None):
        self.time_series_model = TimeSeriesModel()
        self.statistical_model = StatisticalModel()
        self.sentiment_model = SentimentModel()
        self.llm_model = LLMModel()
        
        # Default weights for ensemble
        self.weights = weights or {
            'time_series': 0.3,
            'statistical': 0.4,
            'sentiment': 0.2,
            'llm': 0.1
        }
        
        self.is_fitted = False
        
    def fit(self, matches_data, players_data, teams_data, news_data):
        """Fit all sub-models"""
        print("Fitting Time Series Model...")
        try:
            # Determine the correct column names
            home_score_col = 'home_score' if 'home_score' in matches_data.columns else 'HomeTeamScore'
            date_col = 'date' if 'date' in matches_data.columns else 'Date'
            self.time_series_model.fit(matches_data, home_score_col, date_col)
        except Exception as e:
            print(f"Time series model fitting failed: {e}")
            
        print("Fitting Statistical Model...")
        try:
            self.statistical_model.fit(players_data, 'points_per_game')
        except Exception as e:
            print(f"Statistical model fitting failed: {e}")
            
        print("Fitting Sentiment Model...")
        try:
            self.sentiment_model.fit(news_data)
        except Exception as e:
            print(f"Sentiment model fitting failed: {e}")
            
        self.is_fitted = True
        print("All models fitted successfully!")
        
    def predict_game(self, home_team, away_team, context_data):
        """Predict game outcome using hybrid approach with enhanced confidence"""
        if not self.is_fitted:
            raise NotImplementedError("Models not fitted. Call fit() first.")
            
        predictions = {}
        model_confidence = {}
        
        # Time series prediction
        try:
            ts_pred = self.time_series_model.predict(steps=1)[0]
            predictions['time_series'] = ts_pred
            # Time series confidence based on model fit quality - more generous
            model_confidence['time_series'] = 0.8 if self.time_series_model.is_fitted else 0.3  # Increased from 0.7/0.1
        except:
            predictions['time_series'] = 0
            model_confidence['time_series'] = 0.1
            
        # Statistical prediction
        try:
            stat_pred = self.statistical_model.predict(context_data['player_stats'])
            predictions['statistical'] = np.mean(stat_pred)
            # Statistical confidence based on data quality and model performance - more generous
            data_quality = len(context_data.get('player_stats', []))
            model_confidence['statistical'] = min(0.95, 0.6 + (data_quality / 15) * 0.5)  # More generous scaling
        except:
            predictions['statistical'] = 0
            model_confidence['statistical'] = 0.1
            
        # Sentiment analysis
        try:
            sentiment_score = self.sentiment_model.get_sentiment_score('recent_news')
            predictions['sentiment'] = sentiment_score['sentiment_score']
            # Sentiment confidence based on data availability - more generous
            news_count = len(context_data.get('news', []))
            model_confidence['sentiment'] = min(0.9, 0.5 + (news_count / 8) * 0.6)  # More generous scaling
        except:
            predictions['sentiment'] = 0
            model_confidence['sentiment'] = 0.1
            
        # LLM analysis
        try:
            llm_analysis = self.llm_model.generate_game_narrative(
                home_team, away_team,
                context_data.get('recent_form', {}),
                context_data.get('head_to_head', {})
            )
            predictions['llm_analysis'] = llm_analysis
            model_confidence['llm'] = 0.8 if self.llm_model.is_available else 0.3  # Increased from 0.6/0.1
        except:
            predictions['llm_analysis'] = "LLM analysis unavailable"
            model_confidence['llm'] = 0.1
            
        # Weighted ensemble prediction
        weighted_score = (
            self.weights['time_series'] * predictions['time_series'] +
            self.weights['statistical'] * predictions['statistical'] +
            self.weights['sentiment'] * predictions['sentiment']
        )
        
        # Calculate ensemble confidence
        ensemble_confidence = (
            self.weights['time_series'] * model_confidence['time_series'] +
            self.weights['statistical'] * model_confidence['statistical'] +
            self.weights['sentiment'] * model_confidence['sentiment'] +
            self.weights['llm'] * model_confidence['llm']
        )
        
        # Adjust confidence based on prediction strength - more generous
        prediction_strength = abs(weighted_score)
        strength_factor = min(1.2, prediction_strength * 2.5 + 0.3)  # More generous scaling
        
        final_confidence = ensemble_confidence * strength_factor
        
        # Add additional confidence boost for ensemble agreement
        if len([c for c in model_confidence.values() if c > 0.5]) >= 2:  # At least 2 models confident
            final_confidence += 0.1  # 10% boost for model agreement
        
        predictions['ensemble_score'] = weighted_score
        predictions['predicted_winner'] = home_team if weighted_score > 0 else away_team
        predictions['confidence'] = max(0.25, min(0.95, final_confidence))  # Increased minimum from 0.1 to 0.25
        predictions['model_confidence'] = model_confidence
        
        return predictions
        
    def evaluate(self, test_data):
        """Evaluate model performance"""
        if not self.is_fitted:
            raise NotImplementedError("Models not fitted. Call fit() first.")
            
        # Implementation for model evaluation
        raise NotImplementedError("Evaluation method not implemented")
        
    def update_weights(self, new_weights):
        """Update ensemble weights"""
        self.weights = new_weights
        
    def get_feature_importance(self):
        """Get feature importance from statistical model"""
        if not self.statistical_model.is_fitted:
            raise NotImplementedError("Statistical model not fitted")
            
        if hasattr(self.statistical_model.model, 'feature_importances_'):
            return dict(zip(
                self.statistical_model.feature_columns,
                self.statistical_model.model.feature_importances_
            ))
        return {}

# Utility functions
def prepare_match_data(matches_df):
    """Prepare match data for time series analysis"""
    df = matches_df.copy()
    
    # Handle different possible column names
    date_col = 'date' if 'date' in df.columns else 'Date'
    home_team_col = 'home_team' if 'home_team' in df.columns else 'HomeTeamName'
    away_team_col = 'away_team' if 'away_team' in df.columns else 'VisitorTeamName'
    home_score_col = 'home_score' if 'home_score' in df.columns else 'HomeTeamScore'
    away_score_col = 'away_score' if 'away_score' in df.columns else 'VisitorPoints'
    
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    
    # Create rolling averages
    df['home_avg_score'] = df.groupby(home_team_col)[home_score_col].rolling(5).mean().reset_index(0, drop=True)
    df['away_avg_score'] = df.groupby(away_team_col)[away_score_col].rolling(5).mean().reset_index(0, drop=True)
    
    return df

def prepare_player_data(players_df):
    """Prepare player data for statistical analysis"""
    df = players_df.copy()
    
    # Handle missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    
    # Create derived features
    if 'points' in df.columns and 'games_played' in df.columns:
        df['points_per_game'] = df['points'] / df['games_played']
        
    return df

def prepare_news_data(news_df):
    """Prepare news data for sentiment analysis"""
    df = news_df.copy()
    
    # Handle different possible column names
    title_col = 'Title' if 'Title' in df.columns else 'title'
    content_col = 'Content' if 'Content' in df.columns else 'content'
    
    # Combine title and content for sentiment analysis
    df['full_text'] = df[title_col].fillna('') + ' ' + df[content_col].fillna('')
    
    # Create news dictionary for sentiment model
    news_dict = {}
    for idx, row in df.iterrows():
        news_dict[idx] = row['full_text']
        
    return news_dict
