# 🎯 Prediction Model Calibration Guide

## Overview

The prediction system now includes **adaptive calibration** that automatically adjusts confidence scores based on historical backtest performance to ensure predictions are realistic and well-calibrated.

## How It Works

### 1. **Automatic Calibration**
The system tracks prediction performance and automatically adjusts future predictions:

```python
# In database_prediction.py
if historical_predictions > 20:
    historical_accuracy = correct / total
    historical_avg_confidence = average_confidence
    
    calibration_factor = historical_accuracy / historical_avg_confidence
    confidence = confidence * calibration_factor
```

### 2. **Calibration Factor Interpretation**

| Calibration Factor | Meaning | Action |
|-------------------|---------|--------|
| < 0.9 | **OVERCONFIDENT** | Reduce confidence scores |
| 0.9 - 1.1 | **WELL-CALIBRATED** | No adjustment needed |
| > 1.1 | **UNDERCONFIDENT** | Increase confidence scores |

### 3. **Example**

**Before Calibration:**
- Model predicts with 70% confidence
- Actual accuracy: 55%
- Calibration factor: 55% / 70% = 0.786

**After Calibration:**
- Adjusted confidence: 70% × 0.786 = 55%
- Now confidence matches actual performance!

## Using the Quick Backtest

### Step 1: Run Backtest
1. Open Streamlit app: `streamlit run pages/Hybrid_Predict.py`
2. Navigate to **Quick Backtest** page
3. Set number of games (20-50 recommended)
4. Click **"Run Quick Backtest"**

### Step 2: Review Results
The backtest shows:
- **Overall Accuracy**: How often predictions are correct
- **Average Confidence**: How confident the model is
- **Calibration Factor**: Ratio of accuracy to confidence

### Step 3: Interpret Calibration

**Example 1: Overconfident Model**
```
Accuracy: 58%
Avg Confidence: 72%
Calibration Factor: 0.81

❌ Model is 19% OVERCONFIDENT
💡 Multiply all confidence by 0.81
```

**Example 2: Well-Calibrated Model**
```
Accuracy: 63%
Avg Confidence: 61%
Calibration Factor: 1.03

✅ Model is WELL-CALIBRATED
```

**Example 3: Underconfident Model**
```
Accuracy: 68%
Avg Confidence: 55%
Calibration Factor: 1.24

⚠️ Model is 24% UNDERCONFIDENT
💡 Multiply all confidence by 1.24
```

## Automatic vs Manual Calibration

### Automatic (Default)
- System learns from every prediction
- Requires 20+ predictions to activate
- Smoothed adjustment (70% calibration, 30% original)
- No manual intervention needed

### Manual (Optional)
If you want to force a specific calibration:

1. Run `python calibrate_from_backtest.py`
2. Review calibration factors
3. Manually adjust `database_prediction.py` if needed

## Best Practices

### 1. Regular Backtesting
- Run backtest after every 50-100 predictions
- Monitor calibration drift over time
- Seasonal adjustments may be needed

### 2. Confidence Bounds
Current system limits:
- **Minimum**: 15% (very uncertain)
- **Maximum**: 80% (high confidence, but realistic)
- Never above 90% (NBA is unpredictable!)

### 3. When to Recalibrate

Recalibrate if:
- ✅ After major data updates
- ✅ Start of new season
- ✅ After 100+ new predictions
- ✅ Calibration factor drifts outside 0.9-1.1 range

Don't recalibrate if:
- ❌ Sample size < 20 predictions
- ❌ Recent recalibration (< 1 week)
- ❌ Calibration factor is 0.9-1.1

## Confidence Interpretation

After calibration, confidence levels should mean:

| Confidence | Interpretation | Expected Accuracy |
|-----------|----------------|-------------------|
| 15-30% | Very Uncertain | ~50% (coin flip) |
| 30-45% | Uncertain | ~50-55% |
| 45-55% | Low Confidence | ~55-60% |
| 55-65% | Medium Confidence | ~60-65% |
| 65-75% | High Confidence | ~65-75% |
| 75-80% | Very High Confidence | ~75-80% |

## Monitoring Calibration

### Key Metrics to Track

1. **Overall Accuracy** vs **Average Confidence**
   - Should be within 5% of each other
   
2. **Calibration by Confidence Bucket**
   - High confidence predictions should be more accurate
   - Low confidence predictions should be less accurate

3. **Calibration Trend**
   - Monitor if calibration factor is drifting
   - Seasonal patterns may exist

### Red Flags

⚠️ **Calibration Factor < 0.7**
- Model is severely overconfident
- Immediate recalibration needed

⚠️ **Calibration Factor > 1.3**
- Model is severely underconfident
- Check if data quality improved

⚠️ **Accuracy < 52%**
- Model performing near random
- May need feature/model improvements

## Technical Details

### Calibration Algorithm

```python
def apply_adaptive_calibration(raw_confidence, historical_data):
    if historical_data['total'] > 20:
        accuracy = historical_data['correct'] / historical_data['total']
        avg_confidence = historical_data['avg_confidence']
        
        # Calculate calibration factor
        calibration_factor = accuracy / avg_confidence
        
        # Smooth adjustment (70% new, 30% original)
        calibration_factor = 0.7 * calibration_factor + 0.3 * 1.0
        
        # Apply calibration
        calibrated = raw_confidence * calibration_factor
        
        # Enforce bounds
        return max(0.15, min(0.80, calibrated))
    
    return raw_confidence
```

### Why Smoothing?

Smoothing prevents overcorrection:
- Small sample fluctuations don't drastically change calibration
- Gradual adjustment over time
- More stable predictions

## Troubleshooting

### Problem: Calibration not applying
**Solution**: Need 20+ historical predictions
- Run more predictions
- Check `model_performance.json` exists

### Problem: Calibration too aggressive
**Solution**: Increase smoothing factor
- Change `0.7` to `0.5` in calibration code
- Or reduce to `0.3` for very conservative calibration

### Problem: Calibration not improving
**Solution**: 
1. Check data quality
2. Review team strength calculations
3. Verify news sentiment is working
4. Consider feature engineering improvements

## Summary

✅ **Automatic calibration** ensures realistic confidence scores
✅ **Quick Backtest** provides instant feedback
✅ **Adaptive learning** improves over time
✅ **Realistic bounds** prevent overconfidence

The calibrated system now provides:
- More realistic confidence scores (15-80% range)
- Better alignment between confidence and accuracy
- Automatic adjustment based on historical performance
- Clear feedback on model calibration status

