import psycopg2
import json

def fetch_latest_news():
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        cur.execute('SELECT "NewsID", "Title" FROM "NBA"."News" ORDER BY "Date" DESC LIMIT 4')
        news_items = cur.fetchall()
        
        results = [{"NewsID": row[0], "Title": row[1]} for row in news_items]
        print(json.dumps(results))
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_latest_news()
