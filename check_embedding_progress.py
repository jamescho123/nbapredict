import psycopg2
import time

def check_embedding_progress():
    """Check the progress of the embedding process"""
    print("===== Embedding Progress Monitor =====")
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        # Get total news count
        cur.execute('SELECT COUNT(*) FROM "NBA"."News"')
        total_news = cur.fetchone()[0]
        
        # Initial check
        cur.execute('SELECT COUNT(*) FROM "NBA"."VectorNews"')
        initial_count = cur.fetchone()[0]
        
        print(f"Total news articles: {total_news}")
        print(f"Initial articles with embeddings: {initial_count}")
        print(f"Initial progress: {initial_count / total_news * 100:.2f}%")
        
        # Monitor progress
        print("\nMonitoring progress (press Ctrl+C to stop)...")
        print("Time\t\tEmbedded\tTotal\t\tProgress")
        print("-" * 60)
        
        try:
            prev_count = initial_count
            while True:
                # Get current count
                cur.execute('SELECT COUNT(*) FROM "NBA"."VectorNews"')
                current_count = cur.fetchone()[0]
                
                # Calculate progress
                progress = current_count / total_news * 100
                
                # Calculate rate
                new_embeddings = current_count - prev_count
                
                # Print progress
                current_time = time.strftime("%H:%M:%S")
                print(f"{current_time}\t{current_count}\t\t{total_news}\t\t{progress:.2f}%\t(+{new_embeddings})")
                
                prev_count = current_count
                
                # If all articles are embedded, stop monitoring
                if current_count >= total_news:
                    print("\nAll articles have been embedded!")
                    break
                
                # Wait before next check
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
        
        # Final check
        cur.execute('SELECT COUNT(*) FROM "NBA"."VectorNews"')
        final_count = cur.fetchone()[0]
        
        print(f"\nFinal articles with embeddings: {final_count}")
        print(f"Final progress: {final_count / total_news * 100:.2f}%")
        print(f"Articles remaining: {total_news - final_count}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_embedding_progress() 