import requests
from bs4 import BeautifulSoup
import sys
from datetime import datetime
from db_config import get_connection, DB_SCHEMA
import io

# Set encoding to handle special characters in console
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# DB_CONFIG removed in favor of db_config.py

def crawl_recent_nba_news(max_pages=50):
    """Crawl recent NBA news articles"""
    print(f"Crawling up to {max_pages} pages of NBA news...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    total_articles = 0
    new_articles = 0
    
    for page in range(1, max_pages + 1):
        url = f'https://www.basketballnews.com/news/categories/NBA%20News?page={page}'
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"  Page {page}: Failed ({response.status_code})")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            for a in soup.find_all('a', href=True):
                link = a['href']  
                if not link.startswith('/stories/'):
                    continue
                h1 = a.find('h1', class_='css-1rynq56')
                if not h1:
                    continue
                title = h1.get_text(strip=True)
                if not title:
                    continue
                full_url = f'https://www.basketballnews.com{link}'
                articles.append({'title': title, 'url': full_url})
            
            if articles:
                inserted = insert_news_to_db(articles)
                total_articles += len(articles)
                new_articles += inserted
                print(f"  Page {page}: {len(articles)} articles found, {inserted} new")
            else:
                print(f"  Page {page}: No articles found")
                
            # Print progress every 10 pages
            if page % 10 == 0:
                print(f"\n  Progress: {page}/{max_pages} pages | {total_articles} total | {new_articles} new\n")
                
        except Exception as e:
            print(f"  Page {page}: Error - {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"News crawl complete!")
    print(f"  Total articles found: {total_articles}")
    print(f"  New articles added: {new_articles}")
    print(f"{'='*60}\n")
    
    return total_articles, new_articles

def insert_news_to_db(articles):
    """Insert news articles into database"""
    conn = None
    inserted_count = 0
    
    try:
        conn = get_connection()
        if not conn:
            print("  Database connection failed.")
            return 0
        cursor = conn.cursor()
        
        for article in articles:
            try:
                # Check if URL already exists
                cursor.execute(f'''
                    SELECT "NewsID" FROM "{DB_SCHEMA}"."News" 
                    WHERE "URL" = %s
                ''', (article['url'],))
                
                if cursor.fetchone():
                    continue  # Skip if already exists
                
                # Get article details
                details = extract_article_details(article['url'])
                if not details:
                    continue
                
                # Insert new article
                cursor.execute(f'''
                    INSERT INTO "{DB_SCHEMA}"."News" 
                    ("Title", "Content", "Date", "URL", "Author", "Source")
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    details.get('title', article['title']),
                    details.get('content', ''),
                    details.get('date', datetime.now()),
                    article['url'],
                    details.get('author', ''),
                    "Basketball News"
                ))
                
                inserted_count += 1
                
            except Exception as e:
                print(f"    Error inserting {article['title'][:50]}...: {e}")
                continue
        
        conn.commit()
        cursor.close()
        
    except Exception as e:
        print(f"  Database error: {e}")
    finally:
        if conn:
            conn.close()
    
    return inserted_count

def extract_article_details(article_url):
    """Extract article content, author, and date"""
    try:
        response = requests.get(article_url, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Title
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else None
        
        # Date
        date = None
        date_div = soup.find('div', itemprop='datePublished')
        if date_div and date_div.has_attr('content'):
            try:
                from dateutil import parser
                date = parser.parse(date_div['content'])
            except:
                date = datetime.now()
        else:
            date = datetime.now()
        
        # Author
        author = None
        author_div = soup.find('div', itemprop='author')
        if author_div:
            name_div = author_div.find('div', itemprop='name')
            if name_div:
                author = name_div.get_text(strip=True)
        
        # Content
        content_div = soup.find('div', itemprop='articleBody')
        if content_div:
            content = '\n'.join(p.get_text(strip=True) for p in content_div.find_all('p'))
        else:
            content = ''
        
        return {
            'title': title,
            'date': date,
            'author': author or 'Unknown',
            'content': content
        }
        
    except Exception as e:
        return None

if __name__ == '__main__':
    print("\n" + "="*60)
    print("NBA News Updater")
    print("="*60 + "\n")
    
    # Crawl recent news
    total, new = crawl_recent_nba_news(max_pages=50)
    
    print("\nDone! Your NBA news database is now updated.")
    print(f"   Use these articles in your predictions for better accuracy.\n")

















