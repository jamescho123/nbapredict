import requests
import pandas as pd
import psycopg2
from bs4 import BeautifulSoup
from datetime import datetime

DB_HOST = 'localhost'
DB_NAME = 'James'
DB_USER = 'postgres'
DB_PASS = 'jcjc1749'
DB_SCHEMA = 'NBA'

# Helper: get team name to TeamID mapping from DB
def get_team_name_to_id():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()
    cur.execute(f'SELECT "TeamID", "TeamName" FROM "{DB_SCHEMA}"."Teams"')
    teams = cur.fetchall()
    cur.close()
    conn.close()
    return {name.lower(): tid for tid, name in teams}

def crawl_boxscores_for_season(season_start=1947, season_end=None):
    if season_end is None:
        season_end = datetime.now().year + 1
    all_game_urls = []
    for season in range(season_start, season_end):
        url = f'https://www.basketball-reference.com/leagues/NBA_{season}_games.html'
        print(f'Crawling season page: {url}')
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        months = soup.find('div', {'class': 'filter'})
        if not months:
            continue
        month_links = [f"https://www.basketball-reference.com{a['href']}" for a in months.find_all('a')]
        for month_url in month_links:
            print(f'Crawling month page: {month_url}')
            month_response = requests.get(month_url)
            month_soup = BeautifulSoup(month_response.text, 'html.parser')
            games_table = month_soup.find('table')
            if not games_table:
                continue
            for row in games_table.find('tbody').find_all('tr'):
                boxscore_link = row.find('a', text='Box Score')
                if boxscore_link:
                    game_url = f"https://www.basketball-reference.com{boxscore_link['href']}"
                    all_game_urls.append(game_url)
    print(f"Found {len(all_game_urls)} games.")
    return all_game_urls

def parse_match_details(game_url):
    print(f'Parsing {game_url}')
    response = requests.get(game_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    linescore = soup.find('div', {'class': 'scorebox'})
    if not linescore:
        print('No scorebox found')
        return None
    teams = linescore.find_all('strong')
    scores = linescore.find_all('div', {'class': 'score'})
    if len(teams) < 2 or len(scores) < 2:
        print('Teams or scores not found')
        return None
    home_team = teams[1].text.strip()
    road_team = teams[0].text.strip()
    home_score = int(scores[1].text.strip())
    road_score = int(scores[0].text.strip())
    time_info = soup.find('div', {'class': 'scorebox_meta'})
    match_date = None
    if time_info:
        for div in time_info.find_all('div'):
            try:
                match_date = pd.to_datetime(div.text.strip()).date()
                break
            except Exception:
                continue
    officials = None
    for comment in soup.find_all(string=lambda text: isinstance(text, type(soup.Comment))):
        if 'Officials' in comment:
            officials = comment.split('Officials:')[-1].split('<br')[0].strip()
            break
    return {
        'HomeTeamName': home_team,
        'RoadTeamName': road_team,
        'Date': match_date,
        'HomeScore': home_score,
        'RoadScore': road_score,
        'Officials': officials
    }

def match_exists(cur, home_id, road_id, match_date):
    cur.execute(f'''
        SELECT 1 FROM "{DB_SCHEMA}"."Matches"
        WHERE "HomeTeamID" = %s AND "VisitorTeamID" = %s AND "Date" = %s
    ''', (home_id, road_id, match_date))
    return cur.fetchone() is not None

def main():
    # Process NBA seasons from 2024-25 onward
    season_start = 1990
    season_end = 1991
    months = [
        'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june'
    ]
    # Access Team table from Postgres for mapping
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()
    cur.execute(f'SELECT "TeamID", "TeamName" FROM "{DB_SCHEMA}"."Teams"')
    teams = cur.fetchall()
    team_name_to_id = {name.lower(): tid for tid, name in teams}
    inserted_count = 0
    for season in range(season_start, season_end):
        for month in months:
            month_url = f'https://www.basketball-reference.com/leagues/NBA_{season}_games-{month}.html#schedule'
            print(f'Crawling month page: {month_url}')
            response = requests.get(month_url)
            if response.status_code != 200:
                print(f'Failed to fetch {month_url}')
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            games_table = soup.find('table')
            if not games_table:
                print(f'No table found on {month_url}')
                continue
            row_count = 0
            for row in games_table.find('tbody').find_all('tr'):
                cols = row.find_all('td')
                if not cols or len(cols) < 6:
                    continue
                row_count += 1
                date_cell = row.find('th')
                date_str = date_cell.text.strip() if date_cell else None
                try:
                    match_date = pd.to_datetime(date_str).date() if date_str else None
                except Exception:
                    match_date = None
                visitor_team = cols[0].text.strip()
                visitor_score = int(cols[1].text.strip()) if cols[1].text.strip().isdigit() else None
                home_team = cols[2].text.strip()
                home_score = int(cols[3].text.strip()) if cols[3].text.strip().isdigit() else None
                boxscore_link = row.find('a', text='Box Score')
                officials = None
                if boxscore_link:
                    # Optionally, parse officials from the box score page
                    box_url = f"https://www.basketball-reference.com{boxscore_link['href']}"
                    try:
                        box_response = requests.get(box_url)
                        box_soup = BeautifulSoup(box_response.text, 'html.parser')
                        for comment in box_soup.find_all(string=lambda text: isinstance(text, type(box_soup.Comment))):
                            if 'Officials' in comment:
                                officials = comment.split('Officials:')[-1].split('<br')[0].strip()
                                break
                    except Exception:
                        officials = None
                home_id = team_name_to_id.get(home_team.lower())
                road_id = team_name_to_id.get(visitor_team.lower())
                if not home_id or not road_id:
                    print(f"Skipping match: TeamID not found for {home_team} or {visitor_team}")
                    continue
                if match_exists(cur, home_id, road_id, match_date):
                    print(f"Match already exists: {home_team} vs {visitor_team} at {match_date}")
                    continue
                try:
                    cur.execute(f'''
                        INSERT INTO "{DB_SCHEMA}"."Matches" (
                            "HomeTeamID", "VisitorTeamID", "Date", "VisitorTeamName", "VisitorPoints", "HomeTeamName", "HomeTeamScore"
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        home_id, road_id, match_date, visitor_team, visitor_score, home_team, home_score
                    ))
                    inserted_count += 1
                    print(f"Inserted match: {home_team} vs {visitor_team} at {match_date}")
                except Exception as e:
                    print(f"Error inserting match: {e}")
            print(f"[DEBUG] Parsed {row_count} rows for {season} {month} (URL: {month_url})")
    conn.commit()
    cur.close()
    conn.close()
    print(f"Total matches inserted: {inserted_count}")

if __name__ == "__main__":
    main() 