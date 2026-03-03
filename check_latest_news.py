import psycopg2
from db_config import get_connection, DB_SCHEMA

def check_latest():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT "Title", "Date" FROM "{DB_SCHEMA}"."News" ORDER BY "Date" DESC LIMIT 5')
    rows = cur.fetchall()
    for row in rows:
        print(f"{row[0]} | {row[1]}")
    conn.close()

if __name__ == "__main__":
    check_latest()
