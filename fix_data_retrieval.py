#!/usr/bin/env python3
"""
Fix Data Retrieval Functions
Update functions to use correct table names and columns
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

def check_and_fix_data_retrieval():
    """Check what tables exist and fix data retrieval functions"""
    print("🔧 Fixing Data Retrieval Functions")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Database connected")
        
        cursor = conn.cursor()
        
        # Check what tables exist
        cursor.execute(f'''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = '{DB_SCHEMA}'
            ORDER BY table_name
        ''')
        
        tables = [table[0] for table in cursor.fetchall()]
        print(f"📊 Available tables: {tables}")
        
        # Check for games/results data
        games_table = None
        if 'Schedule' in tables:
            games_table = 'Schedule'
        elif 'Games' in tables:
            games_table = 'Games'
        elif 'Matches' in tables:
            games_table = 'Matches'
        
        print(f"🎮 Games table: {games_table}")
        
        # Check for news data
        news_table = None
        if 'News' in tables:
            news_table = 'News'
        elif 'TeamNews' in tables:
            news_table = 'TeamNews'
        
        print(f"📰 News table: {news_table}")
        
        # Check for team data
        teams_table = None
        if 'Teams' in tables:
            teams_table = 'Teams'
        elif 'TeamStats' in tables:
            teams_table = 'TeamStats'
        
        print(f"🏀 Teams table: {teams_table}")
        
        # Test data retrieval for a sample team
        test_team = "Boston Celtics"
        print(f"\n🧪 Testing data retrieval for {test_team}:")
        
        # Test team stats
        if teams_table:
            try:
                cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."{teams_table}" WHERE "TeamName" = %s LIMIT 1', (test_team,))
                team_data = cursor.fetchone()
                if team_data:
                    print(f"   ✅ Team stats found: {team_data}")
                else:
                    print(f"   ❌ No team stats found for {test_team}")
            except Exception as e:
                print(f"   ❌ Error getting team stats: {e}")
        
        # Test news data
        if news_table:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{news_table}" WHERE "Team" = %s', (test_team,))
                news_count = cursor.fetchone()[0]
                print(f"   📰 News articles for {test_team}: {news_count}")
                
                if news_count > 0:
                    cursor.execute(f'SELECT "Title", "Date" FROM "{DB_SCHEMA}"."{news_table}" WHERE "Team" = %s ORDER BY "Date" DESC LIMIT 3', (test_team,))
                    recent_news = cursor.fetchall()
                    print(f"   Recent news: {recent_news}")
            except Exception as e:
                print(f"   ❌ Error getting news: {e}")
        
        # Test games data
        if games_table:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."{games_table}" WHERE "HomeTeam" = %s OR "AwayTeam" = %s', (test_team, test_team))
                games_count = cursor.fetchone()[0]
                print(f"   🎮 Games for {test_team}: {games_count}")
                
                if games_count > 0:
                    cursor.execute(f'SELECT "Date", "HomeTeam", "AwayTeam" FROM "{DB_SCHEMA}"."{games_table}" WHERE "HomeTeam" = %s OR "AwayTeam" = %s ORDER BY "Date" DESC LIMIT 3', (test_team, test_team))
                    recent_games = cursor.fetchall()
                    print(f"   Recent games: {recent_games}")
            except Exception as e:
                print(f"   ❌ Error getting games: {e}")
        
        conn.close()
        
        # Generate updated functions based on what we found
        print(f"\n📝 Generating updated data retrieval functions...")
        generate_updated_functions(tables, games_table, news_table, teams_table)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def generate_updated_functions(tables, games_table, news_table, teams_table):
    """Generate updated data retrieval functions"""
    
    print(f"\n🔧 Updated Functions for your database:")
    print("=" * 50)
    
    # Updated get_team_stats function
    if teams_table:
        print(f"""
def get_team_stats(team_name):
    \"\"\"Get current team statistics\"\"\"
    conn = connect_to_database()
    if not conn:
        return None
    
    try:
        query = f'''
        SELECT "TeamName", "Wins", "Losses", "PointsFor", "PointsAgainst"
        FROM "{{DB_SCHEMA}}"."{teams_table}"
        WHERE "TeamName" = %s
        '''
        df = pd.read_sql_query(query, conn, params=[team_name])
        conn.close()
        
        if len(df) > 0:
            return df.iloc[0].to_dict()
        return None
    except Exception as e:
        logging.error(f"Error fetching team stats: {{e}}")
        return None
""")
    
    # Updated get_team_news function
    if news_table:
        print(f"""
def get_team_news(team_name, limit=15):
    \"\"\"Get recent news about a team\"\"\"
    conn = connect_to_database()
    if not conn:
        return []
    
    try:
        query = f'''
        SELECT "NewsID", "Title", "Content", "Date", "Team"
        FROM "{{DB_SCHEMA}}"."{news_table}"
        WHERE "Team" = %s
        ORDER BY "Date" DESC
        LIMIT %s
        '''
        df = pd.read_sql_query(query, conn, params=[team_name, limit])
        conn.close()
        return df.to_dict('records')
    except Exception as e:
        logging.error(f"Error fetching team news: {{e}}")
        return []
""")
    
    # Updated get_recent_matches function
    if games_table:
        print(f"""
def get_recent_matches(team_name, days=30):
    \"\"\"Get recent matches for a team\"\"\"
    conn = connect_to_database()
    if not conn:
        return pd.DataFrame()
    
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Check what columns exist in the games table
        query = f'''
        SELECT "Date", "HomeTeam", "AwayTeam"
        FROM "{{DB_SCHEMA}}"."{games_table}"
        WHERE ("HomeTeam" = %s OR "AwayTeam" = %s)
        AND "Date" >= %s
        ORDER BY "Date" DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=[team_name, team_name, cutoff_date])
        conn.close()
        return df
    except Exception as e:
        logging.error(f"Error fetching recent matches: {{e}}")
        return pd.DataFrame()
""")
    
    print(f"\n✅ Use these functions based on your actual database structure!")

if __name__ == "__main__":
    check_and_fix_data_retrieval()
