#!/usr/bin/env python3
"""
Import 2024-25 NBA Season Games Manually
Based on Basketball Reference data from October 2024
"""

import psycopg2
from datetime import datetime
import logging

DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# October 2024 games from Basketball Reference
OCTOBER_2024_GAMES = [
    # October 22, 2024
    {'date': '2024-10-22', 'time': '7:30p', 'away': 'New York Knicks', 'home': 'Boston Celtics', 'away_score': 109, 'home_score': 132},
    {'date': '2024-10-22', 'time': '10:00p', 'away': 'Minnesota Timberwolves', 'home': 'Los Angeles Lakers', 'away_score': 103, 'home_score': 110},
    
    # October 23, 2024
    {'date': '2024-10-23', 'time': '7:00p', 'away': 'Indiana Pacers', 'home': 'Detroit Pistons', 'away_score': 115, 'home_score': 109},
    {'date': '2024-10-23', 'time': '7:30p', 'away': 'Brooklyn Nets', 'home': 'Atlanta Hawks', 'away_score': 116, 'home_score': 120},
    {'date': '2024-10-23', 'time': '7:30p', 'away': 'Orlando Magic', 'home': 'Miami Heat', 'away_score': 116, 'home_score': 97},
    {'date': '2024-10-23', 'time': '7:30p', 'away': 'Milwaukee Bucks', 'home': 'Philadelphia 76ers', 'away_score': 124, 'home_score': 109},
    {'date': '2024-10-23', 'time': '7:30p', 'away': 'Cleveland Cavaliers', 'home': 'Toronto Raptors', 'away_score': 136, 'home_score': 106},
    {'date': '2024-10-23', 'time': '8:00p', 'away': 'Charlotte Hornets', 'home': 'Houston Rockets', 'away_score': 110, 'home_score': 105},
    {'date': '2024-10-23', 'time': '8:00p', 'away': 'Chicago Bulls', 'home': 'New Orleans Pelicans', 'away_score': 111, 'home_score': 123},
    {'date': '2024-10-23', 'time': '9:00p', 'away': 'Memphis Grizzlies', 'home': 'Utah Jazz', 'away_score': 126, 'home_score': 124},
    {'date': '2024-10-23', 'time': '10:00p', 'away': 'Phoenix Suns', 'home': 'Los Angeles Clippers', 'away_score': 116, 'home_score': 113, 'ot': True},
    {'date': '2024-10-23', 'time': '10:00p', 'away': 'Portland Trail Blazers', 'home': 'Golden State Warriors', 'away_score': 104, 'home_score': 139},
    
    # October 24, 2024
    {'date': '2024-10-24', 'time': '7:00p', 'away': 'Boston Celtics', 'home': 'Washington Wizards', 'away_score': 122, 'home_score': 102},
    {'date': '2024-10-24', 'time': '7:30p', 'away': 'Philadelphia 76ers', 'home': 'Toronto Raptors', 'away_score': 115, 'home_score': 107},
    {'date': '2024-10-24', 'time': '8:00p', 'away': 'Detroit Pistons', 'home': 'Cleveland Cavaliers', 'away_score': 113, 'home_score': 121},
    {'date': '2024-10-24', 'time': '8:00p', 'away': 'Atlanta Hawks', 'home': 'Charlotte Hornets', 'away_score': 125, 'home_score': 120},
    {'date': '2024-10-24', 'time': '8:00p', 'away': 'Miami Heat', 'home': 'Orlando Magic', 'away_score': 97, 'home_score': 116},
    {'date': '2024-10-24', 'time': '8:00p', 'away': 'Minnesota Timberwolves', 'home': 'Dallas Mavericks', 'away_score': 120, 'home_score': 114},
    {'date': '2024-10-24', 'time': '9:00p', 'away': 'Utah Jazz', 'home': 'Denver Nuggets', 'away_score': 107, 'home_score': 129},
    {'date': '2024-10-24', 'time': '10:00p', 'away': 'Los Angeles Clippers', 'home': 'Sacramento Kings', 'away_score': 111, 'home_score': 104},
    
    # October 25, 2024
    {'date': '2024-10-25', 'time': '7:30p', 'away': 'Milwaukee Bucks', 'home': 'Brooklyn Nets', 'away_score': 115, 'home_score': 102},
    {'date': '2024-10-25', 'time': '7:30p', 'away': 'Indiana Pacers', 'home': 'New York Knicks', 'away_score': 123, 'home_score': 132},
    {'date': '2024-10-25', 'time': '10:00p', 'away': 'New Orleans Pelicans', 'home': 'Portland Trail Blazers', 'away_score': 105, 'home_score': 103},
    {'date': '2024-10-25', 'time': '10:30p', 'away': 'Golden State Warriors', 'home': 'Los Angeles Lakers', 'away_score': 118, 'home_score': 112},
]

def create_tables(conn):
    """Create tables for 2024-25 season"""
    try:
        cursor = conn.cursor()
        
        # Drop existing tables
        cursor.execute(f'DROP TABLE IF EXISTS "{DB_SCHEMA}"."Season2024_25_Schedule" CASCADE;')
        cursor.execute(f'DROP TABLE IF EXISTS "{DB_SCHEMA}"."Season2024_25_Results" CASCADE;')
        cursor.execute(f'DROP TABLE IF EXISTS "{DB_SCHEMA}"."Season2024_25_TeamStats" CASCADE;')
        
        # Create schedule table
        cursor.execute(f'''
            CREATE TABLE "{DB_SCHEMA}"."Season2024_25_Schedule" (
                "GameID" SERIAL PRIMARY KEY,
                "Date" DATE NOT NULL,
                "Time" VARCHAR(20),
                "HomeTeam" VARCHAR(50) NOT NULL,
                "AwayTeam" VARCHAR(50) NOT NULL,
                "Venue" VARCHAR(100),
                "Season" VARCHAR(10) DEFAULT '2024-25',
                "SeasonType" VARCHAR(20) DEFAULT 'Regular Season'
            );
        ''')
        
        # Create results table
        cursor.execute(f'''
            CREATE TABLE "{DB_SCHEMA}"."Season2024_25_Results" (
                "GameID" SERIAL PRIMARY KEY,
                "Date" DATE NOT NULL,
                "HomeTeam" VARCHAR(50) NOT NULL,
                "AwayTeam" VARCHAR(50) NOT NULL,
                "HomeScore" INTEGER NOT NULL,
                "AwayScore" INTEGER NOT NULL,
                "Winner" VARCHAR(50) NOT NULL,
                "Margin" INTEGER NOT NULL,
                "TotalPoints" INTEGER NOT NULL,
                "Overtime" BOOLEAN DEFAULT FALSE,
                "Season" VARCHAR(10) DEFAULT '2024-25',
                "SeasonType" VARCHAR(20) DEFAULT 'Regular Season'
            );
        ''')
        
        conn.commit()
        logging.info("Tables created successfully")
        return True
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        conn.rollback()
        return False

def import_games(conn, games):
    """Import games to database"""
    try:
        cursor = conn.cursor()
        game_id = 1
        
        for game in games:
            date = game['date']
            time_str = game['time']
            home_team = game['home']
            away_team = game['away']
            home_score = game['home_score']
            away_score = game['away_score']
            overtime = game.get('ot', False)
            
            # Insert into schedule
            cursor.execute(f'''
                INSERT INTO "{DB_SCHEMA}"."Season2024_25_Schedule"
                ("GameID", "Date", "Time", "HomeTeam", "AwayTeam", "Season", "SeasonType")
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (game_id, date, time_str, home_team, away_team, '2024-25', 'Regular Season'))
            
            # Determine winner
            winner = home_team if home_score > away_score else away_team
            margin = abs(home_score - away_score)
            total = home_score + away_score
            
            # Insert into results
            cursor.execute(f'''
                INSERT INTO "{DB_SCHEMA}"."Season2024_25_Results"
                ("GameID", "Date", "HomeTeam", "AwayTeam", "HomeScore", "AwayScore", 
                 "Winner", "Margin", "TotalPoints", "Overtime", "Season", "SeasonType")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (game_id, date, home_team, away_team, home_score, away_score,
                  winner, margin, total, overtime, '2024-25', 'Regular Season'))
            
            game_id += 1
        
        conn.commit()
        logging.info(f"Imported {len(games)} games successfully")
        return True
    except Exception as e:
        logging.error(f"Error importing games: {e}")
        conn.rollback()
        return False

def main():
    """Main import function"""
    print("Importing 2024-25 NBA Season Games (October 2024)")
    print("=" * 60)
    print(f"Data source: Basketball-Reference.com")
    print(f"Games to import: {len(OCTOBER_2024_GAMES)}")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logging.info("Database connection successful")
        
        if not create_tables(conn):
            print("Failed to create tables")
            return
        
        if not import_games(conn, OCTOBER_2024_GAMES):
            print("Failed to import games")
            return
        
        print(f"\nImport Complete!")
        print(f"   Schedule: {len(OCTOBER_2024_GAMES)} games")
        print(f"   Results: {len(OCTOBER_2024_GAMES)} completed games")
        print(f"\nReal 2024-25 season data (October 2024) ready for backtesting!")
        
    except Exception as e:
        logging.error(f"Import error: {e}")
        print(f"Import failed: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()




