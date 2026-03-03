import psycopg2
from db_config import DB_CONFIG, DB_SCHEMA

def check_tables():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{DB_SCHEMA}';")
        tables = cur.fetchall()
        for table in tables:
            print(table[0])
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_tables()
