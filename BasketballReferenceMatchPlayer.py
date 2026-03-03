import requests
import pandas as pd
import psycopg2
from bs4 import BeautifulSoup
from datetime import datetime
import time

DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

BASE_SCHEDULE_URL = "https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html"
MONTHS = [
    'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june'
]

# Helper: get player name to PlayerID mapping from DB
def get_player_name_to_id():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute('SELECT "PlayerID", "PlayerName" FROM "NBA"."Players"')
    players = cur.fetchall()
    cur.close()
    conn.close()
    return {name.lower(): pid for pid, name in players}

# Helper: get match url to MatchID mapping from DB
def get_match_url_to_id(conn):
    with conn.cursor() as cur:
        cur.execute('SELECT "MatchID", "Date", "HomeTeamName" FROM "NBA"."Matches"')
        matches = cur.fetchall()
    # Build a mapping from (date, home_team) to MatchID
    return { (str(date), home_team.lower()): mid for mid, date, home_team in matches }

def crawl_boxscores_for_season(year):
    boxscore_urls = []
    for month in MONTHS:
        url = BASE_SCHEDULE_URL.format(year=year, month=month)
        response = requests.get(url)
        if response.status_code != 200:
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        games_table = soup.find('table')
        if not games_table:
            continue
        for row in games_table.find('tbody').find_all('tr'):
            boxscore_link = row.find('a', text='Box Score')
            if boxscore_link:
                game_url = f"https://www.basketball-reference.com{boxscore_link['href']}"
                boxscore_urls.append(game_url)
    return boxscore_urls

def get_match_key_from_url(url):
    # Example: https://www.basketball-reference.com/boxscores/202506220OKC.html or .../202504210NYK.html
    # Extract date and home team from url
    import re
    m = re.search(r'/boxscores/(\d{8})0?([a-zA-Z]{3})\.html', url)
    if not m:
        print(f"[DEBUG] Regex did not match for url: {url}")
        return None
    date_str, home_initial = m.groups()
    date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    TEAM_INITIAL_TO_NAME = {
        "ATL": "Atlanta Hawks", "BOS": "Boston Celtics", "BRK": "Brooklyn Nets", "CHI": "Chicago Bulls",
        "CHO": "Charlotte Hornets", "CLE": "Cleveland Cavaliers", "DAL": "Dallas Mavericks", "DEN": "Denver Nuggets",
        "DET": "Detroit Pistons", "GSW": "Golden State Warriors", "HOU": "Houston Rockets", "IND": "Indiana Pacers",
        "LAC": "Los Angeles Clippers", "LAL": "Los Angeles Lakers", "MEM": "Memphis Grizzlies", "MIA": "Miami Heat",
        "MIL": "Milwaukee Bucks", "MIN": "Minnesota Timberwolves", "NOP": "New Orleans Pelicans", "NYK": "New York Knicks",
        "OKC": "Oklahoma City Thunder", "ORL": "Orlando Magic", "PHI": "Philadelphia 76ers", "PHO": "Phoenix Suns",
        "POR": "Portland Trail Blazers", "SAC": "Sacramento Kings", "SAS": "San Antonio Spurs", "TOR": "Toronto Raptors",
        "UTA": "Utah Jazz", "WAS": "Washington Wizards"
    }
    home_team = TEAM_INITIAL_TO_NAME.get(home_initial.upper(), home_initial)
    return (date_fmt, home_team.lower())

def crawl_match_player_stats(match_url, match_id, conn):
    """
    Crawl player statistics for a given match from Basketball Reference and insert using match_id.
    """
    import io
    response = requests.get(match_url)
    if response.status_code != 200:
        print(f"[WARN] Could not fetch match page: {match_url}")
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    player_name_to_id = get_player_name_to_id()
    inserted_count = 0
    for table in tables:
        if not table.get('id') or not ('box' in table.get('id') and 'basic' in table.get('id')):
            continue
        from io import StringIO
        df = pd.read_html(StringIO(str(table)))[0]
        if 'Starters' in df.columns:
            df = df[~df['Starters'].isin(['Reserves', 'Team Totals', 'Did Not Play', 'Did Not Dress'])]
        for _, row in df.iterrows():
            player_name = row[df.columns[0]].strip()
            if player_name in ['Reserves', 'Team Totals']:
                continue
            player_id = player_name_to_id.get(player_name.lower())
            if not player_id:
                print(f"[SKIP] Player '{player_name}' does not exist in Players table. Skipping.")
                continue
            try:
                mp = row.get('MP', None)
                if mp is None or mp in ['Did Not Play', 'Did Not Dress', '']:
                    continue
                if isinstance(mp, str) and ':' in mp:
                    min_, sec_ = mp.split(':')
                    mp = int(min_) * 60 + int(sec_)
                else:
                    mp = int(mp) if pd.notna(mp) else 0
                fg = int(row.get('FG', 0)) if pd.notna(row.get('FG', 0)) else 0
                fga = int(row.get('FGA', 0)) if pd.notna(row.get('FGA', 0)) else 0
                fg_pct = float(row.get('FG%', 0)) if pd.notna(row.get('FG%', 0)) and row.get('FG%', 0) != '' else 0.0
                tp = int(row.get('3P', 0)) if pd.notna(row.get('3P', 0)) else 0
                tpa = int(row.get('3PA', 0)) if pd.notna(row.get('3PA', 0)) else 0
            except Exception as e:
                print(f"[WARN] Stat parse error for {player_name}: {e}")
                continue
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO "NBA"."MatchPlayer" ("MatchID", "PlayerID", "MP", "FG", "FGA", "FGPercentage", "3P", "3PA")
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (match_id, player_id, mp, fg, fga, fg_pct, tp, tpa))
            inserted_count += 1
    print(f"[INFO] Inserted {inserted_count} player stats for match {match_id}")

def check_matches_table_access():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute('SELECT "MatchID", "Date", "HomeTeamName" FROM "NBA"."Matches"')
            matches = cur.fetchall()
            print("[DEBUG] Matches table rows:")
            for mid, date, home in matches:
                print(f"MatchID: {mid}, Date: {date}, HomeTeamName: {home}, Key: ({str(date)}, {home.lower()})")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Could not access Matches table: {e}")

def show_matchplayer_for_matchid(match_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM "NBA"."MatchPlayer" WHERE "MatchID" = %s', (match_id,))
            rows = cur.fetchall()
            print(f"[DEBUG] MatchPlayer rows for MatchID={match_id}:")
            for row in rows:
                print(row)
        conn.close()
    except Exception as e:
        print(f"[ERROR] Could not access MatchPlayer table: {e}")

def main():
    show_matchplayer_for_matchid(1)
    check_matches_table_access()
    season = 1990  # 1989-90 season
    conn = psycopg2.connect(**DB_CONFIG)
    match_url_to_id = get_match_url_to_id(conn)
    boxscore_urls = crawl_boxscores_for_season(season)
    for url in boxscore_urls:
        match_key = get_match_key_from_url(url)
        if not match_key:
            print(f"[WARN] Could not parse match key from url: {url}")
            continue
        match_id = match_url_to_id.get(match_key)
        if not match_id:
            print(f"[WARN] No MatchID found for {match_key} from url: {url}")
            continue
        crawl_match_player_stats(url, match_id, conn)
    conn.close()

if __name__ == "__main__":
    main() 