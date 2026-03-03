import psycopg2
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def check_missing_urls():
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        cur.execute('SELECT "Title", "URL" FROM "NBA"."News" WHERE "URL" IS NULL LIMIT 10')
        rows = cur.fetchall()
        for row in rows:
            print(f"Title: {row[0]}")
            print(f"URL: {row[1]}")
            print("-" * 20)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_missing_urls()
