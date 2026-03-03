import psycopg2
from db_config import DB_CONFIG, DB_SCHEMA

def check_schema():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '{DB_SCHEMA}' AND table_name = 'VectorNews';")
        columns = cur.fetchall()
        for col in columns:
            print(f"{col[0]}: {col[1]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
