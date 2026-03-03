import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Import database prediction system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_prediction import get_team_list, predict_game_outcome, get_team_context_data

def app():
    """Main simplified prediction interface using database data"""
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back to Home", key="back_home_simple", type="secondary"):
            st.session_state.current_page = 'Home'
            st.rerun()
    with col2:
        st.title("🏀 NBA Game Prediction")
    st.markdown("**AI-powered predictions based on real NBA data**")
    
    # Get teams from database
    with st.spinner("Loading teams from database..."):
        teams = get_team_list()
    
    if not teams:
        st.error("No teams found in database. Please check your database connection.")
        return
    
    # Simple team selection
    st.header("Select Teams")
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("Home Team", teams, index=0)
    
    with col2:
        away_team = st.selectbox("Away Team", [t for t in teams if t != home_team], index=1)
    
    # Show team information
    st.header("Team Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"🏠 {home_team}")
        try:
            home_context = get_team_context_data(home_team)
            
            # Ensure context is not None
            if home_context is None:
                home_context = {}
            
            if home_context and home_context.get('team_stats'):
                stats = home_context['team_stats']
                wins = stats.get('Wins', 0)
                losses = stats.get('Losses', 0)
                if wins > 0 or losses > 0:
                    st.metric("Record", f"{wins}-{losses}")
                    win_pct = wins / (wins + losses) if (wins + losses) > 0 else 0
                    st.metric("Win %", f"{win_pct:.1%}")
                    st.metric("Points For", f"{stats.get('PointsFor', 0)}")
                    st.metric("Points Against", f"{stats.get('PointsAgainst', 0)}")
                else:
                    st.info("No season record available")
            else:
                st.info("No team stats available in database")
            
            recent_form = home_context.get('recent_form', {}) if home_context else {}
            recent_wins = recent_form.get('wins', 0)
            recent_losses = recent_form.get('losses', 0)
            if recent_wins > 0 or recent_losses > 0:
                st.metric("Recent Form", f"{recent_wins}-{recent_losses}")
                st.metric("Recent Win %", f"{recent_form.get('win_percentage', 0):.1%}")
            else:
                st.info("No recent games found")
                
            # Show recent news count
            news = home_context.get('news', []) if home_context else []
            if news:
                st.metric("Recent News", f"{len(news)} articles")
            else:
                st.info("No recent news found")
                
        except Exception as e:
            st.error(f"Error loading {home_team} data: {e}")
            st.info("Database connection issue")
    
    with col2:
        st.subheader(f"✈️ {away_team}")
        try:
            away_context = get_team_context_data(away_team)
            
            # Ensure context is not None
            if away_context is None:
                away_context = {}
            
            if away_context and away_context.get('team_stats'):
                stats = away_context['team_stats']
                wins = stats.get('Wins', 0)
                losses = stats.get('Losses', 0)
                if wins > 0 or losses > 0:
                    st.metric("Record", f"{wins}-{losses}")
                    win_pct = wins / (wins + losses) if (wins + losses) > 0 else 0
                    st.metric("Win %", f"{win_pct:.1%}")
                    st.metric("Points For", f"{stats.get('PointsFor', 0)}")
                    st.metric("Points Against", f"{stats.get('PointsAgainst', 0)}")
                else:
                    st.info("No season record available")
            else:
                st.info("No team stats available in database")
            
            recent_form = away_context.get('recent_form', {}) if away_context else {}
            recent_wins = recent_form.get('wins', 0)
            recent_losses = recent_form.get('losses', 0)
            if recent_wins > 0 or recent_losses > 0:
                st.metric("Recent Form", f"{recent_wins}-{recent_losses}")
                st.metric("Recent Win %", f"{recent_form.get('win_percentage', 0):.1%}")
            else:
                st.info("No recent games found")
                
            # Show recent news count
            news = away_context.get('news', []) if away_context else []
            if news:
                st.metric("Recent News", f"{len(news)} articles")
            else:
                st.info("No recent news found")
                
        except Exception as e:
            st.error(f"Error loading {away_team} data: {e}")
            st.info("Database connection issue")
    
    # Prediction button
    st.markdown("---")
    if st.button("🎯 Get Prediction", type="primary", use_container_width=True):
        with st.spinner("Analyzing team data and generating prediction..."):
            try:
                # Make prediction using database data
                prediction = predict_game_outcome(home_team, away_team)
                
                if prediction:
                    # Display results
                    display_prediction_results(prediction)
                else:
                    st.error("Failed to generate prediction. Please check your database connection.")
                
            except Exception as e:
                st.error(f"Prediction failed: {e}")
                st.write("This might be due to database connection issues or missing data.")
                st.exception(e)

def display_prediction_results(prediction):
    """Display prediction results with database information"""
    st.markdown("---")
    st.header("🎯 Prediction Result")
    
    winner = prediction['predicted_winner']
    confidence = prediction['confidence']
    
    # Main result display
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if winner == prediction['home_team']:
            st.success(f"🏠 **{winner}** wins at home")
        else:
            st.info(f"✈️ **{winner}** wins away")
        
        # Confidence bar
        st.progress(confidence)
        st.write(f"**Confidence: {confidence:.1%}**")
    
    # Database Information Used
    st.subheader("📊 Database Information Used in Prediction")
    
    # Get fresh team data to show what was actually used
    try:
        home_context = get_team_context_data(prediction['home_team'])
        away_context = get_team_context_data(prediction['away_team'])
        
        # Ensure contexts are not None
        if home_context is None:
            home_context = {}
        if away_context is None:
            away_context = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{prediction['home_team']} Database Stats:**")
            if home_context and home_context.get('team_stats'):
                stats = home_context['team_stats']
                st.write(f"• Season Record: {stats.get('Wins', 0)}-{stats.get('Losses', 0)}")
                win_pct = stats.get('Wins', 0) / (stats.get('Wins', 0) + stats.get('Losses', 0)) if (stats.get('Wins', 0) + stats.get('Losses', 0)) > 0 else 0
                st.write(f"• Win Percentage: {win_pct:.1%}")
                st.write(f"• Points For: {stats.get('PointsFor', 0)}")
                st.write(f"• Points Against: {stats.get('PointsAgainst', 0)}")
            else:
                st.write("• No season stats available in database")
            
            recent_form = home_context.get('recent_form', {}) if home_context else {}
            st.write(f"• Recent Form: {recent_form.get('wins', 0)}-{recent_form.get('losses', 0)}")
            st.write(f"• Recent Win %: {recent_form.get('win_percentage', 0):.1%}")
            
            # Show recent news
            news = home_context.get('news', []) if home_context else []
            if news:
                st.write(f"• Recent News Articles: {len(news)}")
                for i, article in enumerate(news[:2]):  # Show first 2 articles
                    st.write(f"  - {article.get('Title', 'No title')[:50]}...")
            else:
                st.write("• No recent news found")
        
        with col2:
            st.write(f"**{prediction['away_team']} Database Stats:**")
            if away_context and away_context.get('team_stats'):
                stats = away_context['team_stats']
                st.write(f"• Season Record: {stats.get('Wins', 0)}-{stats.get('Losses', 0)}")
                win_pct = stats.get('Wins', 0) / (stats.get('Wins', 0) + stats.get('Losses', 0)) if (stats.get('Wins', 0) + stats.get('Losses', 0)) > 0 else 0
                st.write(f"• Win Percentage: {win_pct:.1%}")
                st.write(f"• Points For: {stats.get('PointsFor', 0)}")
                st.write(f"• Points Against: {stats.get('PointsAgainst', 0)}")
            else:
                st.write("• No season stats available in database")
            
            recent_form = away_context.get('recent_form', {}) if away_context else {}
            st.write(f"• Recent Form: {recent_form.get('wins', 0)}-{recent_form.get('losses', 0)}")
            st.write(f"• Recent Win %: {recent_form.get('win_percentage', 0):.1%}")
            
            # Show recent news
            news = away_context.get('news', []) if away_context else []
            if news:
                st.write(f"• Recent News Articles: {len(news)}")
                for i, article in enumerate(news[:2]):  # Show first 2 articles
                    st.write(f"  - {article.get('Title', 'No title')[:50]}...")
            else:
                st.write("• No recent news found")
    
    except Exception as e:
        st.warning(f"Could not load detailed database information: {e}")
        st.write("• Database connection issue - using fallback data")
    
    # Team strength comparison
    st.subheader("Team Strength Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(f"{prediction['home_team']} Strength", f"{prediction['home_strength']:.3f}")
    
    with col2:
        st.metric(f"{prediction['away_team']} Strength", f"{prediction['away_strength']:.3f}")
    
    # Create strength comparison chart
    strength_data = {
        'Team': [prediction['home_team'], prediction['away_team']],
        'Strength': [prediction['home_strength'], prediction['away_strength']]
    }
    
    fig = px.bar(
        strength_data, 
        x='Team', 
        y='Strength',
        title="Team Strength Comparison",
        color='Strength',
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Head-to-head record
    h2h = prediction['head_to_head']
    if h2h['total_games'] > 0:
        st.subheader("Head-to-Head Record (From Database)")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(f"{prediction['home_team']} Wins", h2h['team1_wins'])
        
        with col2:
            st.metric("Total Games", h2h['total_games'])
        
        with col3:
            st.metric(f"{prediction['away_team']} Wins", h2h['team2_wins'])
    else:
        st.info("No head-to-head record found in database")
    
    # Recent form comparison
    st.subheader("Recent Form Comparison (From Database)")
    col1, col2 = st.columns(2)
    
    with col1:
        home_form = prediction['home_form']
        st.write(f"**{prediction['home_team']}**")
        if home_form.get('total_games', 0) > 0:
            st.write(f"Record: {home_form['wins']}-{home_form['losses']}")
            st.write(f"Win %: {home_form['win_percentage']:.1%}")
        else:
            st.write("No recent games found in database")
    
    with col2:
        away_form = prediction['away_form']
        st.write(f"**{prediction['away_team']}**")
        if away_form.get('total_games', 0) > 0:
            st.write(f"Record: {away_form['wins']}-{away_form['losses']}")
            st.write(f"Win %: {away_form['win_percentage']:.1%}")
        else:
            st.write("No recent games found in database")
    
    # Key factors with database references
    st.subheader("Key Factors (Based on Database Analysis)")
    
    factors = []
    if prediction['home_strength'] > prediction['away_strength'] + 0.1:
        factors.append(f"📈 {prediction['home_team']} has stronger overall performance (from season stats)")
    elif prediction['away_strength'] > prediction['home_strength'] + 0.1:
        factors.append(f"📈 {prediction['away_team']} has stronger overall performance (from season stats)")
    
    if prediction['home_form']['win_percentage'] > prediction['away_form']['win_percentage'] + 0.2:
        factors.append(f"🔥 {prediction['home_team']} has better recent form (from recent games)")
    elif prediction['away_form']['win_percentage'] > prediction['home_form']['win_percentage'] + 0.2:
        factors.append(f"🔥 {prediction['away_team']} has better recent form (from recent games)")
    
    if h2h['total_games'] > 0:
        if h2h['team1_wins'] > h2h['team2_wins']:
            factors.append(f"📊 {prediction['home_team']} leads head-to-head series (from match history)")
        elif h2h['team2_wins'] > h2h['team1_wins']:
            factors.append(f"📊 {prediction['away_team']} leads head-to-head series (from match history)")
    
    factors.append("🏠 Home court advantage considered")
    
    if factors:
        for factor in factors:
            st.write(f"• {factor}")
    else:
        st.write("• Balanced matchup with multiple factors")

if __name__ == "__main__":
    app()