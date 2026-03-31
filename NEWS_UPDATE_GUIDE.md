# NBA News Update Guide

## Overview
The prediction model uses recent NBA news articles to improve prediction accuracy through sentiment analysis. Regular news updates ensure the model has the latest information about teams, players, injuries, and performance.

## How News Affects Predictions

News articles contribute **10%** to the team strength calculation through:
- **Sentiment Analysis**: Positive/negative keywords in articles
- **Recency Weighting**: Recent news (1-7 days) has more impact
- **Volume Factor**: More recent articles = higher confidence

## Available News Sources

### 1. BasketballNews.com (Primary Source)
- **Script**: `New.py`
- **Coverage**: 400+ pages of NBA news
- **Content**: Full articles with author and date
- **Update Frequency**: Run weekly or before important games

### 2. ESPN (Secondary Source)
- **Script**: `ESPN.py`
- **Coverage**: Latest headlines only
- **Content**: Titles and links
- **Update Frequency**: Daily updates

## Quick Update (Recommended)

### Option 1: Quick Update (50 pages)
```bash
python quick_news_update.py
```
- **Time**: ~5-10 minutes
- **Articles**: 50-100 new articles
- **Best for**: Regular weekly updates

### Option 2: Full Update (400 pages)
```bash
python New.py
```
- **Time**: ~30-60 minutes
- **Articles**: 500-1000 new articles
- **Best for**: Initial setup or monthly updates

### Option 3: Command File
```bash
update_news.cmd
```
- Interactive prompts
- Progress display
- Handles errors gracefully

## Update Process

### Step 1: Run News Crawler
```bash
python quick_news_update.py
```

### Step 2: Verify Import
Check database for new articles:
```sql
SELECT COUNT(*) FROM "NBA"."News" 
WHERE "Date" >= CURRENT_DATE - INTERVAL '7 days';
```

### Step 3: (Optional) Embed News
For vector-enhanced predictions:
```bash
python embed_all_news.py
```

## What Gets Updated

When you run the news update:

1. **Crawls BasketballNews.com**
   - Fetches article list from category pages
   - Extracts full article content
   - Parses author, date, and title

2. **Checks for Duplicates**
   - Skips articles already in database (by URL)
   - Only inserts new articles

3. **Stores in Database**
   ```sql
   Table: "NBA"."News"
   Columns:
   - NewsID (auto-increment)
   - Title
   - Content (full article text)
   - Date (publication date)
   - URL (unique)
   - Author
   ```

## Current News Statistics

Check your current news coverage:

```python
from database_prediction import connect_to_database

conn = connect_to_database()
cursor = conn.cursor()

# Total news count
cursor.execute('SELECT COUNT(*) FROM "NBA"."News"')
total = cursor.fetchone()[0]
print(f"Total news articles: {total}")

# Recent news (last 30 days)
cursor.execute('''
    SELECT COUNT(*) FROM "NBA"."News" 
    WHERE "Date" >= CURRENT_DATE - INTERVAL '30 days'
''')
recent = cursor.fetchone()[0]
print(f"Recent news (30 days): {recent}")

conn.close()
```

## Impact on Predictions

### Before News Update
```
Team: Los Angeles Lakers
News Articles (30 days): 15
Sentiment Score: 0.2 (slightly positive)
Confidence Impact: +1.5%
```

### After News Update
```
Team: Los Angeles Lakers
News Articles (30 days): 45 ⬆️
Sentiment Score: 0.4 (positive) ⬆️
Confidence Impact: +4.2% ⬆️
```

## Recommended Update Schedule

| Frequency | When | Method |
|-----------|------|--------|
| **Daily** | Before making predictions | ESPN.py (quick headlines) |
| **Weekly** | Monday mornings | quick_news_update.py (50 pages) |
| **Monthly** | Start of month | New.py (full 400 pages) |
| **Before Big Events** | Playoffs, All-Star | Full update + embeddings |

## Troubleshooting

### Issue: "Connection timeout"
**Solution**: Website might be slow, increase timeout:
```python
response = requests.get(url, headers=headers, timeout=30)  # Increase from 10 to 30
```

### Issue: "Duplicate key error"
**Solution**: Article already exists, this is normal behavior (skips automatically)

### Issue: "No articles found"
**Solution**: 
- Check internet connection
- Website structure might have changed
- Try ESPN.py as backup source

### Issue: "Database connection failed"
**Solution**:
```bash
# Check PostgreSQL is running
net start postgresql-x64-14

# Test connection
python -c "from database_prediction import connect_to_database; print('OK' if connect_to_database() else 'FAILED')"
```

## Advanced: Custom News Sources

To add your own news source:

```python
def crawl_custom_source():
    # 1. Fetch HTML
    response = requests.get('https://your-news-site.com/nba')
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 2. Parse articles
    articles = []
    for article in soup.find_all('article'):
        title = article.find('h2').text
        link = article.find('a')['href']
        articles.append({'title': title, 'url': link})
    
    # 3. Insert to database
    insert_news_to_db(articles)
```

## Files Reference

| File | Purpose | Run Time |
|------|---------|----------|
| `New.py` | Full news crawler (400 pages) | 30-60 min |
| `quick_news_update.py` | Quick update (50 pages) | 5-10 min |
| `ESPN.py` | ESPN headlines only | 1 min |
| `update_news.cmd` | Interactive update script | Varies |
| `embed_all_news.py` | Generate embeddings | 10-30 min |
| `news_embedding.py` | Embedding utilities | - |

## Best Practices

1. ✅ **Update before predictions**: Fresh news = better predictions
2. ✅ **Run weekly**: Keep database current
3. ✅ **Check logs**: Monitor for errors
4. ✅ **Verify imports**: Confirm new articles added
5. ✅ **Clean old news**: Archive articles > 1 year old

## Monitor News Impact

Track how news affects your predictions:

```python
from database_prediction import predict_game_outcome, get_team_context_data

# Get prediction with news
prediction = predict_game_outcome('Lakers', 'Warriors')
print(f"Confidence: {prediction['confidence']:.1%}")

# Check news sentiment
context = get_team_context_data('Lakers')
print(f"News articles: {len(context['news'])}")
```

---

**Need Help?** Check the prediction model logs or database for issues.

















