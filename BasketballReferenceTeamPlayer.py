import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
import unicodedata

NBA_TEAM_INITIALS = [
    "ATL", "BOS", "BRK", "CHI", "CHO", "CLE", "DAL", "DEN", "DET", "GSW",
    "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
    "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"
]

BASE_URL = "https://www.basketball-reference.com/teams/{}/players.html"

DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

TEAM_INITIAL_TO_NAME = {
    "ATL": "Atlanta Hawks",
    "BOS": "Boston Celtics",
    "BRK": "Brooklyn Nets",
    "CHI": "Chicago Bulls",
    "CHO": "Charlotte Hornets",
    "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors",
    "HOU": "Houston Rockets",
    "IND": "Indiana Pacers",
    "LAC": "Los Angeles Clippers",
    "LAL": "Los Angeles Lakers",
    "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks",
    "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans",
    "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic",
    "PHI": "Philadelphia 76ers",
    "PHO": "Phoenix Suns",
    "POR": "Portland Trail Blazers",
    "SAC": "Sacramento Kings",
    "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz",
    "WAS": "Washington Wizards"
}

def normalize_team_name(name):
    # Lowercase, remove accents, strip, and remove non-alphanumeric except spaces
    name = name.lower().strip()
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    name = ''.join(c for c in name if c.isalnum() or c.isspace())
    name = ' '.join(name.split())  # collapse multiple spaces
    return name

def get_team_name_to_id(conn):
    with conn.cursor() as cur:
        cur.execute(f'SELECT "TeamID", "TeamName" FROM "{DB_SCHEMA}"."Teams"')
        teams = cur.fetchall()
    return {normalize_team_name(name): tid for tid, name in teams}

def get_player_name_to_id(conn):
    with conn.cursor() as cur:
        cur.execute(f'SELECT "PlayerID", "PlayerName" FROM "{DB_SCHEMA}"."Players"')
        players = cur.fetchall()
    return {name.lower(): pid for pid, name in players}

def insert_team_player(conn, team_id, player_id, team_name, player_name, from_year, to_year, years):
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO "NBA"."TeamPlayer" ("TeamID", "PlayerID", "TeamName", "PlayerName", "From", "To", "Years")
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT ("TeamID", "PlayerID") DO NOTHING;
        ''', (team_id, player_id, team_name, player_name, from_year, to_year, years))
    conn.commit()

def crawl_team_players(team_initial, conn, team_name_to_id, player_name_to_id):
    url = BASE_URL.format(team_initial)
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    if not table:
        print(f"[DEBUG] No player table found on Basketball Reference for team: {team_initial}")
        return
    print(f"[DEBUG] Player table found for team: {team_initial}")
    team_name = TEAM_INITIAL_TO_NAME.get(team_initial, team_initial)
    norm_team_name = normalize_team_name(team_name)
    team_id = team_name_to_id.get(norm_team_name)
    if not team_id:
        print(f"TeamID not found for {team_name} (normalized: {norm_team_name})")
        return
    tbody = table.find('tbody')
    for row in tbody.find_all('tr'):
        if row.get('class') and 'thead' in row.get('class'):
            continue
        cols = row.find_all('td')
        if not cols or len(cols) < 4:
            continue
        player_link = row.find('a')
        player_name = cols[0].text.strip()
        player_id = player_name_to_id.get(player_name.lower())
        if not player_id:
            print(f"PlayerID not found for {player_name}")
            continue
        from_year = cols[1].text.strip()
        to_year = cols[2].text.strip()
        years = cols[3].text.strip()
        try:
            years = int(years)
            from_date = datetime.strptime(from_year, "%Y").date()
            to_date = datetime.strptime(to_year, "%Y").date()
        except Exception:
            continue
        insert_team_player(conn, team_id, player_id, team_name, player_name, from_date, to_date, years)

def check_teams_table_access():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute(f'SELECT "TeamID", "TeamName" FROM "{DB_SCHEMA}"."Teams"')
            teams = cur.fetchall()
            print("[DEBUG] Teams table rows:")
            for tid, name in teams:
                print(f"TeamID: {tid}, TeamName: {name}")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Could not access Teams table: {e}")

def crawl_all_teams():
    check_teams_table_access()
    conn = psycopg2.connect(**DB_CONFIG)
    team_name_to_id = get_team_name_to_id(conn)
    player_name_to_id = get_player_name_to_id(conn)
    for team in NBA_TEAM_INITIALS:
        print(f"Crawling players for team: {team}")
        crawl_team_players(team, conn, team_name_to_id, player_name_to_id)
    conn.close()

if __name__ == "__main__":
    crawl_all_teams()
