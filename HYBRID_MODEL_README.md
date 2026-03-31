# NBA Hybrid Model Architecture 🏀

A sophisticated ensemble prediction system that combines multiple modeling approaches for accurate NBA game predictions.

## 🏗️ Architecture Overview

The hybrid model integrates four specialized sub-models, each designed to capture different aspects of basketball prediction:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Time Series   │    │   Statistical   │    │   Sentiment     │
│     Model       │    │     Model       │    │     Model       │
│                 │    │                 │    │                 │
│ • ARIMA         │    │ • XGBoost       │    │ • TextBlob      │
│ • Trend Analysis│    │ • Random Forest │    │ • NLTK          │
│ • Seasonality   │    │ • Feature Eng.  │    │ • News Analysis │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   LLM Model     │
                    │                 │
                    │ • Ollama        │
                    │ • Llama2/Mistral│
                    │ • Narrative Gen.│
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Ensemble Layer │
                    │                 │
                    │ • Weighted Avg  │
                    │ • Confidence    │
                    │ • Final Output  │
                    └─────────────────┘
```

## 🧩 Sub-Model Details

### 1. Time Series Model (`TimeSeriesModel`)
- **Purpose**: Captures historical patterns and trends in game outcomes
- **Algorithm**: ARIMA (AutoRegressive Integrated Moving Average)
- **Features**: 
  - Historical score patterns
  - Rolling averages (5, 10, 20 game windows)
  - Seasonality detection
  - Stationarity testing
- **Output**: Trend-based score predictions

### 2. Statistical Model (`StatisticalModel`)
- **Purpose**: Analyzes player and team performance metrics
- **Algorithms**: XGBoost, Random Forest, Gradient Boosting
- **Features**:
  - Player statistics (points, assists, rebounds, etc.)
  - Team performance metrics
  - Advanced statistics (efficiency, usage rate)
  - Historical head-to-head data
- **Output**: Performance-based predictions

### 3. Sentiment Model (`SentimentModel`)
- **Purpose**: Analyzes news sentiment and contextual factors
- **Tools**: TextBlob, NLTK
- **Features**:
  - News article sentiment analysis
  - Injury reports impact
  - Team morale indicators
  - Media coverage sentiment
- **Output**: Sentiment scores (-1 to 1)

### 4. LLM Model (`LLMModel`)
- **Purpose**: Provides AI-powered reasoning and narrative context
- **Backend**: Ollama with Llama2/Mistral models
- **Capabilities**:
  - Injury impact analysis
  - Game narrative generation
  - Strategic insights
  - Contextual reasoning
- **Output**: Textual analysis and explanations

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Ollama Service
```bash
# Install Ollama if not already installed
# Download from https://ollama.com/

# Pull required models
ollama pull llama2
ollama pull bge-m3  # For embeddings
```

### 3. Run Training Script
```bash
python train_hybrid_model.py
```

### 4. Launch Streamlit Interface
```bash
streamlit run streamlit_hybrid_predict.py
```

## 📊 Usage Examples

### Basic Model Training
```python
from hybrid_model import HybridModel

# Initialize model
model = HybridModel(weights={
    'time_series': 0.3,
    'statistical': 0.4,
    'sentiment': 0.2,
    'llm': 0.1
})

# Train with data
model.fit(matches_data, players_data, teams_data, news_data)

# Make prediction
prediction = model.predict_game('Lakers', 'Warriors', context_data)
print(f"Predicted winner: {prediction['predicted_winner']}")
```

### Custom Weight Configuration
```python
# Adjust model weights based on performance
model.update_weights({
    'time_series': 0.25,
    'statistical': 0.45,
    'sentiment': 0.20,
    'llm': 0.10
})
```

### Individual Model Access
```python
# Access individual sub-models
ts_pred = model.time_series_model.predict(steps=1)
stat_pred = model.statistical_model.predict(player_stats)
sentiment = model.sentiment_model.get_sentiment_score('news_id')
llm_analysis = model.llm_model.analyze_injury_impact('Player', 'Injury', 'Stats')
```

## ⚙️ Configuration

### Model Weights
Default ensemble weights can be adjusted in `hybrid_model_config.py`:

```python
ENSEMBLE_CONFIG = {
    'default_weights': {
        'time_series': 0.30,
        'statistical': 0.40,
        'sentiment': 0.20,
        'llm': 0.10
    }
}
```

### Statistical Model Parameters
```python
STATISTICAL_CONFIG = {
    'models': {
        'xgboost': {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 6
        }
    }
}
```

### LLM Configuration
```python
OLLAMA_CONFIG = {
    'base_url': 'http://localhost:11434',
    'default_model': 'llama2',
    'timeout': 30
}
```

## 🔧 Integration with Existing System

### Database Integration
The model automatically connects to your existing PostgreSQL database:

```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749',
    'schema': 'NBA'
}
```

### Streamlit Integration
Replace or enhance your existing `Predict.py` page:

```python
# In your existing Predict.py
from streamlit_hybrid_predict import create_prediction_interface

# Add hybrid predictions to your page
st.header("Hybrid Model Predictions")
create_prediction_interface()
```

### API Integration
Use the model as a service:

```python
from hybrid_model import HybridModel

class PredictionService:
    def __init__(self):
        self.model = HybridModel()
        self.model.fit(...)
    
    def predict_game(self, home_team, away_team, context):
        return self.model.predict_game(home_team, away_team, context)
```

## 📈 Performance Monitoring

### Model Evaluation
```python
# Evaluate model performance
scores = model.evaluate(test_data)

# Get feature importance
importance = model.get_feature_importance()
```

### Confidence Scoring
The model provides confidence levels for predictions:
- **High Confidence**: Ensemble score > 0.7
- **Medium Confidence**: Ensemble score 0.4-0.7
- **Low Confidence**: Ensemble score < 0.4

## 🛠️ Advanced Features

### Adaptive Weighting
Weights automatically adjust based on recent performance:

```python
# Enable adaptive weighting
ENSEMBLE_CONFIG['adaptive_weights'] = True
ENSEMBLE_CONFIG['weight_update_frequency'] = 10
```

### Feature Engineering
Automatic feature creation and selection:

```python
FEATURE_CONFIG = {
    'player_features': {
        'derived_features': ['points_per_game', 'assists_per_game'],
        'rolling_features': ['rolling_5_avg', 'rolling_10_avg']
    }
}
```

### Model Persistence
Save and load trained models:

```python
# Save model
model.save('./models/hybrid_model.pkl')

# Load model
model = HybridModel.load('./models/hybrid_model.pkl')
```

## 🔍 Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Ensure Ollama service is running
   - Check if models are downloaded
   - Verify port 11434 is accessible

2. **Model Training Fails**
   - Check data quality and completeness
   - Verify all required columns are present
   - Ensure sufficient data for time series analysis

3. **Memory Issues**
   - Reduce batch sizes in configuration
   - Use smaller rolling windows
   - Enable data streaming for large datasets

### Debug Mode
Enable detailed logging:

```python
LOGGING_CONFIG = {
    'log_level': 'DEBUG',
    'performance_tracking': True
}
```

## 📚 API Reference

### HybridModel Class
- `__init__(weights=None)`: Initialize with custom weights
- `fit(matches_data, players_data, teams_data, news_data)`: Train all sub-models
- `predict_game(home_team, away_team, context_data)`: Make game prediction
- `update_weights(new_weights)`: Update ensemble weights
- `get_feature_importance()`: Get feature importance scores

### Sub-Model Classes
- `TimeSeriesModel`: ARIMA-based time series analysis
- `StatisticalModel`: ML-based statistical modeling
- `SentimentModel`: Text sentiment analysis
- `LLMModel`: Ollama-powered LLM integration

## 🤝 Contributing

### Adding New Models
1. Create new model class inheriting from base
2. Implement required methods (`fit`, `predict`)
3. Add to ensemble configuration
4. Update weight calculations

### Extending Features
1. Modify configuration files
2. Add new preprocessing steps
3. Implement additional evaluation metrics
4. Create new visualization components

## 📄 License

This hybrid model architecture is part of the NBA Predict project and follows the same licensing terms.

## 🙏 Acknowledgments

- **pgvector**: PostgreSQL vector operations
- **Ollama**: Local AI model hosting
- **scikit-learn**: Machine learning algorithms
- **statsmodels**: Time series analysis
- **TextBlob/NLTK**: Natural language processing

---

**Note**: This hybrid model requires proper setup of PostgreSQL with pgvector extension and Ollama for LLM capabilities. Follow the installation guide carefully for optimal performance.
