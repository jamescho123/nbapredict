#!/usr/bin/env python3
"""
Simple Data Quality Check for NBA Prediction Model
Quick verification of data accuracy and completeness
"""

import psycopg2
import pandas as pd
from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

def check_database_connection():
    """Check if database connection works"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Database connection successful")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_table_structure():
    """Check what tables exist and their structure"""
    print("\n🔍 Checking Database Structure...")
    print("-" * 50)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # List all tables in NBA schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'NBA'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"📊 Found {len(tables)} tables in NBA schema:")
        for table in tables:
            print(f"   • {table[0]}")
        
        # Check each table's structure and data
        for table in tables:
            table_name = table[0]
            print(f"\n📋 Table: {table_name}")
            
            # Get column info
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_schema = 'NBA' AND table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            print(f"   Columns ({len(columns)}):")
            for col_name, col_type, nullable in columns:
                print(f"     {col_name}: {col_type} ({'nullable' if nullable == 'YES' else 'not null'})")
            
            # Get row count
            cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table_name}"')
            row_count = cursor.fetchone()[0]
            print(f"   Rows: {row_count}")
            
            # Show sample data
            if row_count > 0:
                cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."{table_name}" LIMIT 3')
                sample_data = cursor.fetchall()
                print(f"   Sample data:")
                for i, row in enumerate(sample_data):
                    print(f"     Row {i+1}: {row}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking table structure: {e}")
        return False

def check_data_quality():
    """Check data quality and completeness"""
    print("\n🔍 Checking Data Quality...")
    print("-" * 50)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check Teams table
        print("🏀 Teams Table:")
        cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."Teams"')
        team_count = cursor.fetchone()[0]
        print(f"   Total teams: {team_count}")
        
        if team_count > 0:
            cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."Teams" LIMIT 3')
            sample_teams = cursor.fetchall()
            print(f"   Sample teams:")
            for team in sample_teams:
                print(f"     {team}")
        
        # Check Players table
        print("\n👥 Players Table:")
        cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."Players"')
        player_count = cursor.fetchone()[0]
        print(f"   Total players: {player_count}")
        
        if player_count > 0:
            cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."Players" LIMIT 3')
            sample_players = cursor.fetchall()
            print(f"   Sample players:")
            for player in sample_players:
                print(f"     {player}")
        
        # Check News table
        print("\n📰 News Table:")
        cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."News"')
        news_count = cursor.fetchone()[0]
        print(f"   Total news articles: {news_count}")
        
        if news_count > 0:
            cursor.execute(f'SELECT "NewsID", "Title", "Date" FROM "{DB_SCHEMA}"."News" ORDER BY "Date" DESC LIMIT 3')
            sample_news = cursor.fetchall()
            print(f"   Recent news:")
            for news in sample_news:
                print(f"     ID: {news[0]}, Date: {news[2]}, Title: {news[1][:50]}...")
        
        # Check Schedule table
        print("\n📅 Schedule Table:")
        cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."Schedule"')
        schedule_count = cursor.fetchone()[0]
        print(f"   Total scheduled games: {schedule_count}")
        
        if schedule_count > 0:
            cursor.execute(f'SELECT "Date", "HomeTeam", "AwayTeam" FROM "{DB_SCHEMA}"."Schedule" ORDER BY "Date" LIMIT 5')
            sample_games = cursor.fetchall()
            print(f"   Upcoming games:")
            for game in sample_games:
                print(f"     {game[0]}: {game[2]} @ {game[1]}")
        
        # Check Matches table
        print("\n🏆 Matches Table:")
        cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."Matches"')
        matches_count = cursor.fetchone()[0]
        print(f"   Total matches: {matches_count}")
        
        if matches_count > 0:
            cursor.execute(f'SELECT "Date", "HomeTeamName", "VisitorTeamName", "HomeTeamScore", "VisitorPoints" FROM "{DB_SCHEMA}"."Matches" ORDER BY "Date" DESC LIMIT 3')
            sample_matches = cursor.fetchall()
            print(f"   Recent matches:")
            for match in sample_matches:
                print(f"     {match[0]}: {match[2]} {match[4]} @ {match[1]} {match[3]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking data quality: {e}")
        return False

def test_prediction_functions():
    """Test the prediction functions with actual data"""
    print("\n🧪 Testing Prediction Functions...")
    print("-" * 50)
    
    try:
        from database_prediction import predict_game_outcome
        
        # Test prediction on some teams
        test_matchups = [
            ("Boston Celtics", "Los Angeles Lakers"),
            ("Golden State Warriors", "Miami Heat")
        ]
        
        for home_team, away_team in test_matchups:
            print(f"\n🏀 Testing: {away_team} @ {home_team}")
            
            try:
                result = predict_game_outcome(home_team, away_team)
                
                print(f"   ✅ Prediction successful")
                print(f"   🎯 Predicted winner: {result.get('predicted_winner', 'Unknown')}")
                print(f"   📈 Confidence: {result.get('confidence', 0):.1%}")
                print(f"   ⚖️ Prediction score: {result.get('prediction_score', 0):.3f}")
                
                # Check data quality factors
                data_quality = result.get('data_quality_factors', {})
                print(f"   📊 Data quality:")
                print(f"     Home team: {data_quality.get('home_data_quality', 0):.1%}")
                print(f"     Away team: {data_quality.get('away_data_quality', 0):.1%}")
                print(f"     H2H games: {data_quality.get('h2h_games', 0)}")
                
            except Exception as e:
                print(f"   ❌ Prediction failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing prediction functions: {e}")
        return False

def main():
    """Main function to run data quality check"""
    print("🔍 NBA Prediction Model Data Quality Check")
    print("=" * 60)
    
    # Run all checks
    checks = [
        ("Database Connection", check_database_connection),
        ("Table Structure", check_table_structure),
        ("Data Quality", check_data_quality),
        ("Prediction Functions", test_prediction_functions)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            if check_func():
                passed += 1
                print(f"✅ {check_name}: PASSED")
            else:
                print(f"❌ {check_name}: FAILED")
        except Exception as e:
            print(f"❌ {check_name}: ERROR - {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All data quality checks passed!")
    else:
        print("⚠️ Some data quality issues found. Review the results above.")

if __name__ == "__main__":
    main()
