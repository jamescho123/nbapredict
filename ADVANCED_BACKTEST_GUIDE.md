# Advanced Backtest Guide

## Overview

The advanced backtest system allows you to compare the Basic (20 parameters) and Advanced (207 parameters) configurations to measure accuracy improvements.

## Files Created

- **`advanced_backtest.py`**: Main backtest script with comparison mode
- **`model_config_advanced.json`**: 207-parameter configuration (auto-generated)
- **`enhanced_prediction.py`**: Enhanced prediction engine

## Usage

### Option 1: Compare Both Configurations (Recommended)

```bash
python advanced_backtest.py --mode compare --limit 20
```

This runs both basic and advanced configurations and shows a comparison summary.

**Example Output:**
```
======================================================================
COMPARISON SUMMARY
======================================================================

Metric                         Basic           Advanced        Improvement    
---------------------------------------------------------------------------
Accuracy                       50.0%           30.0%           -20.0%
Avg Confidence                 10.0%           77.2%           +67.2%
Score MAE (points)             7.5             8.7             +1.1 (+15.2%)
Spread Accuracy                40.0%           0.0%            -40.0%
```

### Option 2: Test Advanced Config Only

```bash
python advanced_backtest.py --mode advanced --limit 50
```

### Option 3: Test Basic Config Only

```bash
python advanced_backtest.py --mode basic --limit 50
```

## Command Line Arguments

```bash
python advanced_backtest.py [options]

Options:
  --start DATE      Start date (YYYY-MM-DD), default: 2024-10-01
  --end DATE        End date (YYYY-MM-DD), default: 2024-12-31
  --limit N         Max games to test, default: 50
  --mode MODE       Mode: 'compare', 'advanced', or 'basic', default: 'advanced'
  --save            Save results to JSON file
```

## Examples

### Test 100 games in November 2025

```bash
python advanced_backtest.py --mode compare --start 2025-11-01 --end 2025-12-01 --limit 100
```

### Test and save results

```bash
python advanced_backtest.py --mode advanced --limit 50 --save
```

This creates: `backtest_results_advanced_20251105_214530.json`

### Test specific date range

```bash
python advanced_backtest.py --start 2024-10-22 --end 2025-02-01 --limit 200
```

## Evaluation Metrics

### Primary Metrics

| Metric | Description | Excellent | Good | Needs Work |
|--------|-------------|-----------|------|------------|
| **Accuracy** | % of correct predictions | ≥70% | ≥60% | <55% |
| **Avg Confidence** | Average prediction confidence | N/A | N/A | N/A |
| **Score MAE** | Mean absolute error in score predictions | ≤8 pts | ≤10 pts | >12 pts |
| **Spread Accuracy** | % within ±5 points of actual spread | ≥60% | ≥50% | <50% |

### Confidence Calibration

The system breaks down accuracy by confidence level:

```
Accuracy by Confidence Level:
  0.45-0.55: 48.2% (25 games)
  0.55-0.65: 58.4% (42 games)
  0.65-0.75: 67.1% (38 games)
  0.75-0.85: 75.9% (31 games)
  0.85-0.95: 84.2% (14 games)
```

**Ideal calibration**: 65-75% confidence should yield ~70% accuracy.

## Understanding Results

### Sample Output Interpretation

```
======================================================================
BACKTEST RESULTS - Advanced (207 params)
======================================================================
Total Games:              10
Correct Predictions:      3
Accuracy:                 30.0%           ← Overall win/loss accuracy
Average Confidence:       77.2%           ← How confident the model is
Average Score Error:      8.7 points      ← How far off scores are
Average Spread Error:     15.6 points     ← Spread prediction error
Spread Accuracy (±5pts):  0.0%            ← % within 5 points of actual
```

### What Each Metric Means

1. **Accuracy (30.0%)**: The model correctly predicted the winner in 3 out of 10 games.
   
2. **Average Confidence (77.2%)**: The model was highly confident in its predictions.
   - High confidence + low accuracy = Model is overconfident, needs calibration
   - Low confidence + high accuracy = Model is underconfident
   
3. **Average Score Error (8.7 points)**: Predicted scores were off by ~9 points on average.
   - Excellent: ≤8 points
   - Good: ≤10 points
   - This result is "good"
   
4. **Spread Accuracy (0%)**: None of the spread predictions were within ±5 points.
   - Spread = Home Score - Away Score
   - This metric is important for gambling applications

## Data Source

The backtest uses:
- **Primary**: Real game results from `Matches` table
- **Fallback**: Simulated results from `Schedule` table (for testing)

**Note**: Current implementation uses simulated results. For accurate testing, ensure your database has:
- Actual game results in the `Matches` table
- Valid scores for historical games

## Improving Accuracy

### If Advanced Config Underperforms

1. **Tune key parameters**:
   ```python
   from model_config_advanced import load_config, update_parameter, save_config
   
   config = load_config()
   
   # Reduce home advantage if overestimating home wins
   update_parameter(config, 0.08, 'home_advantage', 'base_advantage')
   
   # Adjust strength weights
   update_parameter(config, 0.30, 'strength_weights', 'win_percentage')
   update_parameter(config, 0.18, 'strength_weights', 'recent_form')
   
   save_config(config)
   ```

2. **Re-run backtest**:
   ```bash
   python advanced_backtest.py --mode advanced --limit 100
   ```

3. **Compare results and iterate**.

### If Confidence is Miscalibrated

If 75% confidence predictions are only 55% accurate:

```python
# Reduce base confidence multipliers
update_parameter(config, 0.50, 'confidence_factors', 'base_confidence', 'high_data_quality', 'base_confidence')
```

### Parameter Tuning Workflow

1. Run initial backtest: `python advanced_backtest.py --mode compare --limit 50`
2. Identify weak areas (e.g., road games, close games, B2B situations)
3. Adjust relevant parameters in `model_config_advanced.py`
4. Re-run backtest to measure improvement
5. Repeat until satisfactory performance

## Common Issues

### Issue: Low Sample Size Warning

```
[INFO] Testing 10 games...
```

**Solution**: Increase `--limit` to at least 50-100 games for reliable statistics.

### Issue: No Games Found

```
[ERROR] No games found
```

**Solutions**:
1. Check date range with `--start` and `--end`
2. Ensure Schedule table has games in that range
3. Try a wider date range: `--start 2024-10-01 --end 2025-04-30`

### Issue: Advanced Config Performs Worse

This can happen if:
1. Sample size is too small (< 30 games)
2. Using simulated data (not real results)
3. Parameters need tuning for your specific dataset
4. Configuration is over-fit to training data

**Solution**: Tune parameters using the optimization guide.

## Saving and Loading Results

### Save Results

```bash
python advanced_backtest.py --mode compare --limit 100 --save
```

Creates: `backtest_results_advanced_YYYYMMDD_HHMMSS.json`

### View Saved Results

```python
import json

with open('backtest_results_advanced_20251105_214530.json', 'r') as f:
    results = json.load(f)

print(f"Accuracy: {results['accuracy']:.1%}")
print(f"Avg Score Error: {results['avg_score_error']:.1f} points")
```

## Integration with Optimization

For systematic parameter optimization:

```python
from advanced_backtest import AdvancedBacktester
from model_config_advanced import load_config, update_parameter, save_config

def optimize_home_advantage():
    """Find optimal home advantage parameter"""
    best_accuracy = 0
    best_value = 0.10
    
    for home_adv in [0.08, 0.09, 0.10, 0.11, 0.12]:
        # Update config
        config = load_config()
        update_parameter(config, home_adv, 'home_advantage', 'base_advantage')
        save_config(config)
        
        # Run backtest
        tester = AdvancedBacktester(use_advanced=True)
        results = tester.run_backtest('2024-10-01', '2025-02-01', 100, verbose=False)
        tester.close()
        
        accuracy = results.get('accuracy', 0)
        print(f"Home advantage {home_adv}: Accuracy {accuracy:.1%}")
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_value = home_adv
    
    print(f"\nBest home advantage: {best_value} (Accuracy: {best_accuracy:.1%})")
    return best_value

# Run optimization
optimal_home_adv = optimize_home_advantage()
```

## Expected Performance

With proper tuning on real data:

| Configuration | Expected Accuracy | Expected Score MAE |
|--------------|-------------------|-------------------|
| **Basic (20 params)** | 55-65% | 10-12 points |
| **Advanced (207 params)** | 60-70% | 8-10 points |
| **Improvement** | +5-10% | -2 to -3 points |

**Note**: These are targets with real historical data and proper parameter tuning.

## Best Practices

1. **Use real data**: Simulated results won't accurately reflect model performance
2. **Test on hold-out set**: Don't optimize parameters on the same games you're testing on
3. **Large sample size**: Use at least 100 games for reliable statistics
4. **Cross-validation**: Test on multiple time periods to ensure consistency
5. **Monitor calibration**: Confidence levels should match actual accuracy
6. **Regular re-tuning**: Re-optimize parameters quarterly as NBA dynamics change

## Next Steps

1. **Run initial comparison**:
   ```bash
   python advanced_backtest.py --mode compare --limit 50
   ```

2. **Review `ADVANCED_CONFIG_GUIDE.md`** for parameter details

3. **Study `model_optimization_guide.md`** for systematic tuning

4. **Tune key parameters** based on backtest results

5. **Deploy best configuration** to production

## Support Files

- **Configuration**: `model_config_advanced.py` (207 parameters)
- **Documentation**: `ADVANCED_CONFIG_GUIDE.md`
- **Optimization**: `model_optimization_guide.md`
- **Enhanced prediction**: `enhanced_prediction.py`

---

**Quick Start**:
```bash
# Initialize config
python model_config_advanced.py

# Run comparison backtest
python advanced_backtest.py --mode compare --limit 20

# Review results and tune parameters
# Re-run until satisfied
```
















