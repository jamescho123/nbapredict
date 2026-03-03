import psycopg2
from db_config import DB_SCHEMA

def check_visibility():
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        cur.execute(f'SELECT "PageName", "IsVisible", "MinRole" FROM "{DB_SCHEMA}"."PageVisibility"')
        rows = cur.fetchall()
        print("PageVisibility Settings:")
        for row in rows:
            print(f"Page: {row[0]}, Visible: {row[1]}, MinRole: {row[2]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_visibility()
