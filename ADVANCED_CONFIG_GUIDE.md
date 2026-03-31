# Advanced Model Configuration Guide

## Overview

The advanced configuration system provides 200+ tunable parameters to fine-tune NBA prediction accuracy. This replaces the basic 20-parameter configuration with extensive control over every aspect of the prediction model.

## Files

- **`model_config_advanced.py`**: Advanced configuration with 207 parameters
- **`enhanced_prediction.py`**: Enhanced prediction engine using advanced config
- **`model_config_advanced.json`**: Saved configuration file (auto-generated)

## Key Features

### 1. Core Strength Calculation (6 weighted components)
```python
'strength_weights': {
    'win_percentage': 0.25,
    'point_differential': 0.20,
    'offensive_efficiency': 0.15,
    'defensive_efficiency': 0.15,
    'recent_form': 0.15,
    'news_sentiment': 0.10
}
```

### 2. Home Court Advantage (Dynamic)
- **Base advantage**: 10%
- **Altitude adjustment**: +2% (Denver, Utah)
- **Time of season**: 
  - Early (Oct-Nov): 8%
  - Mid (Dec-Feb): 10%
  - Late (Mar-Apr): 12%
  - Playoffs: 15%
- **Back-to-back penalty**: -3% to -5%

### 3. Recent Form Analysis
- **Multiple windows**: Last 3, 5, 10, 15 games
- **Time decay**: Each day older = 95% weight
- **Streak bonuses**:
  - 3+ wins: +2%
  - 5+ wins: +4%
  - 10+ wins: +6%

### 4. Head-to-Head Factors
- **Base weight**: 15%
- **Recent meetings prioritized**: Last 1 (50%), Last 3 (30%), Last 5 (20%)
- **Blowout discount**: Games >20 points weighted 50% less

### 5. Rest & Schedule Impact
- **Rest days**:
  - 0 days (B2B): -8%
  - 1 day: -3%
  - 2 days: baseline
  - 3+ days: +2-3%
  - 7+ days (rust): -1%
- **Travel distance**:
  - Short (<500mi): 0%
  - Medium (500-1500mi): -1%
  - Long (1500-2500mi): -2%
  - Coast-to-coast (>2500mi): -3%
  - Time zone penalty: -1% per zone

### 6. Injury & Roster Impact
- **Star player levels**:
  - MVP candidate: -15%
  - All-star: -10%
  - Starter: -5%
  - Key rotation: -2%
  - Role player: -1%
- **Multiple injuries**: Compounding penalties
- **Return from injury**: Rust factor for first 2 games back

### 7. News Sentiment Analysis
- **Recency weighting**:
  - Today: 100%
  - Yesterday: 90%
  - 2 days: 75%
  - 3 days: 60%
  - Week old: 40%
  - 2 weeks: 20%
  - Older: 10%
- **Sentiment multipliers**:
  - Very positive: +10%
  - Positive: +5%
  - Neutral: 0%
  - Negative: -5%
  - Very negative: -10%
- **Topic weights**:
  - Injuries: 1.5x
  - Trades: 1.3x
  - Coaching: 1.2x
  - Chemistry: 1.1x

### 8. Confidence Calculation
- **Prediction strength based**:
  - Very strong (>30% gap): 75-95% confidence
  - Strong (20-30%): 65-85%
  - Moderate (10-20%): 55-75%
  - Weak (<10%): 45-65%
- **Uncertainty factors**:
  - Injury uncertainty: -10%
  - New roster: -8%
  - New coach: -5%
  - Long layoff: -5%

### 9. Score Prediction
- **League average**: 112 PPG
- **Home court**: +3 points
- **Pace adjustment**: ±8% for fast/slow teams
- **Matchup adjustments**: ±5 points for mismatches

### 10. Gambling Metrics
- **Spread confidence**:
  - High (>7 points): 70%
  - Medium (3-7): 60%
  - Low (<3): 50%
- **Quarter predictions**: Different variance for Q1-Q4
- **Clutch factors**: 4th quarter high variance

## Usage

### Basic Usage

```python
from enhanced_prediction import predict_game_outcome_advanced

# Make a prediction
result = predict_game_outcome_advanced(
    'Los Angeles Lakers',
    'Boston Celtics',
    game_date='2024-12-25'  # Optional for backtesting
)

print(f"Winner: {result['predicted_winner']}")
print(f"Probability: {result['win_probability']:.1%}")
print(f"Confidence: {result['confidence']:.1%}")
print(f"Score: {result['predicted_scores']['home']} - {result['predicted_scores']['away']}")
```

### Customizing Parameters

```python
from model_config_advanced import load_config, update_parameter, save_config

# Load current config
config = load_config()

# Update a parameter
update_parameter(config, 0.12, 'home_advantage', 'base_advantage')

# Update strength weights
update_parameter(config, 0.30, 'strength_weights', 'win_percentage')
update_parameter(config, 0.15, 'strength_weights', 'recent_form')

# Save changes
save_config(config)
```

### Getting Parameters

```python
from model_config_advanced import get_parameter, load_config

config = load_config()

# Get a parameter
home_adv = get_parameter(config, 'home_advantage', 'base_advantage', default=0.10)

# Get nested parameter
win_weight = get_parameter(config, 'strength_weights', 'win_percentage', default=0.25)
```

### Validating Weights

```python
from model_config_advanced import validate_weights, normalize_weights

# Validate that weights sum to 1.0
weights = config['strength_weights']
if validate_weights(weights):
    print("Weights are valid")

# Auto-normalize weights
normalized = normalize_weights(weights)
```

## Comparison: Basic vs Advanced

| Feature | Basic Config | Advanced Config |
|---------|-------------|-----------------|
| Total Parameters | 20 | 207 |
| Home Advantage | Fixed (10%) | Dynamic (8-15%) |
| Recent Form | Simple average | Time-weighted windows |
| News Sentiment | Basic | Recency + topic weighted |
| Rest Days | Not considered | Detailed impact model |
| Travel | Not considered | Distance + time zones |
| Injuries | Not considered | Star-level impact |
| H2H | Simple | Weighted by recency |
| Confidence | Basic | Multi-factor |
| Score Prediction | Simple | Pace-adjusted |

## Expected Improvements

With proper tuning, the advanced configuration should provide:
- **+5-10% accuracy improvement** over basic config
- **Better calibrated confidence scores**
- **More accurate score predictions** (lower MAE)
- **Better performance on edge cases** (injuries, B2B, travel)
- **Situational awareness** (playoffs, rivalries, etc.)

## Tuning Recommendations

### Start With:
1. **Validate current accuracy** using backtesting
2. **Identify weak areas** (e.g., road games, B2B, close games)
3. **Adjust relevant parameters** by small increments (±0.02)
4. **Test and measure** impact on accuracy
5. **Iterate** until optimal performance

### Parameter Sensitivity:
- **High sensitivity**: `strength_weights`, `home_advantage`, `confidence_factors`
- **Medium sensitivity**: `recent_form`, `news_sentiment`, `rest_schedule`
- **Low sensitivity**: `gambling_metrics`, `situational_factors`

### Best Practices:
- Always validate weights sum to 1.0
- Test changes on historical data first
- Keep optimization history for rollback
- Document parameter changes
- Run full backtest after major changes

## Integration with Existing System

### Option 1: Replace Current Predictions

```python
# In database_prediction.py or main prediction file
from enhanced_prediction import predict_game_outcome_advanced

# Replace existing prediction call
result = predict_game_outcome_advanced(home_team, away_team, game_date)
```

### Option 2: A/B Testing

```python
from database_prediction import predict_game_outcome
from enhanced_prediction import predict_game_outcome_advanced

# Get both predictions
basic_result = predict_game_outcome(home_team, away_team, game_date)
advanced_result = predict_game_outcome_advanced(home_team, away_team, game_date)

# Compare and log
print(f"Basic: {basic_result['predicted_winner']} ({basic_result['confidence']:.1%})")
print(f"Advanced: {advanced_result['predicted_winner']} ({advanced_result['confidence']:.1%})")
```

### Option 3: Ensemble (Recommended)

```python
# Combine both predictions with ensemble weights
ensemble_weights = config['ensemble_weights']

basic_prob = basic_result['win_probability']
advanced_prob = advanced_result['win_probability']

final_prob = (
    ensemble_weights['statistical_model'] * basic_prob +
    ensemble_weights['hybrid_model'] * advanced_prob
)
```

## Maintenance

### Regular Tasks:
1. **Weekly**: Review prediction accuracy
2. **Monthly**: Analyze performance by category
3. **Quarterly**: Major parameter tuning
4. **Yearly**: Full configuration review

### Monitoring:
- Track accuracy by confidence level
- Monitor prediction gap distribution
- Analyze systematic biases (home/away, strong/weak teams)
- Compare against betting lines

## Troubleshooting

### Issue: Weights don't sum to 1.0
```python
from model_config_advanced import normalize_weights
weights = normalize_weights(config['strength_weights'])
```

### Issue: Predictions too conservative
- Increase confidence multipliers
- Reduce uncertainty penalties
- Adjust `min_confidence` upward

### Issue: Predictions too aggressive
- Decrease confidence multipliers
- Increase uncertainty penalties
- Adjust `max_confidence` downward

### Issue: Poor score predictions
- Check `league_average` matches current NBA scoring
- Adjust `strength_multiplier`
- Validate offensive/defensive efficiency calculations

## Next Steps

1. **Run full backtest** with advanced config
2. **Compare results** to basic config
3. **Identify improvement areas**
4. **Fine-tune parameters**
5. **Deploy to production**
6. **Monitor and iterate**

## Support

For questions or issues:
- Check parameter descriptions in `model_config_advanced.py`
- Review this guide
- Test changes on small dataset first
- Keep backup of working configuration
















