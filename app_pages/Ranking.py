import streamlit as st
import pandas as pd
import plotly.express as px
from db_config import get_connection, DB_SCHEMA

def app():
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back to Home", key="back_home_ranking", type="secondary"):
            st.session_state.current_page = 'Home'
            st.rerun()
    with col2:
        st.title("NBA Rankings")

    ranking_type = st.selectbox("Select Ranking Type:", ["Team Rankings", "Player Rankings", "Power Rankings"])

    if ranking_type == "Team Rankings":
        st.subheader("NBA Team Rankings")
        conference = st.radio("Select Conference:", ["Eastern", "Western"])
        
        # Try to get real data from database
        try:
            conn = get_connection()
            query = f'''
            SELECT "TeamName", "Wins", "Losses", 
                   ROUND("Wins"::numeric / NULLIF("Wins" + "Losses", 0), 3) as "WinPct"
            FROM "{DB_SCHEMA}"."Teams"
            WHERE "Wins" IS NOT NULL AND "Losses" IS NOT NULL
            ORDER BY "WinPct" DESC, "Wins" DESC
            LIMIT 10
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
                fig = px.bar(df.head(5), x='TeamName', y='Wins', title='Top Teams by Wins', color='Wins', color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Fallback to sample data
                if conference == "Eastern":
                    standings_data = {
                        'Team': ['Celtics', 'Bucks', '76ers', 'Cavaliers', 'Knicks'],
                        'W': [45, 42, 38, 36, 35],
                        'L': [12, 15, 19, 21, 22],
                        'PCT': [.789, .737, .667, .632, .614]
                    }
                else:
                    standings_data = {
                        'Team': ['Nuggets', 'Thunder', 'Timberwolves', 'Clippers', 'Suns'],
                        'W': [43, 41, 40, 38, 37],
                        'L': [14, 16, 17, 19, 20],
                        'PCT': [.754, .719, .702, .667, .649]
                    }
                df_standings = pd.DataFrame(standings_data)
                st.dataframe(df_standings, hide_index=True)
                fig = px.bar(df_standings, x='Team', y='W', title=f'{conference} Conference Win Leaders', color='W', color_continuous_scale='Viridis')
                st.plotly_chart(fig)
        except Exception as e:
            st.warning(f"Could not load team data: {e}")
            # Fallback to sample data
            if conference == "Eastern":
                standings_data = {
                    'Team': ['Celtics', 'Bucks', '76ers', 'Cavaliers', 'Knicks'],
                    'W': [45, 42, 38, 36, 35],
                    'L': [12, 15, 19, 21, 22],
                    'PCT': [.789, .737, .667, .632, .614]
                }
            else:
                standings_data = {
                    'Team': ['Nuggets', 'Thunder', 'Timberwolves', 'Clippers', 'Suns'],
                    'W': [43, 41, 40, 38, 37],
                    'L': [14, 16, 17, 19, 20],
                    'PCT': [.754, .719, .702, .667, .649]
                }
            df_standings = pd.DataFrame(standings_data)
            st.dataframe(df_standings, hide_index=True)
            fig = px.bar(df_standings, x='Team', y='W', title=f'{conference} Conference Win Leaders', color='W', color_continuous_scale='Viridis')
            st.plotly_chart(fig)
    elif ranking_type == "Player Rankings":
        st.subheader("Player Rankings")
        st.write("""
        ### MVP Race
        1. Player A
        2. Player B
        3. Player C
        
        ### Scoring Leaders
        1. Player X
        2. Player Y
        3. Player Z
        """)
    else:
        st.subheader("Power Rankings")
        st.write("""
        ### Top 5 Teams
        1. Team A
        2. Team B
        3. Team C
        4. Team D
        5. Team E
        """) 