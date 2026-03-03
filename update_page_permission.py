import psycopg2
from db_config import DB_SCHEMA

def add_news_detail_permission():
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        page_name = "News Detail"
        min_role = "guest"
        is_visible = True
        
        # Check if exists
        cur.execute(f'SELECT 1 FROM "{DB_SCHEMA}"."PageVisibility" WHERE "PageName" = %s', (page_name,))
        if cur.fetchone():
            print(f"Page '{page_name}' already exists. Updating...")
            cur.execute(f'''
                UPDATE "{DB_SCHEMA}"."PageVisibility"
                SET "MinRole" = %s, "IsVisible" = %s
                WHERE "PageName" = %s
            ''', (min_role, is_visible, page_name))
        else:
            print(f"Insert page '{page_name}'...")
            cur.execute(f'''
                INSERT INTO "{DB_SCHEMA}"."PageVisibility" ("PageName", "IsVisible", "MinRole")
                VALUES (%s, %s, %s)
            ''', (page_name, is_visible, min_role))
            
        conn.commit()
        print(f"Successfully set permission for '{page_name}' to '{min_role}'.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_news_detail_permission()
