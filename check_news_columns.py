import psycopg2

def check_columns():
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'NBA' AND table_name = 'News'")
        cols = cur.fetchall()
        print([col[0] for col in cols])
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_columns()
