#This is a script to crawl data from basketball reference

import requests
import pandas as pd
from bs4 import BeautifulSoup
import psycopg2

# URL for NBA team stats (2023-24 season as example)
url = 'https://www.basketball-reference.com/leagues/NBA_2024.html'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# The team stats table has id 'team-stats-per_game'
table = soup.find('table', {'id': 'per_game-team'})

# Database connection parameters
DB_HOST = 'localhost'
DB_NAME = 'James'
DB_USER = 'postgres'
DB_PASS = 'jcjc1749'
DB_SCHEMA = 'NBA'

# Parse table into DataFrame
if table:
    df = pd.read_html(str(table))[0]
    # Remove rows that are not teams (like 'League Average')
    df = df[df['Team'] != 'League Average']
    print(df)

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()

    for _, row in df.iterrows():
        team_name = row['Team']
        # You may need to map or fill these fields based on available data
        conference = row.get('Conference', '')
        division = row.get('Division', '')
        state = ''  # Basketball Reference does not provide state directly
        start_date = pd.Timestamp.now().date()  # Use current date as placeholder

        # Check if team exists
        cur.execute(f'SELECT 1 FROM "{DB_SCHEMA}"."Teams" WHERE "TeamName" = %s', (team_name,))
        if not cur.fetchone():
            # Insert if not exists
            cur.execute(f'''
                INSERT INTO "{DB_SCHEMA}"."Teams" ("StartDate", "Conference", "Division", "State", "TeamName")
                VALUES (%s, %s, %s, %s, %s)
            ''', (start_date, conference, division, state, team_name))
            print(f'Inserted team: {team_name}')
        else:
            print(f'Team already exists: {team_name}')
    conn.commit()
    cur.close()
    conn.close()
else:
    print('Could not find the team stats table.')
