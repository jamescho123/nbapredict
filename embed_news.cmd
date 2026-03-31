@echo off
echo ============================================
echo NBA News Embedding
echo ============================================
echo.
echo This will generate vector embeddings for news articles
echo that don't have embeddings yet.
echo.
echo Embeddings are used for vector-enhanced predictions
echo to find similar teams, players, and news context.
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Starting embedding process...
echo This may take 10-30 minutes depending on article count.
echo.
python embed_news_quick.py

echo.
echo ============================================
echo Embedding complete!
echo ============================================
echo.
echo Your news articles are now ready for vector-enhanced predictions.
echo.
pause

















