from db_config import get_connection, DB_SCHEMA

def check_queue():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(f'SELECT count(*) FROM "{DB_SCHEMA}"."News"')
    total = cur.fetchone()[0]
    print(f"Total News: {total}")

    cur.execute(f'SELECT "NewsID", "ImageStatus", "ImagePrompt", "ImageURL" FROM "{DB_SCHEMA}"."News" ORDER BY "Date" DESC LIMIT 10')
    rows = cur.fetchall()
    print("\nLatest 10 News items:")
    for row in rows:
        print(f"ID: {row[0]}, Status: {row[1]}, URL: {row[3]}, Prompt: {row[2][:30] if row[2] else 'None'}...")
    
    cur.execute(f'SELECT count(*) FROM "{DB_SCHEMA}"."News" WHERE "ImageStatus" = \'completed\'')
    completed = cur.fetchone()[0]
    print(f"\nTotal Completed: {completed}")
    
    conn.close()

if __name__ == "__main__":
    check_queue()
