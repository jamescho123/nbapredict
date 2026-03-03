import requests
import pandas as pd
import psycopg2
from io import StringIO
from datetime import datetime

DB_HOST = 'localhost'
DB_NAME = 'James'
DB_USER = 'postgres'
DB_PASS = 'jcjc1749'
DB_SCHEMA = 'NBA'

def year_to_date(year_str):
    if not year_str or not str(year_str).split('-')[0].isdigit():
        return None
    return f"{year_str.split('-')[0]}-01-01"

url = 'https://www.basketball-reference.com/teams/'
response = requests.get(url)
all_tables = pd.read_html(StringIO(response.text))
df = all_tables[0]

print('DataFrame preview:')
print(df.head())
print('Columns:', df.columns.tolist())

# Connect to PostgreSQL
conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
cur = conn.cursor()

inserted_count = 0
for _, row in df.iterrows():
    try:
        team_name = row['Franchise'] if 'Franchise' in row else row.get('Team', None)
        from_year = year_to_date(str(row['From'])) if 'From' in row else None
        to_year = year_to_date(str(row['To'])) if 'To' in row else None
        years = int(row['Yrs']) if 'Yrs' in row and pd.notna(row['Yrs']) else None
        games = int(row['G']) if 'G' in row and pd.notna(row['G']) else None
        win_percentage = float(row['W/L%']) if 'W/L%' in row and pd.notna(row['W/L%']) else None
        playoffs = int(row['Plyfs']) if 'Plyfs' in row and pd.notna(row['Plyfs']) else None
        conference_champion = int(row['Conf']) if 'Conf' in row and pd.notna(row['Conf']) else None
        championship = int(row['Champ']) if 'Champ' in row and pd.notna(row['Champ']) else None
        conference = row['Conf'] if 'Conf' in row else None
        division = row['Div'] if 'Div' in row else None
        print(f"Inserting: {team_name}, {from_year}, {to_year}, {years}, {games}, {win_percentage}, {playoffs}, {conference_champion}, {championship}, {conference}, {division}")
        cur.execute(f'''
            INSERT INTO "{DB_SCHEMA}"."Teams" (
                "TeamName", "From", "To", "Years", "Games", "WinPercentage", "Playoffs", "ConferenceChampion", "Championship", "Conference", "Division"
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (team_name, from_year, to_year, years, games, win_percentage, playoffs, conference_champion, championship, conference, division))
        inserted_count += 1
        print(f'Inserted: {team_name}')
    except Exception as e:
        print(f'Error inserting {team_name}: {e}')
conn.commit()
cur.close()
conn.close()
print(f"Total teams inserted: {inserted_count}")
