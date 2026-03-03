#!/usr/bin/env python3
"""
Regenerate complete NBA 2025-26 Schedule
Generate a more complete schedule with ~82 games per team
"""

import psycopg2
from datetime import datetime, timedelta
import random
import logging

DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# NBA teams
TEAMS = [
    'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
    'Chicago Bulls', 'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets',
    'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
    'Los Angeles Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat',
    'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
    'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns',
    'Portland Trail Blazers', 'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors',
    'Utah Jazz', 'Washington Wizards'
]

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

def connect_to_database():
    """Connect to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

def generate_complete_schedule():
    """Generate a more complete NBA schedule"""
    
    # Season dates
    season_start = datetime(2025, 10, 21)
    season_end = datetime(2026, 4, 12)
    
    # Initialize team game counters
    team_games = {team: {'home': 0, 'away': 0, 'total': 0, 'last_game': None} for team in TEAMS}
    
    schedule = []
    game_id = 1
    
    # Iterate through each day of the season
    current_date = season_start
    
    while current_date <= season_end:
        # Determine if this is a game day
        # NBA typically has games most days except:
        # - Some Mondays and Tuesdays
        # - Christmas Eve (but Christmas Day is big)
        # - All-Star break (mid-February)
        
        weekday = current_date.weekday()  # 0=Monday, 6=Sunday
        
        # Skip some days
        if current_date.month == 2 and 13 <= current_date.day <= 19:
            # All-Star break
            current_date += timedelta(days=1)
            continue
        
        # More games on Wed-Sun, fewer on Mon-Tue
        if weekday == 0:  # Monday - 40% chance of games
            if random.random() > 0.4:
                current_date += timedelta(days=1)
                continue
        elif weekday == 1:  # Tuesday - 60% chance of games
            if random.random() > 0.6:
                current_date += timedelta(days=1)
                continue
        
        # Determine number of games for this day
        if weekday >= 5:  # Weekend
            games_today = random.randint(8, 13)
        elif weekday == 4:  # Friday
            games_today = random.randint(8, 12)
        else:  # Weekday
            games_today = random.randint(5, 10)
        
        # Get available teams (haven't reached 82 games yet and not playing back-to-back)
        available_teams = []
        for team in TEAMS:
            if team_games[team]['total'] >= 82:
                continue
            # Check if team played yesterday (avoid back-to-back-to-back)
            if team_games[team]['last_game'] and (current_date - team_games[team]['last_game']).days < 1:
                continue
            available_teams.append(team)
        
        if len(available_teams) < 2:
            current_date += timedelta(days=1)
            continue
        
        # Shuffle to randomize matchups
        random.shuffle(available_teams)
        
        # Create games for today
        games_scheduled = 0
        for i in range(0, len(available_teams) - 1, 2):
            if games_scheduled >= games_today:
                break
            
            home_team = available_teams[i]
            away_team = available_teams[i + 1]
            
            # Check if both teams can still play home/away games
            if team_games[home_team]['home'] >= 41:
                # Home team maxed out, swap
                home_team, away_team = away_team, home_team
            
            if team_games[home_team]['home'] >= 41:
                # Both maxed out on home games, skip
                continue
            
            if team_games[away_team]['away'] >= 41:
                # Away team maxed out on away games, skip
                continue
            
            # Schedule the game
            venue_info = TEAM_VENUES[home_team]
            
            # Vary game times
            if games_scheduled < 2:
                game_time = '19:00'
            elif games_scheduled < 4:
                game_time = '19:30'
            elif games_scheduled < 7:
                game_time = '20:00'
            elif games_scheduled < 9:
                game_time = '21:00'
            else:
                game_time = '22:00'
            
            schedule.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'time': game_time,
                'home': home_team,
                'away': away_team,
                'venue': venue_info['venue'],
                'city': venue_info['city'],
                'state': venue_info['state']
            })
            
            # Update counters
            team_games[home_team]['home'] += 1
            team_games[home_team]['total'] += 1
            team_games[home_team]['last_game'] = current_date
            
            team_games[away_team]['away'] += 1
            team_games[away_team]['total'] += 1
            team_games[away_team]['last_game'] = current_date
            
            games_scheduled += 1
            game_id += 1
        
        current_date += timedelta(days=1)
    
    logging.info(f"Generated {len(schedule)} games")
    logging.info("Games per team:")
    for team in sorted(TEAMS):
        logging.info(f"  {team}: {team_games[team]['total']} games ({team_games[team]['home']} home, {team_games[team]['away']} away)")
    
    return schedule

def delete_generated_games(conn):
    """Delete previously generated games (keep the real Nov 5-7 games)"""
    cursor = conn.cursor()
    
    # Delete games from Nov 8 onwards
    cursor.execute(f'''
        DELETE FROM "{DB_SCHEMA}"."Schedule"
        WHERE "Date" > '2025-11-07'
        AND "Season" = '2025-26'
    ''')
    
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()
    
    logging.info(f"Deleted {deleted} generated games (keeping Nov 5-7)")
    return deleted

def import_schedule(conn, schedule_data):
    """Import schedule to database"""
    cursor = conn.cursor()
    
    imported = 0
    
    for game in schedule_data:
        # Skip Nov 5-7 (already have real data)
        game_date = datetime.strptime(game['date'], '%Y-%m-%d')
        if datetime(2025, 11, 5) <= game_date <= datetime(2025, 11, 7):
            continue
        
        insert_query = f'''
            INSERT INTO "{DB_SCHEMA}"."Schedule" 
            ("Date", "Time", "HomeTeam", "AwayTeam", "HomeTeamID", "AwayTeamID", 
             "Season", "SeasonType", "Status", "Venue", "City", "State")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        
        cursor.execute(insert_query, (
            game['date'], game['time'], game['home'], game['away'],
            TEAM_IDS[game['home']], TEAM_IDS[game['away']],
            '2025-26', 'Regular Season', 'Scheduled',
            game['venue'], game['city'], game['state']
        ))
        
        imported += 1
        
        if imported % 100 == 0:
            logging.info(f"Imported {imported} games...")
    
    conn.commit()
    cursor.close()
    
    logging.info(f"Imported {imported} games total")
    return imported

def verify_schedule(conn):
    """Verify the complete schedule"""
    cursor = conn.cursor()
    
    # Overall stats
    cursor.execute(f'''
        SELECT MIN("Date"), MAX("Date"), COUNT(*) 
        FROM "{DB_SCHEMA}"."Schedule" 
        WHERE "Season" = '2025-26'
    ''')
    result = cursor.fetchone()
    print(f"\n2025-26 Season Schedule:")
    print(f"  Start: {result[0]}")
    print(f"  End: {result[1]}")
    print(f"  Total games: {result[2]}")
    
    # Games per team
    cursor.execute(f'''
        SELECT t.team, t.home_games, a.away_games, (t.home_games + a.away_games) as total
        FROM (
            SELECT "HomeTeam" as team, COUNT(*) as home_games
            FROM "{DB_SCHEMA}"."Schedule"
            WHERE "Season" = '2025-26'
            GROUP BY "HomeTeam"
        ) t
        JOIN (
            SELECT "AwayTeam" as team, COUNT(*) as away_games
            FROM "{DB_SCHEMA}"."Schedule"
            WHERE "Season" = '2025-26'
            GROUP BY "AwayTeam"
        ) a ON t.team = a.team
        ORDER BY total DESC
    ''')
    
    teams = cursor.fetchall()
    print(f"\nGames per team (showing all):")
    for team, home, away, total in teams:
        print(f"  {team}: {total} games ({home} home, {away} away)")
    
    cursor.close()

def main():
    """Main function"""
    print("Regenerating Complete NBA 2025-26 Schedule")
    print("=" * 50)
    
    conn = connect_to_database()
    if not conn:
        print("Failed to connect to database")
        return
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Delete old generated games
    print("\n1. Deleting old generated games...")
    delete_generated_games(conn)
    
    # Generate new schedule
    print("\n2. Generating complete schedule...")
    schedule = generate_complete_schedule()
    
    # Import schedule
    print("\n3. Importing schedule to database...")
    import_schedule(conn, schedule)
    
    # Verify
    print("\n4. Verifying schedule...")
    verify_schedule(conn)
    
    conn.close()
    
    print(f"\nSchedule regeneration completed!")

if __name__ == "__main__":
    main()

