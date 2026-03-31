# Auto-Optimization System for NBA Prediction Model

## Overview

The auto-optimization system automatically tunes your prediction model's hyperparameters to achieve the best accuracy. It runs multiple backtests with different parameter configurations and identifies the optimal settings.

## New Files Created

### 1. `model_config.py`
**Purpose**: Centralized configuration management

**Features**:
- Stores all tunable model hyperparameters
- Loads/saves configuration to `model_config.json`
- Tracks optimization history
- Manages best performing configuration

**Key Parameters**:
```python
- home_advantage: 0.1 (10% boost for home team)
- strength_weights:
  - win_percentage: 0.30
  - point_differential: 0.25
  - offensive_efficiency: 0.15
  - defensive_efficiency: 0.10
  - recent_form: 0.10
  - news_sentiment: 0.10
- confidence_weights: (for low/high data quality)
- calibration settings: (min/max confidence, smoothing)
```

### 2. `model_optimizer.py`
**Purpose**: Hyperparameter optimization engine

**Features**:
- Generates all parameter combinations to test
- Runs backtests for each configuration
- Tracks results and identifies best config
- Supports quick, moderate, and comprehensive optimization modes

**Optimization Modes**:
- **Quick**: 4 configurations (~1 minute)
- **Moderate**: 24 configurations (~5 minutes)
- **Comprehensive**: 100+ configurations (~20+ minutes)

### 3. `model_config.json`
**Purpose**: Persistent storage of model configuration

**Auto-generated**: Created when you run the system
**Tracks**: Current config + optimization history

## Modified Files

### `database_prediction.py`
**Changes**: 
- Added `from model_config import load_config`
- Replaced hardcoded parameters with `MODEL_CONFIG.get()` calls
- Now reads all tunable parameters from configuration

**Example**:
```python
# Before:
home_advantage = 0.1

# After:
home_advantage = MODEL_CONFIG.get('home_advantage', 0.1)
```

### `pages/Backtest_Analysis.py`
**Changes**:
- Added 3 tabs: Single Backtest, Auto-Optimize, Configuration
- New function: `run_backtest_with_config()` - runs backtest with specific config
- Integrated ModelOptimizer for automatic tuning
- Added UI for manual parameter adjustment

## How to Use

### Method 1: Automatic Optimization (Recommended)

1. Open Streamlit app: `streamlit run Home.py`
2. Navigate to "Backtest Analysis" page
3. Click "🔧 Auto-Optimize Model" tab
4. Select optimization mode:
   - **Quick**: Fast test with 4 configurations
   - **Moderate**: Balanced with 24 configurations  
   - **Comprehensive**: Thorough with 100+ configurations
5. Choose "Games per Configuration" (10-20 recommended)
6. Click "🚀 Start Optimization"
7. Wait for completion (progress shown)
8. Review results and click "💾 Apply Best Config"

### Method 2: Manual Configuration

1. Go to "⚙️ Model Configuration" tab
2. Adjust sliders for each parameter:
   - Home Advantage
   - Strength calculation weights
   - (ensure weights sum to 1.0)
3. Click "💾 Save Configuration"
4. Run regular backtest to test your config

### Method 3: Load Best Historical Config

1. Go to "⚙️ Model Configuration" tab
2. Click "⭐ Load Best Config"
3. System loads the historically best-performing configuration

## How Auto-Optimization Works

```
1. User selects optimization mode (Quick/Moderate/Comprehensive)
   ↓
2. System generates parameter combinations
   Example: home_advantage=[0.08, 0.10, 0.12] x 
            win_pct_weight=[0.25, 0.30, 0.35]
   = 9 configurations to test
   ↓
3. For each configuration:
   a. Temporarily override MODEL_CONFIG
   b. Run backtest on N games (e.g., 15 games)
   c. Calculate accuracy, confidence, score error
   d. Store results
   e. Restore original config
   ↓
4. Identify configuration with highest accuracy
   ↓
5. Display comparison table of all configs
   ↓
6. User clicks "Apply Best Config"
   ↓
7. Best configuration saved to model_config.json
   ↓
8. All future predictions use optimized parameters
```

## Benefits

✅ **Automated Tuning**: No manual trial-and-error
✅ **Data-Driven**: Finds optimal parameters based on actual backtest results
✅ **Temporal Filtering**: Uses proper date filtering to prevent data leakage
✅ **History Tracking**: Keeps record of all optimization runs
✅ **Easy Revert**: Can reset to defaults or load previous best config
✅ **Visual Comparison**: See all tested configs side-by-side

## Example Optimization Results

```
Configuration Comparison:
┌──────────┬────────────┬─────────────┬───────────────┬──────────────┐
│ Accuracy │ Confidence │ Score Error │ Home Advantage│ Win % Weight │
├──────────┼────────────┼─────────────┼───────────────┼──────────────┤
│  68.2%   │   45.3%    │    8.2 pts  │    0.120      │     0.35     │ ← BEST
│  65.1%   │   43.1%    │    9.1 pts  │    0.100      │     0.30     │
│  63.8%   │   44.2%    │    8.7 pts  │    0.080      │     0.25     │
│  62.5%   │   42.8%    │    9.5 pts  │    0.150      │     0.35     │
└──────────┴────────────┴─────────────┴───────────────┴──────────────┘

Best Configuration Found:
  ✓ Home Advantage: 0.120 (12%)
  ✓ Win Percentage Weight: 0.35
  ✓ Recent Form Weight: 0.10
  
Improvement: +5.7% accuracy vs default config
```

## Parameter Descriptions

### home_advantage
- **Range**: 0.0 - 0.20
- **Default**: 0.10
- **Effect**: Boost to home team's strength score
- **Recommendation**: 0.08-0.12 for most balanced results

### strength_weights
**Must sum to 1.0**

- **win_percentage**: Team's overall win-loss record
  - Range: 0.20-0.40
  - Higher = more weight on season performance
  
- **point_differential**: Average point margin
  - Range: 0.15-0.30
  - Higher = more weight on scoring ability
  
- **recent_form**: Last 10 games performance
  - Range: 0.05-0.20
  - Higher = more reactive to current form
  
- **offensive_efficiency**: Points per game
  - Range: 0.10-0.20
  
- **defensive_efficiency**: Points allowed per game
  - Range: 0.05-0.15
  
- **news_sentiment**: Sentiment from news articles
  - Range: 0.05-0.15
  - Higher = more weight on media narrative

### confidence_weights
Controls how confident the model is in its predictions based on available data quality.

### calibration
- **smoothing_factor**: Balance between calibration and original confidence (0.5-0.8)
- **min_confidence**: Minimum confidence threshold (0.10-0.20)
- **max_confidence**: Maximum confidence threshold (0.75-0.90)

## Tips for Best Results

1. **Start with Quick Mode**: Get a feel for the system
2. **Use 15-20 games**: Good balance between speed and reliability
3. **Run Comprehensive Monthly**: Deep optimization periodically
4. **Monitor Improvements**: Track optimization history over time
5. **Season-Specific Tuning**: Re-optimize when new season starts
6. **Combine with Manual**: Fine-tune after auto-optimization

## Troubleshooting

**Q: Optimization takes too long**
- A: Use Quick mode or reduce "Games per Configuration"

**Q: Best config isn't improving accuracy**
- A: Try Comprehensive mode for more thorough search
- A: Increase "Games per Configuration" for more reliable results

**Q: Want to test custom parameters**
- A: Use "Model Configuration" tab to manually adjust and test

**Q: How to revert changes?**
- A: Click "🔄 Reset to Defaults" in Configuration tab

## Technical Details

**Thread Safety**: Configurations are temporarily overridden per backtest run
**Persistence**: Best configs automatically saved to `model_config.json`
**History Limit**: Keeps last 50 optimization results
**Grid Search**: Uses itertools.product for exhaustive parameter combinations
**Evaluation Metric**: Primary = Accuracy, Secondary = Avg Score Error

---
**Created**: 2025-10-27
**Status**: Ready for use
**Next**: Run your first auto-optimization!


