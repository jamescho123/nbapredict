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


def fetch_nba_players():
    url = 'https://www.nba.com/players'
    response = requests.get(url)
    tables = pd.read_html(response.text)
    player_df = tables[0]  # The main player stats table

    # Clean and map columns
    player_df.columns = [col.strip() for col in player_df.columns]
    # Example columns: Player, Team, Number, Position, Height, Weight, Last Attended, Country
    
    # Height and Weight conversion
    def parse_height(height_str):
        if isinstance(height_str, str) and '-' in height_str:
            feet, inches = height_str.split('-')
            return int(feet) * 12 + int(inches)
        return None
    def parse_weight(weight_str):
        if isinstance(weight_str, str) and 'lbs' in weight_str:
            return int(weight_str.replace('lbs', '').strip())
        return None

    # Connect to PostgreSQL
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()
    inserted_count = 0
    for _, row in player_df.iterrows():
        try:
            player_name = row['Player'] if 'Player' in row else None
            number = int(row['Number']) if 'Number' in row and pd.notna(row['Number']) else None
            position = row['Position'] if 'Position' in row else None
            height = parse_height(row['Height']) if 'Height' in row else None
            weight = parse_weight(row['Weight']) if 'Weight' in row else None
            colleges = row['Last Attended'] if 'Last Attended' in row else None
            country = row['Country'] if 'Country' in row else None
            cur.execute(f'''
                INSERT INTO "{DB_SCHEMA}"."Players" (
                    "PlayerName", "Number", "Position", "Height", "Weight", "Colleges", "Country"
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT ("PlayerName", "Colleges") DO NOTHING
            ''', (player_name, number, position, height, weight, colleges, country))
            inserted_count += 1
        except Exception as e:
            print(f'Error inserting {player_name}: {e}')
    conn.commit()
    cur.close()
    conn.close()
    print(f"Total players inserted: {inserted_count}")


def main():
    fetch_nba_players()


if __name__ == '__main__':
    main()
