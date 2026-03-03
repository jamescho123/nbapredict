#!/usr/bin/env python3
"""
Import Real 2024-25 NBA Season Data from Basketball Reference
Fetches actual game schedules and results
"""

import psycopg2
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging
import re

DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BasketballReferenceImporter:
    
    def __init__(self):
        self.conn = None
        self.base_url = "https://www.basketball-reference.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.basketball-reference.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
    def connect_to_database(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            logging.info("Database connection successful")
            return True
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return False
    
    def create_tables(self):
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(f'DROP TABLE IF EXISTS "{DB_SCHEMA}"."Season2024_25_Schedule" CASCADE;')
            cursor.execute(f'DROP TABLE IF EXISTS "{DB_SCHEMA}"."Season2024_25_Results" CASCADE;')
            cursor.execute(f'DROP TABLE IF EXISTS "{DB_SCHEMA}"."Season2024_25_TeamStats" CASCADE;')
            
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
            
            cursor.execute(f'''
                CREATE TABLE "{DB_SCHEMA}"."Season2024_25_TeamStats" (
                    "TeamID" SERIAL PRIMARY KEY,
                    "TeamName" VARCHAR(50) NOT NULL,
                    "Wins" INTEGER NOT NULL,
                    "Losses" INTEGER NOT NULL,
                    "WinPercentage" DECIMAL(5,3) NOT NULL,
                    "PointsFor" INTEGER NOT NULL,
                    "PointsAgainst" INTEGER NOT NULL,
                    "PointDifferential" INTEGER NOT NULL,
                    "HomeWins" INTEGER NOT NULL,
                    "AwayWins" INTEGER NOT NULL,
                    "Conference" VARCHAR(10) NOT NULL,
                    "Division" VARCHAR(20) NOT NULL,
                    "Season" VARCHAR(10) DEFAULT '2024-25'
                );
            ''')
            
            self.conn.commit()
            logging.info("Tables created successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error creating tables: {e}")
            self.conn.rollback()
            return False
    
    def fetch_month_schedule(self, year, month):
        """Fetch schedule for a specific month"""
        url = f"{self.base_url}/leagues/NBA_{year}_games-{month.lower()}.html"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logging.error(f"Error fetching {month} {year}: {e}")
            return None
    
    def parse_games(self, html_content):
        """Parse game data from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        games = []
        
        schedule_table = soup.find('table', {'id': 'schedule'})
        if not schedule_table:
            return games
        
        rows = schedule_table.find('tbody').find_all('tr')
        
        for row in rows:
            if 'class' in row.attrs and 'thead' in row.attrs['class']:
                continue
                
            cols = row.find_all('td')
            if len(cols) < 6:
                continue
            
            try:
                date_link = row.find('th', {'data-stat': 'date_game'})
                if not date_link:
                    continue
                    
                date_str = date_link.get('csk', '')
                if not date_str:
                    continue
                
                game_date = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
                
                start_time = cols[0].text.strip() if len(cols) > 0 else ''
                visitor_team = cols[1].text.strip() if len(cols) > 1 else ''
                visitor_pts = cols[2].text.strip() if len(cols) > 2 else ''
                home_team = cols[3].text.strip() if len(cols) > 3 else ''
                home_pts = cols[4].text.strip() if len(cols) > 4 else ''
                
                if not visitor_team or not home_team:
                    continue
                
                game = {
                    'date': game_date,
                    'time': start_time,
                    'away_team': visitor_team,
                    'home_team': home_team,
                    'away_score': visitor_pts,
                    'home_score': home_pts
                }
                
                games.append(game)
                
            except Exception as e:
                logging.error(f"Error parsing row: {e}")
                continue
        
        return games
    
    def import_games(self):
        """Import all games from 2024-25 season"""
        print("Fetching 2024-25 NBA Season from Basketball Reference")
        print("=" * 60)
        
        months = ['october', 'november', 'december', 'january', 'february', 'march', 'april']
        all_games = []
        
        for month in months:
            print(f"Fetching {month.capitalize()} games...")
            html = self.fetch_month_schedule(2025, month)
            
            if html:
                games = self.parse_games(html)
                all_games.extend(games)
                print(f"   Found {len(games)} games")
                time.sleep(3)  # Increased delay to avoid rate limiting
            else:
                print(f"   WARNING: Could not fetch {month}")
        
        print(f"\nTotal games found: {len(all_games)}")
        
        if not all_games:
            print("ERROR: No games found. Please check the website or try again later.")
            return False
        
        cursor = self.conn.cursor()
        game_id = 1
        results_count = 0
        schedule_count = 0
        
        for game in all_games:
            try:
                date = game['date']
                time_str = game['time']
                away_team = game['away_team']
                home_team = game['home_team']
                away_score = game['away_score']
                home_score = game['home_score']
                
                cursor.execute(f'''
                    INSERT INTO "{DB_SCHEMA}"."Season2024_25_Schedule"
                    ("GameID", "Date", "Time", "HomeTeam", "AwayTeam", "Season", "SeasonType")
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (game_id, date, time_str, home_team, away_team, '2024-25', 'Regular Season'))
                schedule_count += 1
                
                if away_score and home_score and away_score.isdigit() and home_score.isdigit():
                    home_score_int = int(home_score)
                    away_score_int = int(away_score)
                    
                    winner = home_team if home_score_int > away_score_int else away_team
                    margin = abs(home_score_int - away_score_int)
                    total = home_score_int + away_score_int
                    overtime = 'OT' in str(game.get('notes', ''))
                    
                    cursor.execute(f'''
                        INSERT INTO "{DB_SCHEMA}"."Season2024_25_Results"
                        ("GameID", "Date", "HomeTeam", "AwayTeam", "HomeScore", "AwayScore", 
                         "Winner", "Margin", "TotalPoints", "Overtime", "Season", "SeasonType")
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (game_id, date, home_team, away_team, home_score_int, away_score_int,
                          winner, margin, total, overtime, '2024-25', 'Regular Season'))
                    results_count += 1
                
                game_id += 1
                
            except Exception as e:
                logging.error(f"Error importing game: {e}")
                continue
        
        self.conn.commit()
        
        print(f"\nImport Complete!")
        print(f"   Schedule: {schedule_count} games")
        print(f"   Results: {results_count} completed games")
        
        return True
    
    def run_import(self):
        """Run the complete import process"""
        if not self.connect_to_database():
            return False
        
        try:
            if not self.create_tables():
                return False
            
            if not self.import_games():
                return False
            
            print("\n2024-25 Season Data Import Complete!")
            return True
            
        except Exception as e:
            logging.error(f"Import process error: {e}")
            return False
        finally:
            if self.conn:
                self.conn.close()

def main():
    importer = BasketballReferenceImporter()
    success = importer.run_import()
    
    if success:
        print("\nReal 2024-25 season data ready for backtesting!")
    else:
        print("\nImport failed. Check the logs for details.")

if __name__ == "__main__":
    main()

