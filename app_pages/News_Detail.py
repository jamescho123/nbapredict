import streamlit as st
import psycopg2
import pandas as pd
import os
from db_config import get_connection, DB_SCHEMA

def app(news_id=None):
    if not news_id:
        if 'selected_news_id' in st.session_state:
            news_id = st.session_state.selected_news_id
        else:
            st.error("No news article selected.")
            if st.button("🏠 Back to Home"):
                st.session_state.current_page = 'Home'
                st.rerun()
            return

    # Fetch news details
    try:
        conn = get_connection()
        query = f'''
        SELECT "Title", "Content", "Date", "Source", "Author", "URL", "ImageURL"
        FROM "{DB_SCHEMA}"."News"
        WHERE "NewsID" = %s
        '''
        df = pd.read_sql_query(query, conn, params=[news_id])
        conn.close()

        if df.empty:
            st.error("News article not found.")
            return

        article = df.iloc[0]

        # UI
        if st.button("← Back"):
            # Clear query params and return
            st.query_params.clear()
            st.session_state.current_page = 'Home'
            st.rerun()

        st.markdown(f"# {article['Title']}")
        st.caption(f"📅 {article['Date']} | 👤 {article['Author'] if article['Author'] else 'NBA Staff'} | 📰 {article['Source']}")
        
        # Display image if available
        image_url = article.get('ImageURL')
        if image_url:
            if os.path.exists(image_url):
                st.image(image_url, use_container_width=True)
            elif image_url.startswith("http"):
                st.image(image_url, use_container_width=True)
        
        st.divider()
        
        # Display full content
        st.write(article['Content'])
        
        if article['URL']:
            st.markdown(f"[Read original source]({article['URL']})")

    except Exception as e:
        st.error(f"Error loading news article: {e}")
