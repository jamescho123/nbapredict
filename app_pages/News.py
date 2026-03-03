import streamlit as st
from db_config import get_connection, DB_SCHEMA
import pandas as pd
import os

def app():
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back to Home", key="back_home_news", type="secondary"):
            st.session_state.current_page = 'Home'
            st.rerun()
    with col2:
        st.title("NBA News")
    
    category = st.radio("Select Category:", ["Latest News", "Trade Rumors", "Injury Updates", "Game Recaps"])
    
    if category == "Latest News":
        st.subheader("Latest NBA News")
        # Fetch real news from database
        try:
            conn = get_connection()
            query = f'''
            SELECT "NewsID", "Title", "Content", "Date", "Source", "URL", "ImageURL"
            FROM "{DB_SCHEMA}"."News"
            ORDER BY "Date" DESC
            LIMIT 20
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                for idx, row in df.iterrows():
                    date_str = str(row['Date'])[:10] if row['Date'] else "Recent"
                    title_text = row.get('Title', 'No Title')
                    news_id = row.get('NewsID')
                    image_url = row.get('ImageURL')
                    
                    # Add icon if image exists
                    img_icon = " 🖼️" if image_url else ""
                        
                    with st.expander(f"{title_text} - {date_str}{img_icon}"):
                        # Display image if available
                        if image_url:
                            if os.path.exists(image_url):
                                st.image(image_url, use_container_width=True)
                            elif image_url.startswith("http"):
                                st.image(image_url, use_container_width=True)
                        
                        st.write(f"**Source:** {row.get('Source', 'NBA')}")
                        st.write(f"**Date:** {date_str}")
                        st.write(row.get('Content', 'No content available')[:400] + "...")
                        
                        if st.button(f"Read Full Story", key=f"news_page_read_{news_id}"):
                            st.session_state.current_page = 'News Detail'
                            st.session_state.selected_news_id = news_id
                            st.rerun()
            else:
                st.info("No news articles available in the database.")
        except Exception as e:
            st.error(f"Error loading news: {e}")
            st.write("""
            ### Breaking News
            - NBA Announces New TV Deal
            - All-Star Game Format Changes
            
            ### Top Stories
            - Playoff Race Heats Up
            - Rookie of the Year Race
            - MVP Candidates
            """)
    elif category == "Trade Rumors":
        st.subheader("Trade Rumors and Updates")
        st.write("""
        - Trade Deadline Approaching
        - Team X Interested in Player Y
        - Potential Blockbuster Deals
        """)
    elif category == "Injury Updates":
        st.subheader("Injury Reports")
        st.write("""
        - Player A: Out 2-3 weeks
        - Player B: Day-to-day
        - Player C: Expected to return next game
        """)
    else:
        st.subheader("Game Recaps")
        st.write("""
        - Lakers vs Celtics: OT Thriller
        - Warriors Extend Win Streak
        - Bucks Dominate at Home
        """) 