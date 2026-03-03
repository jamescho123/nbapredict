
from db_config import get_connection, DB_SCHEMA
import pandas as pd

def check_latest_news_urls():
    try:
        conn = get_connection()
        query = f'''
        SELECT "NewsID", "Title", "Date", "URL"
        FROM "{DB_SCHEMA}"."News"
        ORDER BY "Date" DESC
        LIMIT 10
        '''
        df = pd.read_sql_query(query, conn)
        print(df)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_latest_news_urls()
