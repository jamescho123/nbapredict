#!/usr/bin/env python3
"""
Diagnose why prediction confidence and data quality are low
"""

import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_prediction import get_team_context_data, predict_game_outcome

def diagnose_data_quality():
    """Diagnose data quality issues"""
    print("🔍 Diagnosing Low Confidence and Data Quality Issues")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        # Check teams table
        print("\n📊 Teams Table Analysis:")
        cur.execute('SELECT COUNT(*) FROM "NBA"."Teams";')
        team_count = cur.fetchone()[0]
        print(f"  Total teams: {team_count}")
        
        if team_count > 0:
            # Check team data quality
            cur.execute('''
                SELECT "TeamName", "Wins", "Losses", "PointsFor", "PointsAgainst"
                FROM "NBA"."Teams" 
                WHERE "Wins" IS NOT NULL AND "Losses" IS NOT NULL
                LIMIT 5
            ''')
            teams = cur.fetchall()
            print(f"  Teams with stats: {len(teams)}")
            
            for team in teams:
                name, wins, losses, pf, pa = team
                total_games = wins + losses if wins and losses else 0
                print(f"    {name}: {wins}-{losses} ({total_games} games), PF: {pf}, PA: {pa}")
        
        # Check players table
        print("\n👥 Players Table Analysis:")
        cur.execute('SELECT COUNT(*) FROM "NBA"."Players";')
        player_count = cur.fetchone()[0]
        print(f"  Total players: {player_count}")
        
        if player_count > 0:
            cur.execute('''
                SELECT "PlayerName", "TeamID", "Position", "Points", "Rebounds", "Assists"
                FROM "NBA"."Players" 
                WHERE "Points" IS NOT NULL
                LIMIT 5
            ''')
            players = cur.fetchall()
            print(f"  Players with stats: {len(players)}")
            
            for player in players:
                name, team_id, pos, pts, reb, ast = player
                print(f"    {name} ({pos}): {pts} PPG, {reb} RPG, {ast} APG")
        
        # Check schedule table
        print("\n🏀 Schedule Table Analysis:")
        cur.execute('SELECT COUNT(*) FROM "NBA"."Schedule";')
        schedule_count = cur.fetchone()[0]
        print(f"  Total games: {schedule_count}")
        
        if schedule_count > 0:
            cur.execute('''
                SELECT "HomeTeam", "AwayTeam", "Date"
                FROM "NBA"."Schedule" 
                ORDER BY "Date" DESC
                LIMIT 5
            ''')
            games = cur.fetchall()
            for game in games:
                home, away, date = game
                print(f"    {away} @ {home} ({date})")
        
        conn.close()
        
        # Test prediction with sample teams
        print("\n🎯 Prediction Quality Test:")
        test_teams = ["Los Angeles Lakers", "Golden State Warriors", "Boston Celtics", "Miami Heat"]
        
        for i in range(0, len(test_teams), 2):
            if i + 1 < len(test_teams):
                team1, team2 = test_teams[i], test_teams[i + 1]
                print(f"\n  Testing: {team1} vs {team2}")
                
                # Get team context
                home_context = get_team_context_data(team1)
                away_context = get_team_context_data(team2)
                
                print(f"    {team1} context: {'✅' if home_context else '❌'}")
                if home_context:
                    stats = home_context.get('team_stats', {})
                    print(f"      Stats: {stats.get('Wins', 0)}-{stats.get('Losses', 0)}")
                    print(f"      Recent form: {home_context.get('recent_form', {})}")
                    print(f"      News: {len(home_context.get('news', []))} articles")
                
                print(f"    {team2} context: {'✅' if away_context else '❌'}")
                if away_context:
                    stats = away_context.get('team_stats', {})
                    print(f"      Stats: {stats.get('Wins', 0)}-{stats.get('Losses', 0)}")
                    print(f"      Recent form: {away_context.get('recent_form', {})}")
                    print(f"      News: {len(away_context.get('news', []))} articles")
                
                # Make prediction
                try:
                    prediction = predict_game_outcome(team1, team2)
                    print(f"    Prediction: {prediction.get('predicted_winner', 'Unknown')}")
                    print(f"    Confidence: {prediction.get('confidence', 0):.1%}")
                    print(f"    Data quality factors: {prediction.get('data_quality_factors', {})}")
                except Exception as e:
                    print(f"    Prediction failed: {e}")
        
        print("\n🔧 Recommendations:")
        print("1. Ensure teams have complete stats (Wins, Losses, PointsFor, PointsAgainst)")
        print("2. Add recent form data (recent games)")
        print("3. Add news articles for sentiment analysis")
        print("4. Add head-to-head historical data")
        print("5. Consider using sample data if real data is limited")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    diagnose_data_quality()
