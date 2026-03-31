# Temporal Filtering for Backtest Implementation

## Problem Statement
User identified that when backtesting a game on 2024/10/23, the prediction should only use data available BEFORE that date. Without temporal filtering, the model would use all historical data including future games, leading to **data leakage** and overly optimistic backtest results.

## Solution Implemented

Added `as_of_date` / `game_date` parameter to all data retrieval functions to enable temporal filtering:

### Modified Functions

#### 1. **get_team_stats(team_name, as_of_date=None)**
```sql
-- Added date filter
WHERE ("HomeTeamName" = %s OR "VisitorTeamName" = %s)
AND "Date" < %s  -- Only matches before as_of_date
```

#### 2. **get_recent_matches(team_name, days=30, as_of_date=None)**
```sql
-- Filters to get matches in date range [as_of_date - days, as_of_date)
WHERE ("HomeTeamName" = %s OR "VisitorTeamName" = %s)
AND "Date" >= %s  -- cutoff_date (as_of_date - days)
AND "Date" < %s   -- as_of_date
```

#### 3. **get_team_news(team_name, limit=15, as_of_date=None)**
```sql
-- Only news published before as_of_date
WHERE (n."Title" ILIKE %s OR n."Content" ILIKE %s)
AND n."Date" < %s
```

#### 4. **get_time_weighted_team_news(team_name, days_back=30, limit=20, as_of_date=None)**
```sql
-- Time-weighted news relative to as_of_date (not current date)
CASE 
    WHEN n."Date" >= (%s::date - INTERVAL '1 day') THEN 1.0
    WHEN n."Date" >= (%s::date - INTERVAL '7 days') THEN 0.8
    -- etc...
END as time_weight
WHERE (n."Title" ILIKE %s OR n."Content" ILIKE %s)
   AND n."Date" >= %s  -- cutoff_date
   AND n."Date" < %s   -- as_of_date
```

#### 5. **calculate_team_form(team_name, days=10, as_of_date=None)**
- Passes `as_of_date` to `get_recent_matches()`

#### 6. **get_head_to_head_record(team1, team2, limit=10, as_of_date=None)**
```sql
-- Only H2H games before as_of_date
WHERE (("HomeTeamName" = %s AND "VisitorTeamName" = %s)
   OR ("HomeTeamName" = %s AND "VisitorTeamName" = %s))
AND "Date" < %s
```

#### 7. **get_team_context_data(team_name, as_of_date=None)**
- Passes `as_of_date` to all data retrieval functions
- Adds "(as of DATE)" to debug output when filtering

#### 8. **prepare_prediction_data(home_team, away_team, as_of_date=None)**
- Passes `as_of_date` to both `get_team_context_data()` calls
- Passes `as_of_date` to `get_head_to_head_record()`

#### 9. **predict_game_outcome(home_team, away_team, game_date=None)**
```python
"""
Args:
    home_team: Name of the home team
    away_team: Name of the away team  
    game_date: Optional date of the game for backtesting (only use data before this date)
"""
prediction_data = prepare_prediction_data(home_team, away_team, as_of_date=game_date)
```

#### 10. **Backtest_Analysis.py**
```python
# Changed from:
prediction = predict_game_outcome(home_team, away_team)

# To:
prediction = predict_game_outcome(home_team, away_team, game_date=game_date)
```

## Test Results

### With Temporal Filtering (as of 2024-10-23):
- Lakers stats: 0.773
- Warriors stats: 0.444
- Found 2 news articles (only before 2024-10-23)
- Predicted: Lakers 121 - Warriors 110

### Without Temporal Filtering (current):
- Lakers stats: 0.760
- Warriors stats: 0.470
- Found 10 news articles (all historical)
- Predicted: Lakers 119 - Warriors 104

**✓ CORRECT**: Team strengths differ with temporal filtering, confirming that the filter works.

## How It Works

1. **Backtest calls** `predict_game_outcome(home, away, game_date="2024-10-23")`

2. **predict_game_outcome** passes `game_date` to `prepare_prediction_data(as_of_date=game_date)`

3. **prepare_prediction_data** passes `as_of_date` to:
   - `get_team_context_data(home_team, as_of_date)`
   - `get_team_context_data(away_team, as_of_date)`
   - `get_head_to_head_record(home, away, as_of_date)`

4. **get_team_context_data** passes `as_of_date` to:
   - `get_team_stats(team, as_of_date)`
   - `calculate_team_form(team, as_of_date)` → `get_recent_matches(team, days, as_of_date)`
   - `get_time_weighted_team_news(team, days, limit, as_of_date)`
   - `get_team_news(team, limit, as_of_date)`

5. **All SQL queries** filter by `WHERE "Date" < as_of_date`

## Impact

- **Prevents data leakage** in backtesting
- **More accurate** evaluation of model performance
- **Realistic confidence metrics** based only on available data
- **Proper simulation** of real-time prediction scenarios

## Backward Compatibility

When `game_date`/`as_of_date` is `None` (default):
- No date filtering applied
- Uses all available historical data
- Functions exactly as before (current prediction mode)

This preserves existing behavior for real-time predictions while enabling proper temporal filtering for backtesting.

---
**Date**: 2025-10-27
**Status**: Complete - All data retrieval functions support temporal filtering


