import requests
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import json
import logging

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

def connect_to_database():
    """Connect to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

def create_schedule_table():
    """Create the NBA schedule table if it doesn't exist"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create schedule table
        create_table_query = f'''
        CREATE TABLE IF NOT EXISTS "{DB_SCHEMA}"."Schedule" (
            "GameID" SERIAL PRIMARY KEY,
            "Date" DATE NOT NULL,
            "Time" TIME,
            "HomeTeam" VARCHAR(100) NOT NULL,
            "AwayTeam" VARCHAR(100) NOT NULL,
            "HomeTeamID" VARCHAR(10),
            "AwayTeamID" VARCHAR(10),
            "Season" VARCHAR(10) NOT NULL,
            "SeasonType" VARCHAR(20) DEFAULT 'Regular Season',
            "Status" VARCHAR(20) DEFAULT 'Scheduled',
            "HomeScore" INTEGER,
            "AwayScore" INTEGER,
            "Venue" VARCHAR(200),
            "City" VARCHAR(100),
            "State" VARCHAR(50),
            "CreatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''
        
        cursor.execute(create_table_query)
        conn.commit()
        
        # Create index for faster queries
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_schedule_date ON "{DB_SCHEMA}"."Schedule" ("Date");')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_schedule_teams ON "{DB_SCHEMA}"."Schedule" ("HomeTeam", "AwayTeam");')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Schedule table created successfully!")
        return True
        
    except Exception as e:
        logging.error(f"Failed to create schedule table: {e}")
        conn.close()
        return False

def generate_2025_2026_schedule():
    """Generate a realistic NBA schedule for 2025-2026 season"""
    
    # NBA teams
    teams = [
        'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
        'Chicago Bulls', 'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets',
        'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
        'Los Angeles Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat',
        'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
        'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns',
        'Portland Trail Blazers', 'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors',
        'Utah Jazz', 'Washington Wizards'
    ]
    
    # Season dates (approximate)
    season_start = datetime(2025, 10, 21)  # Regular season start
    season_end = datetime(2026, 4, 13)     # Regular season end
    
    # Generate schedule
    schedule_data = []
    game_id = 1
    
    # Create a more realistic schedule with proper home/away distribution
    current_date = season_start
    team_games = {team: {'home': 0, 'away': 0, 'total': 0} for team in teams}
    
    while current_date <= season_end:
        # Skip some days (not every day has games)
        if current_date.weekday() < 5:  # Weekdays
            if current_date.day % 3 != 0:  # Not every weekday
                current_date += timedelta(days=1)
                continue
        else:  # Weekends
            if current_date.day % 2 != 0:  # Not every weekend day
                current_date += timedelta(days=1)
                continue
        
        # Generate 5-8 games per day
        games_per_day = 6 if current_date.weekday() >= 5 else 5
        
        # Select teams for today's games
        available_teams = [team for team in teams if team_games[team]['total'] < 82]
        
        if len(available_teams) < 2:
            break
            
        # Shuffle teams for variety
        import random
        random.seed(42)  # For reproducible results
        random.shuffle(available_teams)
        
        games_today = []
        for i in range(0, min(games_per_day * 2, len(available_teams)), 2):
            if i + 1 < len(available_teams):
                home_team = available_teams[i]
                away_team = available_teams[i + 1]
                
                # Check if teams haven't played too many games
                if (team_games[home_team]['total'] < 82 and 
                    team_games[away_team]['total'] < 82 and
                    team_games[home_team]['home'] < 41 and
                    team_games[away_team]['away'] < 41):
                    
                    games_today.append((home_team, away_team))
                    team_games[home_team]['home'] += 1
                    team_games[away_team]['away'] += 1
                    team_games[home_team]['total'] += 1
                    team_games[away_team]['total'] += 1
        
        # Add games to schedule
        for home_team, away_team in games_today:
            # Generate game time (evening games)
            game_time = f"{19 + (game_id % 3)}:00:00"  # 7-9 PM
            
            # Determine venue and city
            venue_info = get_team_venue(home_team)
            
            schedule_data.append({
                'GameID': game_id,
                'Date': current_date.strftime('%Y-%m-%d'),
                'Time': game_time,
                'HomeTeam': home_team,
                'AwayTeam': away_team,
                'HomeTeamID': get_team_id(home_team),
                'AwayTeamID': get_team_id(away_team),
                'Season': '2025-2026',
                'SeasonType': 'Regular Season',
                'Status': 'Scheduled',
                'HomeScore': None,
                'AwayScore': None,
                'Venue': venue_info['venue'],
                'City': venue_info['city'],
                'State': venue_info['state']
            })
            
            game_id += 1
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(schedule_data)

def get_team_venue(team_name):
    """Get venue information for a team"""
    venues = {
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
        'Los Angeles Clippers': {'venue': 'Crypto.com Arena', 'city': 'Los Angeles', 'state': 'CA'},
        'Los Angeles Lakers': {'venue': 'Crypto.com Arena', 'city': 'Los Angeles', 'state': 'CA'},
        'Memphis Grizzlies': {'venue': 'FedExForum', 'city': 'Memphis', 'state': 'TN'},
        'Miami Heat': {'venue': 'FTX Arena', 'city': 'Miami', 'state': 'FL'},
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
        'San Antonio Spurs': {'venue': 'AT&T Center', 'city': 'San Antonio', 'state': 'TX'},
        'Toronto Raptors': {'venue': 'Scotiabank Arena', 'city': 'Toronto', 'state': 'ON'},
        'Utah Jazz': {'venue': 'Vivint Arena', 'city': 'Salt Lake City', 'state': 'UT'},
        'Washington Wizards': {'venue': 'Capital One Arena', 'city': 'Washington', 'state': 'DC'}
    }
    
    return venues.get(team_name, {'venue': 'Unknown Arena', 'city': 'Unknown', 'state': 'Unknown'})

def get_team_id(team_name):
    """Get team ID for a team"""
    team_ids = {
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
    
    return team_ids.get(team_name, 'UNK')

def import_schedule_to_database(schedule_df):
    """Import schedule data to database"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Clear existing schedule data for 2025-2026
        cursor.execute(f'DELETE FROM "{DB_SCHEMA}"."Schedule" WHERE "Season" = %s', ('2025-2026',))
        
        # Insert new schedule data
        for _, row in schedule_df.iterrows():
            insert_query = f'''
            INSERT INTO "{DB_SCHEMA}"."Schedule" 
            ("Date", "Time", "HomeTeam", "AwayTeam", "HomeTeamID", "AwayTeamID", 
             "Season", "SeasonType", "Status", "Venue", "City", "State")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            
            cursor.execute(insert_query, (
                row['Date'], row['Time'], row['HomeTeam'], row['AwayTeam'],
                row['HomeTeamID'], row['AwayTeamID'], row['Season'], row['SeasonType'],
                row['Status'], row['Venue'], row['City'], row['State']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Successfully imported {len(schedule_df)} games to database!")
        return True
        
    except Exception as e:
        logging.error(f"Failed to import schedule: {e}")
        conn.close()
        return False

def get_upcoming_games(limit=50):
    """Get upcoming games from the schedule"""
    conn = connect_to_database()
    if not conn:
        return []
    
    try:
        query = f'''
        SELECT "GameID", "Date", "Time", "HomeTeam", "AwayTeam", "Venue", "City", "State"
        FROM "{DB_SCHEMA}"."Schedule"
        WHERE "Date" >= CURRENT_DATE
        AND "Status" = 'Scheduled'
        ORDER BY "Date", "Time"
        LIMIT %s
        '''
        
        df = pd.read_sql_query(query, conn, params=[limit])
        conn.close()
        
        return df.to_dict('records')
        
    except Exception as e:
        logging.error(f"Error fetching upcoming games: {e}")
        conn.close()
        return []

def get_games_by_date_range(start_date, end_date):
    """Get games within a date range"""
    conn = connect_to_database()
    if not conn:
        return []
    
    try:
        query = f'''
        SELECT "GameID", "Date", "Time", "HomeTeam", "AwayTeam", "Venue", "City", "State"
        FROM "{DB_SCHEMA}"."Schedule"
        WHERE "Date" BETWEEN %s AND %s
        ORDER BY "Date", "Time"
        '''
        
        df = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        
        return df.to_dict('records')
        
    except Exception as e:
        logging.error(f"Error fetching games by date range: {e}")
        conn.close()
        return []

def main():
    """Main function to import NBA schedule"""
    print("🏀 NBA Schedule Importer for 2025-2026 Season")
    print("=" * 50)
    
    # Create schedule table
    print("Creating schedule table...")
    if not create_schedule_table():
        print("❌ Failed to create schedule table")
        return
    
    # Generate schedule
    print("Generating 2025-2026 schedule...")
    schedule_df = generate_2025_2026_schedule()
    print(f"Generated {len(schedule_df)} games")
    
    # Import to database
    print("Importing schedule to database...")
    if import_schedule_to_database(schedule_df):
        print("✅ Schedule import completed successfully!")
        
        # Show some sample games
        print("\n📅 Sample upcoming games:")
        upcoming = get_upcoming_games(10)
        for game in upcoming[:5]:
            print(f"  {game['Date']} - {game['AwayTeam']} @ {game['HomeTeam']} ({game['Venue']})")
    else:
        print("❌ Schedule import failed")

if __name__ == "__main__":
    main()
