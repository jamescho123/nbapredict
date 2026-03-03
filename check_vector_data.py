import psycopg2
from db_config import DB_CONFIG, DB_SCHEMA

def check_vector_data():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."VectorNews";')
        count = cur.fetchone()[0]
        print(f"Total rows in VectorNews: {count}")
        if count > 0:
            cur.execute(f'SELECT "NewsID" FROM "{DB_SCHEMA}"."VectorNews" LIMIT 5;')
            ids = cur.fetchall()
            print(f"Sample NewsIDs: {[i[0] for i in ids]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_vector_data()
