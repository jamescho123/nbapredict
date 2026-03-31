# Basketball Reference Import - 2024-25 Season

## Overview

This import script fetches **real game data** from [Basketball-Reference.com](https://www.basketball-reference.com/leagues/NBA_2025_games.html) for the 2024-25 NBA season.

## What Changed

### Previous Approach (Simulated Data)
- `import_2024_25_season.py` - Generated fake/simulated game results
- `import_real_2024_25_season.py` - Generated fake/simulated game results
- **Problem**: Games had wrong dates (2025-10-21, 2025-11-12, 2025-12-12) that haven't happened yet

### New Approach (Real Data)
- `import_basketball_reference_2024_25.py` - Fetches actual games from Basketball Reference
- **Solution**: Uses real game dates and scores from October 2024 - April 2025

## 2024-25 Season Timeline

According to [Basketball-Reference.com](https://www.basketball-reference.com/leagues/NBA_2025_games.html):

- **Season Start**: October 22, 2024
- **Regular Season**: October 2024 - April 2025  
- **Playoffs**: April - June 2025
- **Champion**: Oklahoma City Thunder
- **MVP**: Shai Gilgeous-Alexander

## How to Use

### Quick Start

Run the complete backtest suite:

```bash
python run_2024_25_backtest.py
```

This will:
1. Import real 2024-25 season data from Basketball Reference
2. Run comprehensive backtest on completed games
3. Generate detailed performance metrics

### Manual Steps

#### Step 1: Import Data

```bash
python import_basketball_reference_2024_25.py
```

This fetches:
- October 2024 - April 2025 games
- Real scores for completed games
- Actual game dates and times

#### Step 2: Run Backtest

```bash
python backtest_2024_25_season.py
```

Tests predictions against actual results.

### Alternative Backtest Scripts

All backtest scripts now use the correct date range (Oct 22, 2024 - June 15, 2025):

```bash
# Quick backtest (15 games)
python quick_backtest.py

# Simple backtest (10 games)
python simple_backtest.py

# Fast backtest (20 games)
python fast_backtest.py

# Realistic backtest (15 games with full context)
python realistic_backtest.py
```

## Database Tables

The import creates:

1. **Season2024_25_Schedule** - All scheduled games
2. **Season2024_25_Results** - Completed games with scores
3. **Season2024_25_TeamStats** - Team statistics (optional)

## Data Source

All data is sourced from Basketball-Reference.com:
- Main page: https://www.basketball-reference.com/leagues/NBA_2025_games.html
- Monthly schedules: `/leagues/NBA_2025_games-{month}.html`

## Requirements

```bash
pip install beautifulsoup4 requests psycopg2
```

## Troubleshooting

### No games found
```bash
# Clear existing data and reimport
python import_basketball_reference_2024_25.py
```

### Database connection error
Check `DB_CONFIG` in the script:
- host: localhost
- database: James
- user: postgres
- password: jcjc1749

### Website not accessible
- Check internet connection
- Basketball-Reference.com may be blocking requests
- Try again after a few minutes

## Notes

- The script includes a 1-second delay between month fetches to be respectful to the website
- Only completed games with scores are added to the Results table
- Games without scores are added to the Schedule table only
- The import drops and recreates tables each time to ensure clean data

## Comparison: Old vs New

### Old Import (Simulated)
```
2025-11-12  Chicago Bulls      Boston Celtics      ❌ Future date
2025-12-12  Philadelphia 76ers Memphis Grizzlies   ❌ Future date  
2025-10-21  Oklahoma City      Houston Rockets     ❌ Wrong date
```

### New Import (Real)
```
2024-10-22  New York Knicks    Boston Celtics      ✅ 109-132 (Actual)
2024-10-22  Minnesota          LA Lakers           ✅ 103-110 (Actual)
2024-10-23  Indiana Pacers     Detroit Pistons     ✅ 115-109 (Actual)
```

## References

- [Basketball-Reference.com 2024-25 Season](https://www.basketball-reference.com/leagues/NBA_2025_games.html)
- [2024-25 NBA Schedule](https://www.basketball-reference.com/leagues/NBA_2025_games-october.html)


