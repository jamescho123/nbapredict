# NOTE: Crawl news from https://www.nba.com/news

import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
import re
from dateutil import parser
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def crawl_all_nba_news():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for page in range(1, 410):
        url = f'https://www.basketballnews.com/news/categories/NBA%20News?page={page}'
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}: {response.status_code}")
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
            print(f"Page {page}: Found {len(articles)} news articles.")
            insert_news_to_db(articles)
        else:
            print(f"Page {page}: No news articles found.")


def extract_article_details(article_url):
    try:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to fetch article {article_url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Failed to fetch article {article_url}: {e}")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')

    # Title
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else None

    # Author: find the first matching div after the title
    author = None
    parent_block = soup.find('div', class_='css-175oi2r r-eqz5dr r-1uu6nss')
    if parent_block:
        # Author
        author_div = parent_block.find('div', itemprop='author')
        if author_div:
            name_div = author_div.find('div', itemprop='name')
            if name_div:
                author_inner = name_div.find('div', class_='css-1rynq56 r-1niwhzg r-t1lq8t r-1231a37 r-1enofrn r-356f0p r-tsynxw r-1xnzce8')
                if author_inner:
                    author = author_inner.get_text(strip=True)
        # Date
        date_div = parent_block.find('div', itemprop='datePublished')
        if date_div and date_div.has_attr('content'):
            from dateutil import parser
            try:
                date = parser.parse(date_div['content'])
            except Exception as e:
                print(f"Failed to parse date: {date_div['content']} - {e}")
    else:
        # Fallback: just find the first div with the class
        author_div = soup.find('div', class_='css-1rynq56 r-1niwhzg r-t1lq8t r-1231a37 r-1enofrn r-356f0p r-tsynxw r-1xnzce8')
        if author_div:
            author = author_div.get_text(strip=True)
        # Fallback: try to find by class
        date_div = soup.find('div', class_='css-1rynq56 r-1niwhzg r-t1lq8t r-1231a37 r-1enofrn r-356f0p r-1xnzce8')
        if date_div:
            from dateutil import parser
            try:
                date = parser.parse(date_div.get_text(strip=True))
            except Exception as e:
                print(f"Failed to parse date: {date_div.get_text(strip=True)} - {e}")
                date = None

    # Content
    content_div = soup.find('div', itemprop='articleBody')
    if content_div:
        content = '\n'.join(p.get_text(strip=True) for p in content_div.find_all('p'))
    else:
        content = None

    source = 'basketballnews.com'

    return {
        'title': title,
        'date': date,
        'source': source,
        'author': author,
        'content': content
    }


def insert_news_to_db(news_list):
    conn = psycopg2.connect(
        host='localhost',
        dbname='James',
        user='postgres',
        password='jcjc1749'
    )
    cur = conn.cursor()
    for news in news_list:
        details = extract_article_details(news['url'])
        if not details or not details['date'] or not details['content']:
            print(f"Skipping article due to missing date or content: {news['title']} ({news['url']})")
            continue
        
        # Check if article already exists
        cur.execute('''
            SELECT 1 FROM "NBA"."News" WHERE "Title" = %s AND "Source" = %s
        ''', (news['title'], details['source']))
        
        if cur.fetchone():
            print(f"Article already exists: {news['title']} ({news['url']})")
            continue
            
        try:
            cur.execute('''
                INSERT INTO "NBA"."News" ("Title", "Date", "Source", "Author", "Content", "URL")
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                news['title'],
                details['date'],
                details['source'],
                details['author'],
                details['content'],
                news['url']
            ))
            print(f"Inserted article: {news['title']} ({news['url']})")
        except psycopg2.IntegrityError:
            conn.rollback()
            print(f"Duplicate article (integrity error): {news['title']} ({news['url']})")
            continue
    conn.commit()
    cur.close()
    conn.close()


# Usage
if __name__ == '__main__':
    crawl_all_nba_news()
