import psycopg2

def add_image_column():
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        # Add ImageURL column
        cur.execute("""
            ALTER TABLE "NBA"."News" 
            ADD COLUMN IF NOT EXISTS "ImageURL" TEXT;
        """)
        
        conn.commit()
        print("Successfully added ImageURL column to News table.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_image_column()
