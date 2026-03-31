# NBA Predict 🏀

A comprehensive NBA statistics, news, and prediction application built with Streamlit and PostgreSQL, featuring advanced vector search capabilities using pgvector and AI-powered embeddings.

## 🚀 Features

- **📊 Statistics Dashboard**: Comprehensive player and team statistics
- **📰 News Aggregation**: Latest NBA news from multiple sources

- **🎯 Game Predictions**: Predictive analytics for upcoming NBA games
- **🏆 Team Rankings**: Current NBA team standings and rankings
- **🧠 Vector Search**: Advanced similarity search using pgvector extension

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: PostgreSQL with pgvector extension
- **AI/ML**: Ollama with BGE-M3 model for embeddings
- **Data Sources**: Basketball Reference, ESPN
- **Vector Operations**: pgvector for similarity search

## 📋 Prerequisites

- Python 3.7+
- PostgreSQL 12+
- pgvector extension
- Ollama (for AI embeddings)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd nbapredict
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install pgvector Extension

#### Option A: Using Pre-compiled Binaries
```bash
# Windows
compile_pgvector.cmd

# Or manually
copy_pgvector_files.cmd
```

#### Option B: Compile from Source
```bash
# Windows
compile_pgvector_source.cmd

# Or manually
compile_pgvector.py
```

### 4. Install Ollama
1. Download from [https://ollama.com/](https://ollama.com/)
2. Install and start the service
3. Pull the BGE-M3 model:
```bash
ollama pull bge-m3
```

### 5. Database Setup
```sql
-- Create the vector extension
CREATE EXTENSION vector;

-- Create the NBA schema and tables
-- (See Database.md for detailed schema)
```

## 🎯 Usage

### Running the Application
```bash
streamlit run Home.py
```

### Navigation
The application features a sidebar navigation with the following pages:

- **🏠 Home**: Welcome page with overview
- **📊 Check Stats**: Player and team statistics
- **📰 News**: Latest NBA news articles

- **🎯 Predict**: Game predictions and analytics
- **🏆 Ranking**: Team standings and rankings

### Vector Search Features
The application includes advanced semantic search capabilities:

- **News Embeddings**: AI-generated vector representations of news articles
- **Similarity Search**: Find related news using cosine similarity
- **Real-time Processing**: Generate embeddings for new articles automatically

## 🗄️ Database Structure

### Core Tables
- **News**: NBA news articles with metadata
- **VectorNews**: Vector embeddings for semantic search
- **Players**: Player statistics and information
- **Teams**: Team data and performance metrics
- **Matches**: Game results and statistics

### Vector Schema
```sql
CREATE TABLE "NBA"."VectorNews" (
    "NewsID" integer NOT NULL,
    "NewsVector" vector NOT NULL,
    CONSTRAINT "VectorNews_pkey" PRIMARY KEY ("NewsID")
);
```

## 🔧 Configuration

### Database Connection
- **Host**: localhost
- **Database**: James
- **Schema**: NBA
- **Username**: postgres
- **Password**: jcjc1749

### Environment Variables
Set the following environment variables or modify the connection strings in the code:
- `POSTGRES_HOST`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

## 📁 Project Structure

```
nbapredict/
├── Home.py                          # Main Streamlit application
├── pages/                           # Application pages
│   ├── Check_Stats.py              # Statistics dashboard
│   ├── News.py                     # News display

│   ├── Predict.py                  # Game predictions
│   └── Ranking.py                  # Team rankings
├── BasketballReference*.py          # Data scraping modules
├── ESPN.py                         # ESPN data integration
├── news_embedding.py               # Vector embedding generation
├── setup_vector_db.py              # Database setup utilities
├── pgvector/                       # pgvector extension source
├── requirements.txt                 # Python dependencies
└── README.md                       # This file
```

## 🧪 Testing

### Test Database Connection
```bash
python check_postgres.py
```

### Test Vector Extension
```bash
python check_pgvector.py
```

### Test Embeddings
```bash
python test_embedding.py
```

## 🚨 Troubleshooting

### Common Issues

1. **pgvector Extension Not Found**
   - Ensure PostgreSQL is running
   - Check if the extension is properly installed
   - Verify the extension files are in the correct PostgreSQL directory

2. **Ollama Connection Errors**
   - Ensure Ollama service is running on localhost:11434
   - Check if the BGE-M3 model is downloaded
   - Verify network connectivity

3. **Database Connection Issues**
   - Check PostgreSQL service status
   - Verify connection credentials
   - Ensure the NBA schema exists

### Debug Commands
```bash
# Check PostgreSQL status
python check_postgres_status.py

# Check pgvector installation
python verify_pgvector.py

# Check embedding progress
python check_embedding_progress.py
```

## 📈 Performance

- **Vector Search**: Optimized using pgvector's HNSW and IVFFlat indexes
- **Embedding Generation**: Batch processing for large datasets
- **Database Queries**: Optimized with proper indexing strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **pgvector**: PostgreSQL extension for vector operations
- **Ollama**: Local AI model hosting
- **BGE-M3**: Multilingual embedding model
- **Streamlit**: Web application framework
- **Basketball Reference**: NBA statistics data
- **ESPN**: Sports news and data

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the documentation files
3. Open an issue on GitHub
4. Check the logs in the project directory

---

**Note**: This application requires proper setup of PostgreSQL with pgvector extension and Ollama for AI embeddings. Follow the installation guide carefully for optimal performance.
