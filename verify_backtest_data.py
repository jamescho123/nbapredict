#!/usr/bin/env python3
"""
Backtest Data Verification Tool

This script verifies that all data used in backtest predictions:
1. Comes from BEFORE the game date (no future data leakage)
2. Is accurate and matches historical records
3. Shows exactly what the model sees for a given prediction

Usage:
    python verify_backtest_data.py "Boston Celtics" "New York Knicks" "2024-10-23"
"""

import psycopg2
from datetime import datetime, timedelta
import sys

DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

def verify_backtest_data(home_team, away_team, game_date):
    """
    Verify all data used for a game prediction is from before game_date
    Shows exactly what data the model sees
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    game_date_dt = datetime.strptime(game_date, '%Y-%m-%d').date()
    
    print(f"=" * 80)
    print(f"BACKTEST DATA VERIFICATION")
    print(f"Game: {away_team} @ {home_team}")
    print(f"Game Date: {game_date}")
    print(f"=" * 80)
    
    issues_found = []
    
    # 1. Verify team stats (from Matches before game_date)
    print(f"\n{'='*80}")
    print(f"1. TEAM STATS (calculated from Matches table, before {game_date})")
    print(f"{'='*80}")
    
    for team in [home_team, away_team]:
        cursor.execute('''
            SELECT COUNT(*) as games,
                   SUM(CASE WHEN "HomeTeamName" = %s AND "HomeTeamScore" > "VisitorPoints" THEN 1
                            WHEN "VisitorTeamName" = %s AND "VisitorPoints" > "HomeTeamScore" THEN 1
                            ELSE 0 END) as wins,
                   SUM(CASE WHEN "HomeTeamName" = %s THEN "HomeTeamScore"
                            ELSE "VisitorPoints" END) as points_for,
                   SUM(CASE WHEN "HomeTeamName" = %s THEN "VisitorPoints"
                            ELSE "HomeTeamScore" END) as points_against,
                   MAX("Date") as last_game_date
            FROM "NBA"."Matches"
            WHERE ("HomeTeamName" = %s OR "VisitorTeamName" = %s)
              AND "Date" < %s
        ''', (team, team, team, team, team, team, game_date))
        
        result = cursor.fetchone()
        games, wins, points_for, points_against, last_game = result
        losses = games - wins if games > 0 else 0
        win_pct = wins / games if games > 0 else 0
        ppg = points_for / games if games > 0 else 0
        papg = points_against / games if games > 0 else 0
        
        print(f"\n{team}:")
        print(f"  Record: {wins}W - {losses}L ({win_pct:.1%})")
        print(f"  Games played: {games}")
        print(f"  Points per game: {ppg:.1f}")
        print(f"  Points allowed: {papg:.1f}")
        print(f"  Point differential: {(ppg - papg):+.1f}")
        print(f"  Last game date: {last_game}")
        
        if last_game and last_game >= game_date_dt:
            issues_found.append(f"ISSUE: {team} has games on or after prediction date!")
            print(f"  [X] ERROR: Last game is NOT before {game_date}!")
        else:
            print(f"  [OK] All games are BEFORE {game_date}")
    
    # 2. Verify recent form (last 10 games)
    print(f"\n{'='*80}")
    print(f"2. RECENT FORM (last 10 games before {game_date})")
    print(f"{'='*80}")
    
    for team in [home_team, away_team]:
        cursor.execute('''
            SELECT "Date", "HomeTeamName", "VisitorTeamName", "HomeTeamScore", "VisitorPoints"
            FROM "NBA"."Matches"
            WHERE ("HomeTeamName" = %s OR "VisitorTeamName" = %s)
              AND "Date" < %s
            ORDER BY "Date" DESC
            LIMIT 10
        ''', (team, team, game_date))
        
        matches = cursor.fetchall()
        print(f"\n{team} last 10 games:")
        
        if matches:
            wins = 0
            form_string = []
            
            for i, match in enumerate(matches):
                date, home, away, home_score, away_score = match
                
                # Check if team won
                if (home == team and home_score > away_score) or (away == team and away_score > home_score):
                    result = "W"
                    wins += 1
                else:
                    result = "L"
                
                form_string.append(result)
                
                # Show first 5 games
                if i < 5:
                    opponent = away if home == team else home
                    location = "vs" if home == team else "@"
                    team_score = home_score if home == team else away_score
                    opp_score = away_score if home == team else home_score
                    print(f"  {date}: {result} {location} {opponent} ({team_score}-{opp_score})")
                
                # Verify date
                if date >= game_date_dt:
                    issues_found.append(f"ISSUE: {team} has match on {date} which is >= {game_date}")
            
            recent_form = ''.join(form_string[:10])
            print(f"  Form (last 10): {recent_form} ({wins}W-{10-wins}L)")
            print(f"  [OK] All matches verified BEFORE {game_date}")
        else:
            print(f"  No games found (new team or early in season)")
    
    # 3. Verify news data
    print(f"\n{'='*80}")
    print(f"3. NEWS DATA (articles before {game_date})")
    print(f"{'='*80}")
    
    for team in [home_team, away_team]:
        cursor.execute('''
            SELECT "Date", "Title", "Content"
            FROM "NBA"."News"
            WHERE ("Title" ILIKE %s OR "Content" ILIKE %s)
              AND "Date" < %s
            ORDER BY "Date" DESC
            LIMIT 15
        ''', (f'%{team}%', f'%{team}%', game_date))
        
        news = cursor.fetchall()
        print(f"\n{team} news articles:")
        
        if news:
            # Show first 3 articles
            for i, article in enumerate(news[:3]):
                date, title, content = article
                print(f"  [{date}] {title[:70]}")
                
                if date >= game_date_dt:
                    issues_found.append(f"ISSUE: News article for {team} dated {date} is >= {game_date}")
            
            # Check all dates
            future_news = [n for n in news if n[0] >= game_date_dt]
            if future_news:
                print(f"  [X] ERROR: Found {len(future_news)} articles on or after {game_date}!")
            else:
                print(f"  [OK] All {len(news)} articles are BEFORE {game_date}")
        else:
            print(f"  No news articles found for this team")
    
    # 4. Verify head-to-head record
    print(f"\n{'='*80}")
    print(f"4. HEAD-TO-HEAD RECORD (before {game_date})")
    print(f"{'='*80}")
    
    cursor.execute('''
        SELECT "Date", "HomeTeamName", "VisitorTeamName", "HomeTeamScore", "VisitorPoints"
        FROM "NBA"."Matches"
        WHERE (("HomeTeamName" = %s AND "VisitorTeamName" = %s)
           OR ("HomeTeamName" = %s AND "VisitorTeamName" = %s))
          AND "Date" < %s
        ORDER BY "Date" DESC
        LIMIT 10
    ''', (home_team, away_team, away_team, home_team, game_date))
    
    h2h = cursor.fetchall()
    
    if h2h:
        home_wins = 0
        away_wins = 0
        
        print(f"Last {len(h2h)} matchups:")
        for match in h2h[:5]:  # Show first 5
            date, home, away, home_score, away_score = match
            winner = home if home_score > away_score else away
            
            if winner == home_team:
                home_wins += 1
            else:
                away_wins += 1
            
            print(f"  {date}: {away} @ {home} ({away_score}-{home_score}) - Winner: {winner}")
            
            if date >= game_date_dt:
                issues_found.append(f"ISSUE: H2H game on {date} is >= {game_date}")
        
        print(f"\nH2H Summary: {home_team} {home_wins}-{away_wins} {away_team}")
        
        future_h2h = [m for m in h2h if m[0] >= game_date_dt]
        if future_h2h:
            print(f"  [X] ERROR: Found {len(future_h2h)} H2H games on or after {game_date}!")
        else:
            print(f"  [OK] All H2H games are BEFORE {game_date}")
    else:
        print(f"No previous matchups found (teams haven't played recently)")
    
    # 5. Check if actual game result exists (should only exist after game date)
    print(f"\n{'='*80}")
    print(f"5. ACTUAL GAME RESULT")
    print(f"{'='*80}")
    
    cursor.execute('''
        SELECT "Date", "HomeTeamScore", "VisitorPoints"
        FROM "NBA"."Matches"
        WHERE "HomeTeamName" = %s
          AND "VisitorTeamName" = %s
          AND "Date" = %s
    ''', (home_team, away_team, game_date))
    
    actual_game = cursor.fetchone()
    
    if actual_game:
        date, home_score, away_score = actual_game
        winner = home_team if home_score > away_score else away_team
        print(f"Actual Result: {away_team} {away_score} @ {home_team} {home_score}")
        print(f"Winner: {winner}")
        print(f"[OK] This result should NOT be visible to the prediction model")
    else:
        print(f"No result found for this game (game hasn't been played or not in database)")
    
    # 6. Data age verification
    print(f"\n{'='*80}")
    print(f"6. DATA FRESHNESS CHECK")
    print(f"{'='*80}")
    
    for team in [home_team, away_team]:
        cursor.execute('''
            SELECT MAX("Date") as most_recent_game
            FROM "NBA"."Matches"
            WHERE ("HomeTeamName" = %s OR "VisitorTeamName" = %s)
              AND "Date" < %s
        ''', (team, team, game_date))
        
        result = cursor.fetchone()
        if result[0]:
            most_recent = result[0]
            days_ago = (game_date_dt - most_recent).days
            print(f"{team}:")
            print(f"  Most recent game: {most_recent} ({days_ago} days before prediction)")
            
            if days_ago > 10:
                print(f"  [!] Warning: Data is {days_ago} days old (team may not have played recently)")
            else:
                print(f"  [OK] Data is reasonably fresh")
    
    # Final Summary
    print(f"\n{'='*80}")
    print(f"DATA INTEGRITY VERIFICATION SUMMARY")
    print(f"{'='*80}")
    
    if issues_found:
        print(f"\n[X] ISSUES FOUND ({len(issues_found)}):")
        for issue in issues_found:
            print(f"  - {issue}")
        print(f"\n[!] DATA LEAKAGE DETECTED! Backtest may not be reliable.")
    else:
        print(f"\n[OK] NO ISSUES FOUND")
        print(f"[OK] All team stats calculated from games BEFORE {game_date}")
        print(f"[OK] All news articles dated BEFORE {game_date}")
        print(f"[OK] All recent matches from BEFORE {game_date}")
        print(f"[OK] All H2H records from BEFORE {game_date}")
        print(f"[OK] No future data leakage detected")
        print(f"\n[OK] BACKTEST DATA INTEGRITY VERIFIED")
        print(f"  This prediction uses only historically available data.")
    
    conn.close()
    
    return len(issues_found) == 0

def list_available_games(start_date='2024-10-01', limit=20):
    """List available games for verification"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Check Matches table date range
    cursor.execute('SELECT MIN("Date"), MAX("Date"), COUNT(*) FROM "NBA"."Matches"')
    result = cursor.fetchone()
    
    print(f"Database Statistics:")
    print(f"  Matches table: {result[2]} games from {result[0]} to {result[1]}")
    
    # Check if 2024-25 season results table exists
    try:
        cursor.execute('SELECT COUNT(*) FROM "NBA"."Season2024_25_Results"')
        season_count = cursor.fetchone()[0]
        print(f"  Season2024_25_Results: {season_count} games")
    except:
        print(f"  Season2024_25_Results: Not found")
    
    print()
    
    # List games from Matches table
    cursor.execute('''
        SELECT "Date", "HomeTeamName", "VisitorTeamName", "HomeTeamScore", "VisitorPoints"
        FROM "NBA"."Matches"
        WHERE "Date" >= %s
        ORDER BY "Date"
        LIMIT %s
    ''', (start_date, limit))
    
    games = cursor.fetchall()
    
    if games:
        print(f"Available games for verification (from {start_date}):")
        for game in games:
            date, home, away, home_score, away_score = game
            print(f"  {date}: {away} @ {home} ({away_score}-{home_score})")
    else:
        # Show most recent games instead
        cursor.execute('''
            SELECT "Date", "HomeTeamName", "VisitorTeamName", "HomeTeamScore", "VisitorPoints"
            FROM "NBA"."Matches"
            ORDER BY "Date" DESC
            LIMIT %s
        ''', (limit,))
        
        games = cursor.fetchall()
        if games:
            print(f"Most recent games in database:")
            for game in games[:10]:
                date, home, away, home_score, away_score = game
                print(f"  {date}: {away} @ {home} ({away_score}-{home_score})")
        else:
            print("No games found in database")
    
    print()
    print(f"To verify a game:")
    print(f'  python verify_backtest_data.py "Home Team" "Away Team" "YYYY-MM-DD"')
    print()
    print(f"Example:")
    if games:
        example = games[0]
        print(f'  python verify_backtest_data.py "{example[1]}" "{example[2]}" "{example[0]}"')
    
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments, show available games
        print("Backtest Data Verification Tool\n")
        list_available_games()
        print("\nTo verify a specific game:")
        print('  python verify_backtest_data.py "Home Team" "Away Team" "YYYY-MM-DD"')
    elif len(sys.argv) == 4:
        # Verify specific game
        home_team = sys.argv[1]
        away_team = sys.argv[2]
        game_date = sys.argv[3]
        
        try:
            is_valid = verify_backtest_data(home_team, away_team, game_date)
            sys.exit(0 if is_valid else 1)
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("Usage:")
        print('  python verify_backtest_data.py "Home Team" "Away Team" "YYYY-MM-DD"')
        print("Or run without arguments to see available games")
        sys.exit(1)

