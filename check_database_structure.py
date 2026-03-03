#!/usr/bin/env python3
"""
Check Database Structure and Data Availability
Investigate what tables and data are actually available
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

def check_database_structure():
    """Check what tables exist and what data is available"""
    print("🔍 Checking Database Structure and Data")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Database connected")
        
        cursor = conn.cursor()
        
        # Get all tables in NBA schema
        cursor.execute(f'''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = '{DB_SCHEMA}'
            ORDER BY table_name
        ''')
        
        tables = cursor.fetchall()
        print(f"\n📊 Available Tables in {DB_SCHEMA} schema:")
        for table in tables:
            print(f"   • {table[0]}")
        
        # Check each table for data
        for table in tables:
            table_name = table[0]
            print(f"\n🔍 Checking {table_name}:")
            
            try:
                # Get row count
                cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{table_name}"')
                count = cursor.fetchone()[0]
                print(f"   Rows: {count}")
                
                if count > 0:
                    # Get column info
                    cursor.execute(f'''
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_schema = '{DB_SCHEMA}' 
                        AND table_name = '{table_name}'
                        ORDER BY ordinal_position
                    ''')
                    columns = cursor.fetchall()
                    print(f"   Columns: {[col[0] for col in columns]}")
                    
                    # Show sample data
                    cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."{table_name}" LIMIT 3')
                    sample_data = cursor.fetchall()
                    print(f"   Sample data:")
                    for i, row in enumerate(sample_data):
                        print(f"     Row {i+1}: {row}")
                else:
                    print("   ⚠️  No data found")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Specifically check for recent data
        print(f"\n📅 Checking for Recent Data:")
        
        # Check if there are any recent games
        try:
            cursor.execute(f'''
                SELECT COUNT(*) 
                FROM "{DB_SCHEMA}"."Schedule" 
                WHERE "Date" >= %s
            ''', ((datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),))
            recent_games = cursor.fetchone()[0]
            print(f"   Recent games (last 30 days): {recent_games}")
        except Exception as e:
            print(f"   ❌ Error checking recent games: {e}")
        
        # Check if there are any recent news
        try:
            cursor.execute(f'''
                SELECT COUNT(*) 
                FROM "{DB_SCHEMA}"."News" 
                WHERE "Date" >= %s
            ''', ((datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),))
            recent_news = cursor.fetchone()[0]
            print(f"   Recent news (last 30 days): {recent_news}")
        except Exception as e:
            print(f"   ❌ Error checking recent news: {e}")
        
        # Check team data
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."Teams"')
            team_count = cursor.fetchone()[0]
            print(f"   Teams: {team_count}")
            
            if team_count > 0:
                cursor.execute(f'SELECT "TeamName", "Wins", "Losses" FROM "{DB_SCHEMA}"."Teams" LIMIT 5')
                teams = cursor.fetchall()
                print(f"   Sample teams: {teams}")
        except Exception as e:
            print(f"   ❌ Error checking teams: {e}")
        
        conn.close()
        print(f"\n✅ Database structure check complete!")
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")

if __name__ == "__main__":
    check_database_structure()
