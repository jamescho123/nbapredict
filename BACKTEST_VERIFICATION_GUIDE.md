# Backtest Data Verification Guide

## Overview

The `verify_backtest_data.py` tool allows you to verify that all stats and news used in backtest analysis are correct and don't contain future data leakage.

## Why This Matters

When backtesting predictions, it's critical that:
1. **No Future Data Leakage**: The model only uses data available BEFORE the game date
2. **Accurate Historical Stats**: Team stats reflect their true performance at that point in time
3. **Correct News Context**: News articles are from before the prediction was made

## How to Use

### Check Available Games

Run without arguments to see games you can verify:
```bash
python verify_backtest_data.py
```

### Verify a Specific Game

```bash
python verify_backtest_data.py "Home Team" "Away Team" "YYYY-MM-DD"
```

Example:
```bash
python verify_backtest_data.py "Boston Celtics" "New York Knicks" "2024-10-23"
```

## What Gets Verified

The tool checks 6 critical areas:

### 1. Team Stats
- **What**: Win/loss record, points per game, defensive stats
- **Verification**: All stats calculated ONLY from games before prediction date
- **Shows**: Record, PPG, points allowed, point differential, last game date

Example Output:
```
Boston Celtics:
  Record: 54W - 33L (62.1%)
  Games played: 87
  Points per game: 110.5
  Points allowed: 106.7
  Last game date: 1990-05-06
  [OK] All games are BEFORE 2024-10-23
```

### 2. Recent Form
- **What**: Last 10 games for each team
- **Verification**: All matches are before prediction date
- **Shows**: Win/loss for each game, form string (WWLWL...), opponents

Example Output:
```
Boston Celtics last 10 games:
  1990-05-06: L vs New York Knicks (114-121)
  1990-05-04: L @ New York Knicks (108-135)
  Form (last 10): LLLWWWWWLW (6W-4L)
  [OK] All matches verified BEFORE 2024-10-23
```

### 3. News Data
- **What**: News articles about each team
- **Verification**: All articles dated before prediction date
- **Shows**: Article dates, titles, count

Example Output:
```
Boston Celtics news articles:
  [2024-10-18] Tyler Herro on him and Terry Rozier...
  [2024-10-07] NBA Abu Dhabi Games 2024...
  [OK] All 15 articles are BEFORE 2024-10-23
```

### 4. Head-to-Head Record
- **What**: Recent matchups between the two teams
- **Verification**: All H2H games before prediction date
- **Shows**: Game results, scores, series record

Example Output:
```
H2H Summary: Boston Celtics 2-3 New York Knicks
  [OK] All H2H games are BEFORE 2024-10-23
```

### 5. Actual Game Result
- **What**: The actual outcome of the game being predicted
- **Verification**: Shows if result exists (it shouldn't be visible to model)
- **Shows**: Actual score if game was played

Example Output:
```
Actual Result: New York Knicks 132 @ Boston Celtics 109
Winner: New York Knicks
[OK] This result should NOT be visible to the prediction model
```

### 6. Data Freshness
- **What**: How recent the available data is
- **Verification**: Checks if teams have played recently
- **Shows**: Days since last game before prediction

Example Output:
```
Boston Celtics:
  Most recent game: 2024-10-20 (3 days before prediction)
  [OK] Data is reasonably fresh
```

## Understanding the Results

### Success Indicators
- `[OK]` - Verification passed
- All dates are before prediction date
- No data leakage detected

### Warning Indicators
- `[!]` - Warning (not critical but worth noting)
- Example: Data is old (team hasn't played in >10 days)

### Error Indicators
- `[X]` - Critical error
- Data leakage detected
- Future data found in the dataset

## Example: Complete Verification

```bash
$ python verify_backtest_data.py "Boston Celtics" "New York Knicks" "2024-10-23"

================================================================================
BACKTEST DATA VERIFICATION
Game: New York Knicks @ Boston Celtics
Game Date: 2024-10-23
================================================================================

[Detailed checks for all 6 areas...]

================================================================================
DATA INTEGRITY VERIFICATION SUMMARY
================================================================================

[OK] NO ISSUES FOUND
[OK] All team stats calculated from games BEFORE 2024-10-23
[OK] All news articles dated BEFORE 2024-10-23
[OK] All recent matches from BEFORE 2024-10-23
[OK] All H2H records from BEFORE 2024-10-23
[OK] No future data leakage detected

[OK] BACKTEST DATA INTEGRITY VERIFIED
  This prediction uses only historically available data.
```

## Common Issues and Solutions

### Issue: "Data is X days old"
**What it means**: Team hasn't played recently before prediction date
**Is it a problem?**: Usually no, but the model has less recent data
**Solution**: Normal for early season or after breaks (All-Star, Olympics)

### Issue: "No news articles found"
**What it means**: No news in database mentioning this team
**Is it a problem?**: Reduces prediction accuracy but doesn't invalidate it
**Solution**: Consider importing more news data for better predictions

### Issue: "ERROR: Found games/news on or after prediction date"
**What it means**: **CRITICAL** - Future data leakage detected!
**Is it a problem?**: YES - Backtest results are invalid
**Solution**: Fix the data query to filter by date correctly

## Best Practices

1. **Verify Random Samples**: Check 10-20 random games from your backtest
2. **Check Different Date Ranges**: Verify games from different parts of the season
3. **Spot Check Predictions**: When a prediction seems too accurate, verify that game
4. **Document Issues**: Keep track of any data quality issues you find

## Integration with Backtest

Use this in your backtest workflow:

```python
from verify_backtest_data import verify_backtest_data
from database_prediction import predict_game_outcome

# Before running backtest on a game
game_date = "2024-10-23"
home_team = "Boston Celtics"
away_team = "New York Knicks"

# Verify data integrity
if verify_backtest_data(home_team, away_team, game_date):
    # Data is clean, proceed with prediction
    prediction = predict_game_outcome(home_team, away_team, game_date)
    print(f"Prediction: {prediction['predicted_winner']}")
else:
    print("WARNING: Data integrity issues detected!")
```

## Technical Details

### How It Works
1. Connects to PostgreSQL database
2. Queries Matches table with date filters
3. Queries News table with date filters
4. Verifies all dates are < game_date
5. Reports any violations

### Database Tables Used
- `NBA.Matches` - Historical game results
- `NBA.News` - News articles
- `NBA.Teams` - Team information

### Date Filtering
All queries use: `WHERE "Date" < game_date`

This ensures the model only sees data that was available at the time of prediction.

## FAQ

**Q: Why does it show data from 1990 for a 2024 game?**
A: Your database may only have old historical data. The tool still verifies no future leakage.

**Q: How often should I run verification?**
A: Run it when:
- Setting up a new backtest
- After database updates
- When results seem suspicious
- Periodically (monthly) for quality assurance

**Q: Can I automate verification?**
A: Yes! The tool returns exit code 0 (success) or 1 (failure), perfect for CI/CD:
```bash
python verify_backtest_data.py "Team A" "Team B" "2024-10-23" || exit 1
```

**Q: What if verification fails?**
A: Do NOT use that backtest result. Fix the data issue first, then re-run the backtest.

## Summary

This verification tool is your **data integrity guard** for backtesting. Use it to:
- ✅ Ensure no future data leakage
- ✅ Verify historical accuracy
- ✅ Build confidence in backtest results
- ✅ Catch data quality issues early

**Remember**: A backtest is only as good as the data it uses. Always verify!
















