#!/usr/bin/env python3
"""
Import Real NBA 2025-26 Season Schedule
Scrapes full schedule from Basketball-Reference.com
"""

import psycopg2
from datetime import datetime
import logging
import requests
from bs4 import BeautifulSoup
import re
import time
import sys

DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Team venue mapping
TEAM_VENUES = {
    'Atlanta Hawks': {'venue': 'State Farm Arena', 'city': 'Atlanta', 'state': 'GA'},
    'Boston Celtics': {'venue': 'TD Garden', 'city': 'Boston', 'state': 'MA'},
    'Brooklyn Nets': {'venue': 'Barclays Center', 'city': 'Brooklyn', 'state': 'NY'},
    'Charlotte Hornets': {'venue': 'Spectrum Center', 'city': 'Charlotte', 'state': 'NC'},
    'Chicago Bulls': {'venue': 'United Center', 'city': 'Chicago', 'state': 'IL'},
    'Cleveland Cavaliers': {'venue': 'Rocket Mortgage FieldHouse', 'city': 'Cleveland', 'state': 'OH'},
    'Dallas Mavericks': {'venue': 'American Airlines Center', 'city': 'Dallas', 'state': 'TX'},
    'Denver Nuggets': {'venue': 'Ball Arena', 'city': 'Denver', 'state': 'CO'},
    'Detroit Pistons': {'venue': 'Little Caesars Arena', 'city': 'Detroit', 'state': 'MI'},
    'Golden State Warriors': {'venue': 'Chase Center', 'city': 'San Francisco', 'state': 'CA'},
    'Houston Rockets': {'venue': 'Toyota Center', 'city': 'Houston', 'state': 'TX'},
    'Indiana Pacers': {'venue': 'Gainbridge Fieldhouse', 'city': 'Indianapolis', 'state': 'IN'},
    'Los Angeles Clippers': {'venue': 'Intuit Dome', 'city': 'Inglewood', 'state': 'CA'},
    'Los Angeles Lakers': {'venue': 'Crypto.com Arena', 'city': 'Los Angeles', 'state': 'CA'},
    'Memphis Grizzlies': {'venue': 'FedExForum', 'city': 'Memphis', 'state': 'TN'},
    'Miami Heat': {'venue': 'Kaseya Center', 'city': 'Miami', 'state': 'FL'},
    'Milwaukee Bucks': {'venue': 'Fiserv Forum', 'city': 'Milwaukee', 'state': 'WI'},
    'Minnesota Timberwolves': {'venue': 'Target Center', 'city': 'Minneapolis', 'state': 'MN'},
    'New Orleans Pelicans': {'venue': 'Smoothie King Center', 'city': 'New Orleans', 'state': 'LA'},
    'New York Knicks': {'venue': 'Madison Square Garden', 'city': 'New York', 'state': 'NY'},
    'Oklahoma City Thunder': {'venue': 'Paycom Center', 'city': 'Oklahoma City', 'state': 'OK'},
    'Orlando Magic': {'venue': 'Amway Center', 'city': 'Orlando', 'state': 'FL'},
    'Philadelphia 76ers': {'venue': 'Wells Fargo Center', 'city': 'Philadelphia', 'state': 'PA'},
    'Phoenix Suns': {'venue': 'Footprint Center', 'city': 'Phoenix', 'state': 'AZ'},
    'Portland Trail Blazers': {'venue': 'Moda Center', 'city': 'Portland', 'state': 'OR'},
    'Sacramento Kings': {'venue': 'Golden 1 Center', 'city': 'Sacramento', 'state': 'CA'},
    'San Antonio Spurs': {'venue': 'Frost Bank Center', 'city': 'San Antonio', 'state': 'TX'},
    'Toronto Raptors': {'venue': 'Scotiabank Arena', 'city': 'Toronto', 'state': 'ON'},
    'Utah Jazz': {'venue': 'Delta Center', 'city': 'Salt Lake City', 'state': 'UT'},
    'Washington Wizards': {'venue': 'Capital One Arena', 'city': 'Washington', 'state': 'DC'}
}

TEAM_IDS = {
    'Atlanta Hawks': 'ATL', 'Boston Celtics': 'BOS', 'Brooklyn Nets': 'BKN',
    'Charlotte Hornets': 'CHA', 'Chicago Bulls': 'CHI', 'Cleveland Cavaliers': 'CLE',
    'Dallas Mavericks': 'DAL', 'Denver Nuggets': 'DEN', 'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW', 'Houston Rockets': 'HOU', 'Indiana Pacers': 'IND',
    'Los Angeles Clippers': 'LAC', 'Los Angeles Lakers': 'LAL', 'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA', 'Milwaukee Bucks': 'MIL', 'Minnesota Timberwolves': 'MIN',
    'New Orleans Pelicans': 'NOP', 'New York Knicks': 'NYK', 'Oklahoma City Thunder': 'OKC',
    'Orlando Magic': 'ORL', 'Philadelphia 76ers': 'PHI', 'Phoenix Suns': 'PHX',
    'Portland Trail Blazers': 'POR', 'Sacramento Kings': 'SAC', 'San Antonio Spurs': 'SAS',
    'Toronto Raptors': 'TOR', 'Utah Jazz': 'UTA', 'Washington Wizards': 'WAS'
}

MONTHS = [
    'october', 'november', 'december', 'january', 
    'february', 'march', 'april'
]

def connect_to_database():
    """Connect to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

def parse_time(time_str):
    """Parse time string like '7:30p' to '19:30:00'"""
    if not time_str:
        return None
    
    try:
        # Remove trailing p/a
        time_clean = time_str.lower().replace('p', ' PM').replace('a', ' AM')
        # Handle cases without p/a if any
        if 'M' not in time_clean:
            # Assume PM for NBA games unless explicit
            time_clean += ' PM'
            
        dt = datetime.strptime(time_clean, '%I:%M %p')
        return dt.strftime('%H:%M:%S')
    except Exception as e:
        logging.warning(f"Could not parse time: {time_str}")
        return '19:00:00' # Default

def scrape_month(month):
    """Scrape schedule for a specific month"""
    url = f"https://www.basketball-reference.com/leagues/NBA_2026_games-{month}.html"
    logging.info(f"Scraping {url}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.error(f"Failed to fetch {url}: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'schedule'})
        
        if not table:
            logging.warning(f"No schedule table found for {month}")
            return []
        
        games = []
        rows = table.find('tbody').find_all('tr')
        
        for row in rows:
            if 'class' in row.attrs and 'thead' in row.attrs['class']:
                continue
                
            cols = row.find_all(['th', 'td'])
            if not cols:
                continue
                
            # Date (header cell usually)
            date_col = row.find('th', {'data-stat': 'date_game'})
            start_col = row.find('td', {'data-stat': 'game_start_time'})
            visitor_col = row.find('td', {'data-stat': 'visitor_team_name'})
            home_col = row.find('td', {'data-stat': 'home_team_name'})
            arena_col = row.find('td', {'data-stat': 'arena_name'})
            
            if not (date_col and visitor_col and home_col):
                continue
                
            date_text = date_col.get_text()
            # Parse date: "Tue, Oct 21, 2025" -> "2025-10-21"
            try:
                game_date = datetime.strptime(date_text, '%a, %b %d, %Y').strftime('%Y-%m-%d')
            except ValueError:
                logging.warning(f"Could not parse date: {date_text}")
                continue
            
            time_text = start_col.get_text() if start_col else ''
            game_time = parse_time(time_text)
            
            visitor = visitor_col.get_text()
            home = home_col.get_text()
            
            # Use provided arena if available, else lookup
            arena = arena_col.get_text() if arena_col else ''
            
            games.append({
                'date': game_date,
                'time': game_time,
                'away': visitor,
                'home': home,
                'arena': arena
            })
            
        logging.info(f"Found {len(games)} games in {month}")
        time.sleep(1) # Be nice to the server
        return games
        
    except Exception as e:
        logging.error(f"Error scraping {month}: {e}")
        return []

def import_games(conn, games):
    """Import scraped games to database"""
    cursor = conn.cursor()
    imported = 0
    updated = 0
    
    for game in games:
        home_team = game['home']
        away_team = game['away']
        game_date = game['date']
        
        # Get venue info (prefer lookup for consistency but use scraped arena if needed)
        venue_info = TEAM_VENUES.get(home_team, {
            'venue': game['arena'] or 'Unknown Arena', 
            'city': 'Unknown', 
            'state': 'Unknown'
        })
        
        # Check if game exists
        cursor.execute(f'''
            SELECT "GameID" FROM "{DB_SCHEMA}"."Schedule"
            WHERE "Date" = %s AND "HomeTeam" = %s AND "AwayTeam" = %s
        ''', (game_date, home_team, away_team))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update
            cursor.execute(f'''
                UPDATE "{DB_SCHEMA}"."Schedule"
                SET "Time" = %s, "Venue" = %s, "Status" = 'Scheduled'
                WHERE "GameID" = %s
            ''', (game['time'], venue_info['venue'], existing[0]))
            updated += 1
        else:
            # Insert
            insert_query = f'''
                INSERT INTO "{DB_SCHEMA}"."Schedule" 
                ("Date", "Time", "HomeTeam", "AwayTeam", "HomeTeamID", "AwayTeamID", 
                 "Season", "SeasonType", "Status", "Venue", "City", "State")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            
            cursor.execute(insert_query, (
                game_date, game['time'], home_team, away_team,
                TEAM_IDS.get(home_team, 'UNK'), TEAM_IDS.get(away_team, 'UNK'),
                '2025-26', 'Regular Season', 'Scheduled',
                venue_info['venue'], venue_info['city'], venue_info['state']
            ))
            imported += 1
            
    conn.commit()
    cursor.close()
    return imported, updated

def main():
    print("Importing NBA 2025-26 Schedule from Basketball-Reference")
    print("=" * 60)
    
    conn = connect_to_database()
    if not conn:
        print("Failed to connect to database")
        return
        
    total_imported = 0
    total_updated = 0
    
    for month in MONTHS:
        games = scrape_month(month)
        if games:
            imported, updated = import_games(conn, games)
            total_imported += imported
            total_updated += updated
            print(f"  - {month.capitalize()}: {len(games)} found ({imported} new, {updated} updated)")
            
    print("\nSummary:")
    print(f"Total New Games Imported: {total_imported}")
    print(f"Total Games Updated: {total_updated}")
    
    conn.close()

if __name__ == "__main__":
    main()
