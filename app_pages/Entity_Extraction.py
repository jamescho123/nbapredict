import streamlit as st
import pandas as pd
from datetime import datetime
import json
from news_entity_processor import NewsEntityProcessor
from nba_entity_extractor import NBAEntityExtractor
from nba_entity_extractor_offline import NBAEntityExtractorOffline

from nba_supabase_auth import check_authentication, is_admin

def app():
    # Check authentication and admin status
    if not check_authentication():
        st.warning("Please login to access this page")
        st.stop()
    
    if not is_admin():
        st.error("🔒 Access Denied: This page is only available to administrators.")
        st.stop()

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back to Home", key="back_home_entity", type="secondary"):
            st.session_state.current_page = 'Home'
            st.rerun()
    with col2:
        st.title("🏀 NBA News Entity Extraction")
    st.write("Transform messy NBA news into structured data using LLM-powered entity recognition")
    
    processor = NewsEntityProcessor()
    extractor = NBAEntityExtractor()
    offline_extractor = NBAEntityExtractorOffline()
    
    # Sidebar controls
    st.sidebar.header("Controls")
    
    # Process existing news
    if st.sidebar.button("Process Existing News"):
        with st.spinner("Processing existing news articles..."):
            result = processor.process_existing_news(limit=10)
            st.success(f"Processed {result['processed']} articles, skipped {result['skipped']}, failed {result['failed']}")
    
    # Force reprocess
    if st.sidebar.button("Force Reprocess All"):
        with st.spinner("Force reprocessing all news articles..."):
            result = processor.process_existing_news(limit=50, force_reprocess=True)
            st.success(f"Processed {result['processed']} articles, skipped {result['skipped']}, failed {result['failed']}")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Statistics", 
        "🔍 Entity Search", 
        "🏥 Injuries", 
        "⚖️ Penalties", 
        "📝 Process New Article"
    ])
    
    with tab1:
        st.header("Entity Extraction Statistics")
        
        stats = processor.get_entity_statistics()
        
        if stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total News Articles", stats.get("total_news_articles", 0))
            
            with col2:
                st.metric("Total Entities", stats.get("total_entities", 0))
            
            with col3:
                st.metric("Total Mentions", stats.get("total_mentions", 0))
            
            # Entity type distribution
            if "entity_counts" in stats:
                st.subheader("Entity Types Distribution")
                entity_df = pd.DataFrame(
                    list(stats["entity_counts"].items()),
                    columns=["Entity Type", "Count"]
                )
                st.bar_chart(entity_df.set_index("Entity Type"))
        else:
            st.warning("No statistics available. Process some news articles first.")
    
    with tab2:
        st.header("Search Entities")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input("Search for entities:", placeholder="e.g., LeBron, Lakers, injury")
        
        with col2:
            entity_type = st.selectbox(
                "Filter by type:",
                ["All", "player", "team", "injury", "penalty", "stat", "conflict", "trade", "award", "location", "date"]
            )
        
        if search_query:
            entity_type_filter = None if entity_type == "All" else entity_type
            
            with st.spinner("Searching..."):
                results = processor.search_entities(search_query, entity_type_filter, limit=20)
            
            if results:
                st.subheader(f"Found {len(results)} entities")
                
                for result in results:
                    with st.expander(f"{result['name']} ({result['type']}) - {result['mention_count']} mentions"):
                        st.json(result['props'])
            else:
                st.info("No entities found matching your search.")
    
    with tab3:
        st.header("Latest Player Injuries")
        
        with st.spinner("Loading injuries..."):
            try:
                injuries = extractor.get_latest_injuries(limit=20)
            except:
                injuries = offline_extractor.get_latest_injuries(limit=20)
        
        if injuries:
            st.subheader(f"Found {len(injuries)} injury reports")
            
            for injury in injuries:
                with st.expander(f"{injury['player']} - {injury['injury']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Player:** {injury['player']}")
                        st.write(f"**Injury:** {injury['injury']}")
                        st.write(f"**Status:** {injury['status']}")
                    
                    with col2:
                        st.write(f"**Source:** {injury['title']}")
                        st.write(f"**Date:** {injury['published_at']}")
        else:
            st.info("No injury reports found. Process some news articles first.")
    
    with tab4:
        st.header("Recent Technical Fouls")
        
        with st.spinner("Loading penalties..."):
            try:
                fouls = extractor.get_technical_fouls(limit=20)
            except:
                fouls = offline_extractor.get_technical_fouls(limit=20)
        
        if fouls:
            st.subheader(f"Found {len(fouls)} technical fouls")
            
            for foul in fouls:
                with st.expander(f"{foul['player']} - {foul['penalty']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Player:** {foul['player']}")
                        st.write(f"**Penalty:** {foul['penalty']}")
                    
                    with col2:
                        st.write(f"**Source:** {foul['title']}")
                        st.write(f"**Date:** {foul['published_at']}")
        else:
            st.info("No technical fouls found. Process some news articles first.")
    
    with tab5:
        st.header("Process New Article")
        
        st.write("Enter a new NBA news article to extract entities from:")
        
        title = st.text_input("Article Title:", placeholder="e.g., Lakers Edge Warriors in Thriller")
        
        content = st.text_area(
            "Article Content:", 
            placeholder="Paste the full article content here...",
            height=200
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            url = st.text_input("Article URL (optional):", placeholder="https://...")
        
        with col2:
            source = st.text_input("Source:", value="manual", placeholder="e.g., ESPN, NBA.com")
        
        if st.button("Extract Entities", type="primary"):
            if title and content:
                with st.spinner("Processing article and extracting entities..."):
                    success = processor.process_new_article(
                        title=title,
                        content=content,
                        url=url if url else None,
                        source=source
                    )
                
                if success:
                    st.success("Article processed successfully! Entities have been extracted and stored.")
                    
                    # Show extracted entities
                    st.subheader("Extracted Entities Preview")
                    
                    # Extract entities for preview
                    extracted_data = extractor.extract_entities(content, title)
                    if extracted_data:
                        entities = extracted_data.get("entities", [])
                        
                        if entities:
                            entity_df = pd.DataFrame(entities)
                            st.dataframe(entity_df[["type", "name", "details"]], use_container_width=True)
                        else:
                            st.info("No entities were extracted from this article.")
                    else:
                        st.warning("Failed to extract entities. Check the LLM connection.")
                else:
                    st.error("Failed to process article. Check the logs for details.")
            else:
                st.error("Please provide both title and content.")
    
    # Footer
    st.markdown("---")
    st.markdown("**Entity Types Supported:**")
    st.markdown("""
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
    """)
