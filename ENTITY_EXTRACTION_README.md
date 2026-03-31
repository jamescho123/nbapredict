# NBA News Entity Extraction System

This system implements the approach described in [Teaching a Database to Read NBA News with LLMs](https://alvincho.medium.com/teaching-a-database-to-read-nba-news-with-llms-2d7480ccbe59) to transform messy NBA news into structured data using LLM-powered entity recognition.

## 🎯 Overview

The system extracts structured entities from NBA news articles, including:
- **Players**: Individual basketball players
- **Teams**: NBA teams and organizations  
- **Injuries**: Player injuries and medical conditions
- **Penalties**: Fouls, technicals, and disciplinary actions
- **Stats**: Game statistics and performance metrics
- **Conflicts**: Altercations and disputes
- **Trades**: Player trades and transactions
- **Awards**: Recognition and achievements
- **Locations**: Arenas, cities, and venues
- **Dates**: Game dates and time references

## 🏗️ Architecture

### Database Schema

The system uses three main PostgreSQL tables:

```sql
-- News articles
CREATE TABLE "NBA"."news" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    body TEXT,
    url TEXT,
    published_at TIMESTAMPTZ,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Canonical entities
CREATE TABLE "NBA"."entity" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    etype entity_type NOT NULL,
    name TEXT NOT NULL,
    props JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(etype, name)
);

-- Entity mentions (links news to entities)
CREATE TABLE "NBA"."entity_mention" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    news_id UUID REFERENCES "NBA"."news"(id) ON DELETE CASCADE,
    entity_id UUID REFERENCES "NBA"."entity"(id) ON DELETE CASCADE,
    details JSONB DEFAULT '{}'::jsonb,
    source TEXT NOT NULL DEFAULT 'llm',
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### Components

1. **`create_entity_schema.py`** - Creates the PostgreSQL schema
2. **`nba_entity_extractor.py`** - LLM-powered entity extraction (requires Ollama)
3. **`nba_entity_extractor_offline.py`** - Rule-based fallback extraction
4. **`news_entity_processor.py`** - Main processing pipeline
5. **`pages/Entity_Extraction.py`** - Streamlit web interface

## 🚀 Usage

### 1. Setup Database Schema

```bash
python create_entity_schema.py
```

### 2. Process Existing News

```python
from news_entity_processor import NewsEntityProcessor

processor = NewsEntityProcessor()

# Process existing news articles
result = processor.process_existing_news(limit=10)
print(f"Processed {result['processed']} articles")
```

### 3. Process New Article

```python
# Process a single article
success = processor.process_new_article(
    title="Lakers Edge Warriors in Thriller",
    content="LeBron James dropped 42 points as the Lakers edged the Warriors...",
    source="ESPN"
)
```

### 4. Query Extracted Data

```python
from nba_entity_extractor import NBAEntityExtractor

extractor = NBAEntityExtractor()

# Get latest injuries
injuries = extractor.get_latest_injuries(limit=10)

# Get technical fouls
fouls = extractor.get_technical_fouls(limit=10)

# Get team game summaries
summaries = extractor.get_team_game_summaries("Lakers", limit=10)
```

## 🔍 Example Queries

### Find Latest Injuries
```sql
SELECT e.name AS player,
       em.details->>'injury' AS injury,
       em.details->>'status' AS status,
       n.title, n.published_at
FROM "NBA"."entity" e
JOIN "NBA"."entity_mention" em ON em.entity_id = e.id
JOIN "NBA"."news" n ON n.id = em.news_id
WHERE e.etype = 'player' AND em.details ? 'injury'
ORDER BY n.published_at DESC;
```

### See All Technical Fouls
```sql
SELECT e.name AS player, 
       em.details->>'penalty' AS penalty, 
       n.title
FROM "NBA"."entity" e
JOIN "NBA"."entity_mention" em ON em.entity_id = e.id
JOIN "NBA"."news" n ON n.id = em.news_id
WHERE em.details->>'penalty' = 'technical foul'
ORDER BY n.published_at DESC;
```

### Game Summaries for Lakers
```sql
SELECT em.details->>'score' AS score, 
       n.title, n.published_at
FROM "NBA"."entity" e
JOIN "NBA"."entity_mention" em ON em.entity_id = e.id
JOIN "NBA"."news" n ON n.id = em.news_id
WHERE e.etype = 'team' AND e.name = 'Los Angeles Lakers'
ORDER BY n.published_at DESC;
```

## 🌐 Web Interface

Access the entity extraction interface through the Streamlit app:

```bash
streamlit run Home.py
```

Navigate to "Entity Extraction" in the sidebar to:
- View extraction statistics
- Search for entities
- Browse injuries and penalties
- Process new articles
- Query structured data

## 🔧 Configuration

### LLM Setup (Optional)

For LLM-powered extraction, install and run Ollama:

```bash
# Install Ollama (if not already installed)
# Download from https://ollama.ai

# Pull a model
ollama pull llama3.1:latest

# Run the model
ollama serve
```

The system will automatically fall back to rule-based extraction if Ollama is not available.

### Database Configuration

Update the database connection in the files:
- Host: localhost
- Database: James
- Schema: NBA
- Username: postgres
- Password: jcjc1749

## 📊 Features

### Entity Extraction
- **LLM-powered**: Uses Ollama for intelligent entity recognition
- **Rule-based fallback**: Works without LLM using pattern matching
- **Comprehensive coverage**: Extracts 10+ entity types
- **Structured output**: JSON format with detailed properties

### Data Processing
- **Batch processing**: Process multiple articles at once
- **Incremental updates**: Skip already processed articles
- **Error handling**: Graceful fallback and error recovery
- **Statistics tracking**: Monitor processing progress

### Query Capabilities
- **Injury tracking**: Find player injuries and status
- **Penalty monitoring**: Track technical fouls and violations
- **Team analysis**: Get game summaries and performance
- **Entity search**: Search across all extracted entities
- **Temporal queries**: Filter by date ranges

## 🧪 Testing

Run the test suite to verify the system:

```bash
python test_entity_extraction.py
```

This will test:
- Database schema creation
- Entity extraction (both LLM and offline)
- News processing pipeline
- Query functions

## 📈 Benefits

1. **Structured Data**: Transform unstructured news into queryable data
2. **Real-time Insights**: Track injuries, penalties, and performance
3. **Scalable**: Process large volumes of news articles
4. **Flexible**: Support both LLM and rule-based extraction
5. **User-friendly**: Web interface for easy interaction

## 🔮 Future Enhancements

- **Sentiment Analysis**: Add emotional context to entities
- **Relationship Mapping**: Connect related entities
- **Trend Analysis**: Identify patterns over time
- **API Integration**: Real-time news processing
- **Advanced Queries**: More sophisticated search capabilities

## 📚 References

- [Teaching a Database to Read NBA News with LLMs](https://alvincho.medium.com/teaching-a-database-to-read-nba-news-with-llms-2d7480ccbe59)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
