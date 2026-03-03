import psycopg2
import json

def get_latest_news():
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        # Get latest 4 news
        cur.execute('SELECT "NewsID", "Title" FROM "NBA"."News" ORDER BY "Date" DESC LIMIT 4')
        news_items = cur.fetchall()
        
        results = []
        for news_id, title in news_items:
            results.append({"id": news_id, "title": title})
            
        print(json.dumps(results))
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_latest_news()
