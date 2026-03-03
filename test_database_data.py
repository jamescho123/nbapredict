#!/usr/bin/env python3
"""
Test Database Data Availability
Check what stats and news data is available
"""

import psycopg2
import pandas as pd
from datetime import datetime, timedelta

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

def test_database_connection():
    """Test database connection and data availability"""
    print("🔍 Testing Database Data Availability")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Database connection successful")
        
        cursor = conn.cursor()
        
        # Test Teams table
        print("\n📊 Testing Teams Table:")
        cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."Teams"')
        team_count = cursor.fetchone()[0]
        print(f"   Total teams: {team_count}")
        
        if team_count > 0:
            cursor.execute(f'SELECT "TeamName", "Wins", "Losses", "PointsFor", "PointsAgainst" FROM "{DB_SCHEMA}"."Teams" LIMIT 5')
            teams = cursor.fetchall()
            print("   Sample teams:")
            for team in teams:
                print(f"     {team[0]}: {team[1]}W-{team[2]}L, {team[3]}PF-{team[4]}PA")
        
        # Test News table
        print("\n📰 Testing News Table:")
        cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."News"')
        news_count = cursor.fetchone()[0]
        print(f"   Total news articles: {news_count}")
        
        if news_count > 0:
            cursor.execute(f'SELECT "Team", "Title", "Date", "Sentiment" FROM "{DB_SCHEMA}"."News" ORDER BY "Date" DESC LIMIT 5')
            news = cursor.fetchall()
            print("   Recent news:")
            for article in news:
                print(f"     {article[0]} ({article[2]}): {article[1][:50]}... [{article[3]}]")
        
        # Test Schedule table
        print("\n📅 Testing Schedule Table:")
        cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."Schedule"')
        schedule_count = cursor.fetchone()[0]
        print(f"   Total scheduled games: {schedule_count}")
        
        if schedule_count > 0:
            cursor.execute(f'SELECT "Date", "HomeTeam", "AwayTeam" FROM "{DB_SCHEMA}"."Schedule" ORDER BY "Date" ASC LIMIT 5')
            games = cursor.fetchall()
            print("   Upcoming games:")
            for game in games:
                print(f"     {game[0]}: {game[2]} @ {game[1]}")
        
        # Test Players table
        print("\n👥 Testing Players Table:")
        cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."Players"')
        player_count = cursor.fetchone()[0]
        print(f"   Total players: {player_count}")
        
        if player_count > 0:
            cursor.execute(f'SELECT "PlayerName", "Team", "Position" FROM "{DB_SCHEMA}"."Players" LIMIT 5')
            players = cursor.fetchall()
            print("   Sample players:")
            for player in players:
                print(f"     {player[0]} ({player[2]}) - {player[1]}")
        
        conn.close()
        print("\n✅ Database test complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()
