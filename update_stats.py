"""
NBA Stats Updater
Fetches latest game results from Basketball Reference and updates the database.
"""

import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from db_config import get_connection, DB_SCHEMA

def get_current_season_year():
    """
    Get the current NBA season year (ending year).
    E.g. Oct 2023 -> 2024 season. Jan 2024 -> 2024 season.
    """
    now = datetime.now()
    # NBA season typically starts in October
    if now.month >= 10:
        return now.year + 1
    return now.year

def get_current_month_name():
    """Get full month name in lowercase, e.g. 'january'"""
    return datetime.now().strftime('%B').lower()

def get_months_to_update():
    """
    Get list of months to update: current month and previous month 
    (to ensure we catch late-reported games or corrections)
    """
    now = datetime.now()
    months = []
    
    # Current month
    months.append(now.strftime('%B').lower())
    
    # Previous month
    prev_month = now.replace(day=1) - timedelta(days=1)
    # Only include previous month if it's part of the current season (Oct onwards)
    if prev_month.month >= 10 or prev_month.year == now.year:
        months.append(prev_month.strftime('%B').lower())
        
    return list(set(months)) # Deduplicate

def get_team_map(cur):
    """Get mapping of team name (lower) to TeamID"""
    try:
        cur.execute(f'SELECT "TeamID", "TeamName" FROM "{DB_SCHEMA}"."Teams"')
        teams = cur.fetchall()
        return {name.lower(): tid for tid, name in teams}
    except Exception as e:
        print(f"Error fetching teams: {e}")
        return {}

def update_todays_stats():
    """Main function to update stats"""
    print(f"Starting NBA Stats Update...")
    
    conn = get_connection()
    if not conn:
        print("Database connection failed.")
        return False
        
    try:
        cur = conn.cursor()
        team_map = get_team_map(cur)
        if not team_map:
            print("No teams found in database. Please populate Teams table first.")
            return False
            
        season = get_current_season_year()
        months = get_months_to_update()
        
        total_inserted = 0
        
        for month in months:
            url = f'https://www.basketball-reference.com/leagues/NBA_{season}_games-{month}.html'
            print(f"Fetching data for {month.capitalize()} {season} from: {url}")
            
            try:
                response = requests.get(url, timeout=15)
                if response.status_code != 200:
                    print(f"  Failed to fetch: {response.status_code}")
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table', id='schedule')
                if not table:
                    print(f"  No schedule table found.")
                    continue
                
                rows = table.find('tbody').find_all('tr')
                print(f"  Found {len(rows)} potential games.")
                
                for row in rows:
                    # Skip header rows (class 'thead') or empty rows
                    if row.get('class') == ['thead']:
                        continue
                        
                    cols = row.find_all('td')
                    if not cols or len(cols) < 4:
                        continue
                        
                    # Parse Date
                    date_th = row.find('th', {'data-stat': 'date_game'})
                    if not date_th: 
                        continue
                        
                    date_str = date_th.get_text(strip=True)
                    try:
                        game_date = pd.to_datetime(date_str).date()
                    except:
                        continue
                        
                    # Skip future games
                    if game_date > datetime.now().date():
                        continue
                        
                    # Parse Teams and Scores
                    visitor_team_name = cols[0].get_text(strip=True)
                    visitor_pts_str = cols[1].get_text(strip=True)
                    
                    home_team_name = cols[2].get_text(strip=True)
                    home_pts_str = cols[3].get_text(strip=True)
                    
                    # Check if game was played (has scores)
                    if not visitor_pts_str or not home_pts_str:
                        continue
                        
                    try:
                        visitor_pts = int(visitor_pts_str)
                        home_pts = int(home_pts_str)
                    except ValueError:
                        continue # Empty or invalid score
                        
                    # Map to IDs
                    visitor_id = team_map.get(visitor_team_name.lower())
                    home_id = team_map.get(home_team_name.lower())
                    
                    if not visitor_id or not home_id:
                        # Try fuzzy matching or known aliases if needed
                        # print(f"    Skipping: Unknown team {visitor_team_name} or {home_team_name}")
                        continue
                        
                    # Check if exists
                    cur.execute(f'''
                        SELECT "MatchID" FROM "{DB_SCHEMA}"."Matches"
                        WHERE "Date" = %s AND "HomeTeamID" = %s AND "VisitorTeamID" = %s
                    ''', (game_date, home_id, visitor_id))
                    
                    if cur.fetchone():
                        continue # Already exists
                        
                    # Insert
                    cur.execute(f'''
                        INSERT INTO "{DB_SCHEMA}"."Matches"
                        ("Date", "HomeTeamID", "VisitorTeamID", "HomeTeamScore", "VisitorPoints", 
                         "HomeTeamName", "VisitorTeamName")
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', (game_date, home_id, visitor_id, home_pts, visitor_pts, home_team_name, visitor_team_name))
                    
                    total_inserted += 1
                    # print(f"    Inserted: {game_date} - {visitor_team_name} @ {home_team_name}")
                    
            except Exception as e:
                print(f"  Error processing {month}: {e}")
                
            # Be polite to the server
            time.sleep(2)
            
        conn.commit()
        print(f"\nSuccess! Inserted {total_inserted} new game records.")
        return True
        
    except Exception as e:
        print(f"Error updating stats: {e}")
        conn.rollback()
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

if __name__ == "__main__":
    update_todays_stats()
