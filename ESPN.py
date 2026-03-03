import requests
import pandas as pd
from bs4 import BeautifulSoup

# Crawl latest NBA news from ESPN

def crawl_espn_nba_news():
    url = 'https://www.espn.com/nba/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    print(f"HTTP status code: {response.status_code}")
    print("First 500 characters of the page:")
    print(response.text[:500])
    soup = BeautifulSoup(response.text, 'html.parser')
    news_items = []
    # ESPN NBA page: headlines are in <section> with class 'headlineStack', links in <li><a>
    headline_section = soup.find('section', class_='headlineStack')
    if headline_section:
        for li in headline_section.find_all('li'):
            a = li.find('a')
            if a and a.text:
                title = a.text.strip()
                link = a['href']
                if not link.startswith('http'):
                    link = 'https://www.espn.com' + link
                news_items.append({'Title': title, 'Link': link})
    else:
        print('Could not find news headlines section.')
    df = pd.DataFrame(news_items)
    print('Latest ESPN NBA News:')
    print(df)
    return df

if __name__ == '__main__':
    crawl_espn_nba_news() 