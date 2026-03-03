import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time

# Set page config
st.set_page_config(
    page_title="NBA Analytics",
    page_icon="🏀",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("NBA Analytics")
page = st.sidebar.radio(
    "Select a page:",
    ["Predict", "Check Stats", "News", "Ranking"]
)

def fetch_statmuse_data(query):
    try:
        # Format the query for StatMuse URL
        formatted_query = query.replace(" ", "+")
        url = f"https://www.statmuse.com/nba/ask/{formatted_query}"
        
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract data from the response
        data = []
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                data.append([col.text.strip() for col in cols])
        
        if data and len(data) > 0:
            # Clean up column names
            headers = data[0]
            # Remove empty strings and duplicates
            seen = set()
            cleaned_headers = []
            for header in headers:
                if header and header not in seen:
                    seen.add(header)
                    cleaned_headers.append(header)
                else:
                    # If duplicate, append a number
                    counter = 1
                    while f"{header}_{counter}" in seen:
                        counter += 1
                    new_header = f"{header}_{counter}"
                    seen.add(new_header)
                    cleaned_headers.append(new_header)
            
            # Create DataFrame with cleaned headers
            df = pd.DataFrame(data[1:], columns=cleaned_headers)
            
            # Clean up the data
            # Remove any completely empty rows
            df = df.dropna(how='all')
            
            # Remove any completely empty columns
            df = df.dropna(axis=1, how='all')
            
            return df
        return None
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

# Main content area
if page == "Predict":
    st.title("NBA Game Predictions")
    
    # Game selection
    st.subheader("Select Teams")
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("Home Team:", 
            ['Lakers', 'Celtics', 'Warriors', 'Bucks', 'Heat', 'Nuggets', 'Suns'])
    
    with col2:
        away_team = st.selectbox("Away Team:", 
            ['Lakers', 'Celtics', 'Warriors', 'Bucks', 'Heat', 'Nuggets', 'Suns'])
    
    if st.button("Predict Winner"):
        st.subheader("Prediction Results")
        st.write("Based on current team performance and historical data:")
        # Add prediction logic here
        st.write(f"Predicted Winner: {home_team} (65% confidence)")
        
        # Show prediction factors
        st.write("Key Factors:")
        st.write("- Home Court Advantage")
        st.write("- Recent Performance")
        st.write("- Head-to-Head Record")
        st.write("- Team Injuries")

elif page == "Check Stats":
    st.title("NBA Statistics")
    
    # Statistics type selection
    stat_type = st.selectbox("Select Statistics Type:", 
        ["Player Stats", "Team Stats", "Game Stats"])
    
    if stat_type == "Player Stats":
        st.subheader("Player Statistics")
        
        # Query input for StatMuse
        query = st.text_input("Enter your StatMuse query (e.g., 'who leads the nba in points per game')")
        
        if query:
            with st.spinner("Fetching data from StatMuse..."):
                df = fetch_statmuse_data(query)
                
                if df is not None and not df.empty:
                    st.dataframe(df, hide_index=True)
                    
                    # Create visualization if there's numerical data
                    if len(df.columns) >= 2:
                        try:
                            # Try to find a numeric column for visualization
                            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                            if len(numeric_cols) > 0:
                                # Use the first numeric column for visualization
                                y_col = numeric_cols[0]
                                x_col = df.columns[0]  # Use the first column as x-axis
                                
                                # Convert data to numeric, handling any errors
                                df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
                                
                                fig = px.bar(df, x=x_col, y=y_col, 
                                           title=f'{y_col} by {x_col}')
                                st.plotly_chart(fig)
                        except Exception as e:
                            st.write(f"Could not create visualization: {str(e)}")
                else:
                    st.warning("No data found for the given query")
        
        # Example queries
        st.subheader("Example Queries")
        st.write("""
        Try these example queries:
        - who leads the nba in points per game
        - who leads the nba in assists
        - who leads the nba in rebounds
        - who leads the nba in steals
        - who leads the nba in blocks
        """)
    
    elif stat_type == "Team Stats":
        st.subheader("Team Statistics")
        
        # Query input for team stats
        query = st.text_input("Enter your StatMuse query (e.g., 'which team has the best record in the nba')")
        
        if query:
            with st.spinner("Fetching data from StatMuse..."):
                df = fetch_statmuse_data(query)
                
                if df is not None and not df.empty:
                    st.dataframe(df, hide_index=True)
                    
                    # Create visualization if there's numerical data
                    if len(df.columns) >= 2:
                        try:
                            # Try to find a numeric column for visualization
                            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                            if len(numeric_cols) > 0:
                                # Use the first numeric column for visualization
                                y_col = numeric_cols[0]
                                x_col = df.columns[0]  # Use the first column as x-axis
                                
                                # Convert data to numeric, handling any errors
                                df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
                                
                                fig = px.bar(df, x=x_col, y=y_col, 
                                           title=f'{y_col} by {x_col}')
                                st.plotly_chart(fig)
                        except Exception as e:
                            st.write(f"Could not create visualization: {str(e)}")
                else:
                    st.warning("No data found for the given query")
        
        # Example queries
        st.subheader("Example Queries")
        st.write("""
        Try these example queries:
        - which team has the best record in the nba
        - which team scores the most points per game
        - which team has the best defense
        - which team has the most wins
        """)
    
    else:
        st.subheader("Game Statistics")
        
        # Query input for game stats
        query = st.text_input("Enter your StatMuse query (e.g., 'what was the highest scoring game this season')")
        
        if query:
            with st.spinner("Fetching data from StatMuse..."):
                df = fetch_statmuse_data(query)
                
                if df is not None and not df.empty:
                    st.dataframe(df, hide_index=True)
                else:
                    st.warning("No data found for the given query")
        
        # Example queries
        st.subheader("Example Queries")
        st.write("""
        Try these example queries:
        - what was the highest scoring game this season
        - what was the biggest margin of victory this season
        - what was the lowest scoring game this season
        - what was the most points scored by a team in a game
        """)

elif page == "News":
    st.title("NBA News")
    
    # News categories
    category = st.radio("Select Category:", 
        ["Latest News", "Trade Rumors", "Injury Updates", "Game Recaps"])
    
    if category == "Latest News":
        st.subheader("Latest NBA News")
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

elif page == "Ranking":
    st.title("NBA Rankings")
    
    # Ranking type selection
    ranking_type = st.selectbox("Select Ranking Type:", 
        ["Team Rankings", "Player Rankings", "Power Rankings"])
    
    if ranking_type == "Team Rankings":
        st.subheader("NBA Team Rankings")
        conference = st.radio("Select Conference:", ["Eastern", "Western"])
        
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
        
        fig = px.bar(df_standings, x='Team', y='W', 
                     title=f'{conference} Conference Win Leaders',
                     color='W',
                     color_continuous_scale='Viridis')
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

# Add some styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True) 