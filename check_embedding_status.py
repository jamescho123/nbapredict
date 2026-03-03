"""
Check News Embedding Status
Shows how many articles have embeddings vs need embeddings
"""

import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

def check_status():
    """Check embedding status"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n" + "="*60)
        print("NEWS EMBEDDING STATUS")
        print("="*60 + "\n")
        
        # Total news count
        cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."News"')
        total = cursor.fetchone()[0]
        print(f"Total News Articles: {total}")
        
        # News with embeddings
        cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."VectorNews"')
        embedded = cursor.fetchone()[0]
        print(f"Articles with Embeddings: {embedded}")
        
        # News without embeddings
        remaining = total - embedded
        print(f"Articles Pending: {remaining}")
        
        # Percentage
        if total > 0:
            percentage = (embedded / total) * 100
            print(f"Completion: {percentage:.1f}%")
        
        # Recent news (last 7 days)
        cursor.execute(f'''
            SELECT COUNT(*) FROM "{DB_SCHEMA}"."News" 
            WHERE "Date" >= CURRENT_DATE - INTERVAL '7 days'
        ''')
        recent = cursor.fetchone()[0]
        print(f"\nRecent News (7 days): {recent}")
        
        # Recent news with embeddings
        cursor.execute(f'''
            SELECT COUNT(*) 
            FROM "{DB_SCHEMA}"."News" n
            INNER JOIN "{DB_SCHEMA}"."VectorNews" v ON n."NewsID" = v."NewsID"
            WHERE n."Date" >= CURRENT_DATE - INTERVAL '7 days'
        ''')
        recent_embedded = cursor.fetchone()[0]
        print(f"Recent with Embeddings: {recent_embedded}")
        
        # Progress bar
        print("\n" + "="*60)
        if total > 0:
            bar_length = 40
            filled = int((embedded / total) * bar_length)
            bar = "#" * filled + "-" * (bar_length - filled)
            print(f"Progress: [{bar}] {percentage:.1f}%")
        print("="*60 + "\n")
        
        # Recommendations
        if remaining > 0:
            print("\nTo embed remaining articles:")
            print("   python embed_all_news.py")
            print("   or")
            print("   python embed_news_quick.py")
        else:
            print("\nAll articles are embedded!")
            print("Your predictions can now use vector-enhanced analysis.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_status()

