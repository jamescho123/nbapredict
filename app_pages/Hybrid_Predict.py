import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Import our hybrid model
from hybrid_model import HybridModel, prepare_match_data, prepare_player_data, prepare_news_data
from hybrid_model_config import ENSEMBLE_CONFIG, FEATURE_CONFIG

# Import database prediction system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_prediction import (
    get_team_list, predict_game_outcome, get_team_context_data,
    get_upcoming_games, get_games_today, get_games_this_week,
    get_games_by_date_range
)

# Import entity extraction and query processing
from query_processor import QueryProcessor
from nba_entity_extractor_offline import NBAEntityExtractorOffline

# Import vector embedding system
from vector_enhanced_prediction import VectorEnhancedPredictionSystem

def load_vector_enhanced_system():
    """Load or initialize the vector enhanced prediction system"""
    if 'vector_system' not in st.session_state:
        try:
            st.session_state.vector_system = VectorEnhancedPredictionSystem()
            if st.session_state.vector_system.connect_to_database():
                st.session_state.vector_system.load_embeddings()
                st.success("✅ Vector enhanced prediction system loaded!")
            else:
                st.warning("⚠️ Vector system loaded but database connection failed")
        except Exception as e:
            st.error(f"Failed to initialize vector system: {e}")
            return None
    return st.session_state.vector_system

def load_hybrid_model():
    """Load or initialize the hybrid model"""
    if 'hybrid_model' not in st.session_state:
        try:
            # Initialize the model
            st.session_state.hybrid_model = HybridModel(
                weights=ENSEMBLE_CONFIG['default_weights']
            )
            st.success("✅ Hybrid model initialized successfully!")
        except Exception as e:
            st.error(f"Failed to initialize hybrid model: {e}")
            return None
    
    # Check if model is fitted, if not, fit it with sample data
    if not st.session_state.hybrid_model.is_fitted:
        with st.spinner("Training hybrid model with sample data..."):
            try:
                # Create sample data for training
                sample_data = create_sample_training_data()
                
                # Train the model
                st.session_state.hybrid_model.fit(
                    matches_data=sample_data['matches'],
                    players_data=sample_data['players'],
                    teams_data=sample_data['teams'],
                    news_data=sample_data['news']
                )
                st.success("✅ Hybrid model trained successfully!")
            except Exception as e:
                st.error(f"Failed to train hybrid model: {e}")
                return None
    
    return st.session_state.hybrid_model

def create_sample_training_data():
    """Create sample training data for the hybrid model"""
    import numpy as np
    import pandas as pd
    
    # Sample matches data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    teams = ['Lakers', 'Warriors', 'Celtics', 'Heat', 'Bulls', 'Knicks', 'Nets', 'Suns']
    
    matches_data = []
    for i in range(100):
        home_team = np.random.choice(teams)
        away_team = np.random.choice([t for t in teams if t != home_team])
        home_score = np.random.randint(90, 130)
        away_score = np.random.randint(90, 130)
        
        matches_data.append({
            'date': dates[i],
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score
        })
    
    matches_df = pd.DataFrame(matches_data)
    
    # Sample players data
    players_data = []
    for team in teams:
        for i in range(8):  # 8 players per team
            players_data.append({
                'PlayerName': f'Player_{team}_{i+1}',
                'Team': team,
                'Points': np.random.randint(5, 30),
                'GamesPlayed': np.random.randint(20, 82),
                'Assists': np.random.randint(1, 10),
                'Rebounds': np.random.randint(1, 12),
                'points_per_game': np.random.randint(5, 30) / np.random.randint(20, 82)
            })
    
    players_df = pd.DataFrame(players_data)
    
    # Sample teams data
    teams_data = []
    for team in teams:
        wins = np.random.randint(20, 60)
        losses = 82 - wins
        teams_data.append({
            'TeamName': team,
            'Wins': wins,
            'Losses': losses,
            'PointsFor': np.random.randint(8000, 12000),
            'PointsAgainst': np.random.randint(8000, 12000)
        })
    
    teams_df = pd.DataFrame(teams_data)
    
    # Sample news data
    news_data = []
    news_templates = [
        "{} shows impressive performance in recent games",
        "{} struggles with injuries this season",
        "{} makes strategic changes to lineup",
        "{} player returns from suspension",
        "{} faces tough competition in upcoming matches"
    ]
    
    for i in range(50):
        team = np.random.choice(teams)
        template = np.random.choice(news_templates)
        title = template.format(team)
        content = f"This is a detailed news article about {team}. " + \
                 f"The team has been performing well and shows great potential for the season."
        
        news_data.append({
            'NewsID': i + 1,
            'Title': title,
            'Content': content
        })
    
    news_df = pd.DataFrame(news_data)
    
    # Prepare data
    prepared_matches = prepare_match_data(matches_df)
    prepared_players = prepare_player_data(players_df)
    prepared_news = prepare_news_data(news_df)
    
    return {
        'matches': prepared_matches,
        'players': prepared_players,
        'teams': teams_df,
        'news': prepared_news
    }

def create_sample_player_stats(home_team, away_team):
    """Create sample player statistics for demonstration"""
    np.random.seed(42)
    
    players_data = []
    for team in [home_team, away_team]:
        for i in range(8):  # 8 players per team
            players_data.append({
                'PlayerName': f'Player_{team}_{i+1}',
                'Team': team,
                'Points': np.random.randint(5, 30),
                'GamesPlayed': np.random.randint(20, 82),
                'Assists': np.random.randint(1, 10),
                'Rebounds': np.random.randint(1, 12)
            })
    
    return pd.DataFrame(players_data)

def app():
    """Main hybrid prediction interface with side-by-side layout"""
    top_col1, top_col2 = st.columns([1, 5])
    with top_col1:
        if st.button("← Back to Home", key="back_home_hybrid", type="secondary"):
            st.session_state.current_page = 'Home'
            st.rerun()
    with top_col2:
        st.title("🏀 NBA Hybrid Predictions")
        
        with st.expander("ℹ️ How This Works", expanded=True):
            st.markdown("""
            ### The Hybrid Ensemble Model
            This system predicts game outcomes by aggregating **four independent analytical engines**. You can adjust the weight of each engine in the sidebar to customize the prediction logic.
            
            1.  **📉 Time Series Model (Trend Analysis)**
                *analyzes historical momentum, winning streaks, and head-to-head history.*
            2.  **📊 Statistical Model (Efficiency Metrics)**
                *evaluates offensive/defensive ratings, player efficiency (PER), and team comparisons.*
            3.  **📰 Sentiment Model (News Analysis)**
                *scans recent news articles to gauge team morale, injury impact, and media sentiment.*
            4.  **🧠 LLM Model (Strategic Reasoning)**
                *uses a Large Language Model to synthesize intangible factors, matchups, and expert context.*
            
            **Combined with Vector Search:** The system also looks for **historically similar games** (e.g., "How did strong home teams fare against tired away teams?") to further refine the confidence score.
            """)
    
    st.header("🎮 Game Selection")
    st.markdown("---")
    with st.container():
        create_game_selection_interface()

    st.header("🎯 Prediction Results")
    st.markdown("---")
    if st.session_state.get('show_prediction') and st.session_state.get('selected_game'):
        display_game_prediction(st.session_state.selected_game)
    else:
        st.info("Select a game above to see predictions")
        st.markdown("""
        ### How to use:
        1. **Browse games** in the selector above
        2. **Choose a matchup** from the list
        3. **View detailed predictions** here
        4. **Use filters** to find specific games
        """)
    
    # Create tabs for additional interfaces below with more spacing
    st.markdown("---")
    st.markdown("## Additional Features")
    tab1, tab2 = st.tabs(["💬 Chat Interface", "📊 Advanced Analysis"])
    
    with tab1:
        st.markdown("""
        **AI-Powered Game Predictions with Entity Extraction**
        
        Ask me anything about NBA matchups! I'll analyze teams, extract relevant data, and provide predictions.
        
        **Examples:**
        - "Who will win, Boston Celtics or Atlanta Hawks?"
        - "Predict Lakers vs Warriors"
        - "Celtics against Hawks who wins"
        """)
        
        # Initialize session state for chat
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'query_processor' not in st.session_state:
            st.session_state.query_processor = QueryProcessor()
        
        if 'entity_extractor' not in st.session_state:
            st.session_state.entity_extractor = NBAEntityExtractorOffline()
        
        # Chat interface
        create_chat_interface()
    
    with tab2:
        create_advanced_analysis_interface()
    
    # Sidebar for additional controls
    with st.sidebar:
        st.header("Settings")
        
        # Model weights
        st.subheader("Model Weights")
        st.caption("Adjust the influence of each model on the final prediction:")
        
        time_weight = st.slider("Time Series Weight", 0.0, 1.0, 0.3, 0.05, help="Based on historical trends and momentum.")
        stat_weight = st.slider("Statistical Weight", 0.0, 1.0, 0.4, 0.05, help="Based on player efficiency, team offense/defense ratings.")
        sent_weight = st.slider("Sentiment Weight", 0.0, 1.0, 0.2, 0.05, help="Based on positive/negative tone in recent news articles.")
        llm_weight = st.slider("LLM Weight", 0.0, 1.0, 0.1, 0.05, help="Based on AI qualitative analysis of matchups and intangible factors.")
        
        # Normalize weights
        total_weight = time_weight + stat_weight + sent_weight + llm_weight
        if total_weight > 0:
            time_weight /= total_weight
            stat_weight /= total_weight
            sent_weight /= total_weight
            llm_weight /= total_weight
        
        st.session_state.model_weights = {
            'time_series': time_weight,
            'statistical': stat_weight,
            'sentiment': sent_weight,
            'llm': llm_weight
        }
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
        
        # Model insights
        if st.button("📊 Model Insights"):
            show_model_insights()
        
        # Model performance
        if st.button("📈 Model Performance"):
            show_model_performance()
        
        # Import schedule button
        if st.button("📅 Import 2025-2026 Schedule"):
            import_schedule()
        
        # Create embeddings button
        if st.button("🧠 Create Vector Embeddings"):
            create_embeddings()
        
        # Backtest analysis button
        if st.button("🧪 Run Backtest Analysis"):
            st.switch_page("pages/Backtest_Analysis.py")

def create_game_selection_interface():
    """Create the game selection interface"""
    # Set default to show all upcoming games (like NBA website)
    if 'game_filter' not in st.session_state:
        st.session_state.game_filter = "all"
    
    # Compact filter options
    st.markdown("**📅 Filter Games**")
    
    # Main filter buttons in a more compact layout
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📅 Today", type="primary" if st.session_state.game_filter == "today" else "secondary", use_container_width=True):
            st.session_state.game_filter = "today"
            st.rerun()
    
    with col2:
        if st.button("📆 Week", type="primary" if st.session_state.game_filter == "week" else "secondary", use_container_width=True):
            st.session_state.game_filter = "week"
            st.rerun()
    
    # Second row of buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔮 All", type="primary" if st.session_state.game_filter == "all" else "secondary", use_container_width=True):
            st.session_state.game_filter = "all"
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Custom date range toggle
    if st.button("🔍 Custom Date Range", use_container_width=True):
        st.session_state.show_custom_filter = not st.session_state.get('show_custom_filter', False)
        st.rerun()
    
    # Custom date range (show/hide based on toggle)
    if st.session_state.get('show_custom_filter', False):
        st.markdown("---")
        st.markdown("**🔍 Custom Range**")
        col_start, col_end = st.columns(2)
        with col_start:
            start_date = st.date_input("Start", value=None)
        with col_end:
            end_date = st.date_input("End", value=None)
        
        if st.button("🔍 Search", use_container_width=True) and start_date and end_date:
            st.session_state.game_filter = "custom"
            st.session_state.custom_start = start_date
            st.session_state.custom_end = end_date
            st.rerun()
        st.markdown("---")
    
    # Display games based on selection
    display_selected_games()

def display_selected_games():
    """Display games based on user selection"""
    
    # Get games based on filter
    if st.session_state.game_filter == "today":
        games = get_games_today()
        st.subheader("📅 Today's Games")
    elif st.session_state.game_filter == "week":
        games = get_games_this_week()
        st.subheader("📆 This Week's Games")
    elif st.session_state.game_filter == "all":
        games = get_upcoming_games(100)
        st.subheader("🔮 All Upcoming Games")
    elif st.session_state.game_filter == "custom":
        games = get_games_by_date_range(
            st.session_state.custom_start.strftime('%Y-%m-%d'),
            st.session_state.custom_end.strftime('%Y-%m-%d')
        )
        st.subheader(f"🔍 Games from {st.session_state.custom_start} to {st.session_state.custom_end}")
    else:
        games = []
    
    if not games:
        st.warning("No games found for the selected criteria.")
        return
    
    # Compact game display
    st.markdown(f"**📊 {len(games)} Games**")
    
    st.markdown(f"**📊 {len(games)} Games Found**")
    
    # Create options dict for mapping
    # Format: "TeamA @ TeamB (Date | Time)"
    game_options = {}
    game_labels = []
    
    # Sort games by date/time
    sorted_games = sorted(games, key=lambda x: (x['Date'], x.get('Time', '')))
    
    current_index = 0
    selected_label = None
    
    for g in sorted_games:
        # Create readable label
        time_str = str(g['Time'])[:5] if g.get('Time') else "TBD"
        label = f"{g['AwayTeam']} @ {g['HomeTeam']} ({g['Date']} | {time_str})"
        game_options[label] = g
        game_labels.append(label)
        
        # Check if currently selected
        if st.session_state.get('selected_game') and st.session_state['selected_game'].get('GameID') == g['GameID']:
            selected_label = label
            current_index = len(game_labels) - 1

    # Render as a "Long Select Box" using Radio
    # Render as a Dropdown Box using Selectbox
    selection = st.selectbox(
        "Select a game:",
        options=game_labels,
        index=current_index if selected_label else 0,
        label_visibility="collapsed",
        key="game_selection_box"
    )
    
    # Handle selection change
    if selection:
        selected_game = game_options[selection]
        # Only update if changed (comparing ID to avoid loops)
        current_id = st.session_state.get('selected_game', {}).get('GameID')
        if selected_game['GameID'] != current_id:
            make_prediction_for_game(selected_game)

def make_prediction_for_game(game):
    """Make a prediction for a selected game"""
    st.session_state.selected_game = game
    st.session_state.show_prediction = True
    st.rerun()

def display_game_prediction(game):
    """Display prediction results for a selected game"""
    # Game info with better styling
    st.markdown(f"## 🏀 {game['AwayTeam']} @ {game['HomeTeam']}")
    
    # Game details in a more prominent layout
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Date", str(game['Date']))
    with col2:
        st.metric("🕐 Time", str(game['Time']))
    with col3:
        st.metric("🏟️ Venue", str(game.get('Venue', 'TBD')))
    with col4:
        if st.button("❌ Close", help="Close this prediction", use_container_width=True):
            st.session_state.show_prediction = False
            st.session_state.selected_game = None
            st.rerun()
    
    st.markdown("---")
    
    # Make prediction
    with st.spinner("Analyzing teams and generating prediction..."):
        try:
            # Load vector enhanced system
            vector_system = load_vector_enhanced_system()
            
            # Generate enhanced prediction with vector insights
            if vector_system and vector_system.team_embeddings:
                enhanced_prediction = vector_system.predict_with_vector_enhancement(
                    game['HomeTeam'], game['AwayTeam']
                )
                
                # Display enhanced results
                display_enhanced_prediction(enhanced_prediction, game)
            else:
                # Fallback to traditional prediction
                prediction_result = generate_prediction_response(
                    game['HomeTeam'], 
                    game['AwayTeam'], 
                    {'is_valid_matchup': True, 'team1': game['HomeTeam'], 'team2': game['AwayTeam'], 'entities': []}
                )
                
                # Display results
                if isinstance(prediction_result, tuple):
                    response_text, chart_data = prediction_result
                    st.markdown(response_text)
                    
                    # Display charts
                    display_prediction_charts(chart_data)
                else:
                    st.markdown(prediction_result)
                
        except Exception as e:
            st.error(f"Prediction failed: {e}")

def display_enhanced_prediction(enhanced_prediction, game):
    """Display enhanced prediction with vector insights"""
    # Basic prediction info
    st.subheader("🎯 Prediction Results")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Predicted Winner", enhanced_prediction.get('predicted_winner', 'Unknown'))
    with col2:
        st.metric("Confidence", f"{enhanced_prediction.get('confidence', 0):.1%}")
    with col3:
        st.metric("Enhanced Confidence", f"{enhanced_prediction.get('enhanced_confidence', 0):.1%}")
    
    # Display win probabilities
    home_win_prob = enhanced_prediction.get('home_win_probability', 0.5)
    away_win_prob = enhanced_prediction.get('away_win_probability', 0.5)
    
    st.subheader("🎲 Win Probabilities")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"🏠 {game['HomeTeam']}", f"{home_win_prob:.1%}")
    with col2:
        st.metric(f"✈️ {game['AwayTeam']}", f"{away_win_prob:.1%}")
    
    # Show team strengths
    home_strength = enhanced_prediction.get('home_strength', 0.5)
    away_strength = enhanced_prediction.get('away_strength', 0.5)
    
    st.subheader("💪 Team Strengths")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"🏠 {game['HomeTeam']} Strength", f"{home_strength:.3f}")
    with col2:
        st.metric(f"✈️ {game['AwayTeam']} Strength", f"{away_strength:.3f}")
    
    # Vector insights
    vector_insights = enhanced_prediction.get('vector_insights', {})
    if vector_insights:
        st.subheader("🧠 Vector Analysis")
        
        # Team similarity
        team_similarity = vector_insights.get('team_similarity', 0)
        st.metric("Team Similarity", f"{team_similarity:.3f}")
        
        # Style analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"🏠 {game['HomeTeam']} Style Analysis")
            home_style = vector_insights.get('home_team_style', {})
            st.metric("Style Confidence", f"{home_style.get('style_confidence', 0):.3f}")
            
            similar_teams = home_style.get('similar_teams', [])
            if similar_teams:
                st.write("**Similar Teams:**")
                for team, similarity in similar_teams[:3]:
                    st.write(f"- {team}: {similarity:.3f}")
        
        with col2:
            st.subheader(f"✈️ {game['AwayTeam']} Style Analysis")
            away_style = vector_insights.get('away_team_style', {})
            st.metric("Style Confidence", f"{away_style.get('style_confidence', 0):.3f}")
            
            similar_teams = away_style.get('similar_teams', [])
            if similar_teams:
                st.write("**Similar Teams:**")
                for team, similarity in similar_teams[:3]:
                    st.write(f"- {team}: {similarity:.3f}")
        
        # Historical match similarity
        hist_similarity = vector_insights.get('historical_match_similarity', {})
        if hist_similarity:
            st.subheader("📊 Historical Match Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg Similarity", f"{hist_similarity.get('avg_similarity', 0):.3f}")
            with col2:
                similar_matches = hist_similarity.get('similar_matches', [])
                st.metric("Similar Matches", len(similar_matches))
            
            if similar_matches:
                st.write("**Most Similar Historical Matches:**")
                for match in similar_matches[:5]:
                    st.write(f"- {match['away_team']} @ {match['home_team']} ({match['date']}): {match['similarity']:.3f}")
    
    # Vector predictions
    vector_predictions = enhanced_prediction.get('vector_predictions', {})
    if vector_predictions:
        st.subheader("🔮 Vector-Based Predictions")
        
        # Conference advantage
        conf_advantage = vector_predictions.get('conference_advantage', {})
        if conf_advantage:
            st.write(f"**Conference Advantage:** {conf_advantage.get('advantage', 'Unknown')}")
            st.write(f"Home Team Conference Affinity: {conf_advantage.get('home_team', 0):.3f}")
            st.write(f"Away Team Conference Affinity: {conf_advantage.get('away_team', 0):.3f}")
        
        # Similarity impact
        similarity_impact = vector_predictions.get('similarity_impact', {})
        if similarity_impact:
            st.write(f"**Game Type Prediction:** {similarity_impact.get('prediction', 'Unknown')}")
            st.write(f"Similarity Score: {similarity_impact.get('similarity_score', 0):.3f}")
        
        # Historical patterns
        hist_patterns = vector_predictions.get('historical_patterns', {})
        if hist_patterns:
            st.write(f"**Historical Patterns:**")
            st.write(f"- Similar Matches Found: {hist_patterns.get('similar_matches_count', 0)}")
            st.write(f"- Average Similarity: {hist_patterns.get('avg_similarity', 0):.3f}")
            st.write(f"- High Similarity Matches: {hist_patterns.get('high_similarity_count', 0)}")
    
    # Traditional prediction details
    if 'score_predictions' in enhanced_prediction:
        st.subheader("📊 Score Predictions")
        score_pred = enhanced_prediction['score_predictions']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{game['HomeTeam']} Score", score_pred.get('home_score', 0))
        with col2:
            st.metric(f"{game['AwayTeam']} Score", score_pred.get('away_score', 0))
        with col3:
            st.metric("Total Points", score_pred.get('total_points', 0))
    
    # Gambling stats
    if 'gambling_stats' in enhanced_prediction:
        st.subheader("🎲 Gambling Statistics")
        gambling_stats = enhanced_prediction['gambling_stats']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Point Spread", f"{gambling_stats.get('point_spread', 0):.1f}")
        with col2:
            st.metric("First Half Total", gambling_stats.get('first_half_total', 0))
        with col3:
            st.metric("Overtime Probability", f"{gambling_stats.get('overtime_probability', 0):.1%}")
        with col4:
            st.metric("Margin of Victory", f"{gambling_stats.get('margin_of_victory', 0):.1f}")

def show_game_details(game):
    """Show detailed information about a game"""
    st.subheader(f"📋 Game Details: {game['AwayTeam']} @ {game['HomeTeam']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Date:** {str(game['Date'])}")
        st.write(f"**Time:** {str(game['Time'])}")
        st.write(f"**Venue:** {game['Venue']}")
        st.write(f"**Location:** {game['City']}, {game['State']}")
    
    with col2:
        st.write(f"**Game ID:** {game['GameID']}")
        st.write(f"**Status:** Scheduled")
        st.write(f"**Season:** 2025-2026")
    
    # Add prediction button
    if st.button("🎯 Make Prediction", type="primary"):
        make_prediction_for_game(game)

def show_team_comparison(game):
    """Show team comparison for a game"""
    st.subheader(f"📊 Team Comparison: {game['AwayTeam']} vs {game['HomeTeam']}")
    
    # Get team context data
    home_context = get_team_context_data(game['HomeTeam'])
    away_context = get_team_context_data(game['AwayTeam'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**🏠 {game['HomeTeam']}**")
        if home_context and home_context.get('team_stats'):
            stats = home_context['team_stats']
            st.write(f"Record: {stats.get('Wins', 0)}-{stats.get('Losses', 0)}")
            st.write(f"Points For: {stats.get('PointsFor', 0)}")
            st.write(f"Points Against: {stats.get('PointsAgainst', 0)}")
        
        recent_form = home_context.get('recent_form', {}) if home_context else {}
        if recent_form.get('total_games', 0) > 0:
            st.write(f"Recent Form: {recent_form['wins']}-{recent_form['losses']}")
    
    with col2:
        st.write(f"**✈️ {game['AwayTeam']}**")
        if away_context and away_context.get('team_stats'):
            stats = away_context['team_stats']
            st.write(f"Record: {stats.get('Wins', 0)}-{stats.get('Losses', 0)}")
            st.write(f"Points For: {stats.get('PointsFor', 0)}")
            st.write(f"Points Against: {stats.get('PointsAgainst', 0)}")
        
        recent_form = away_context.get('recent_form', {}) if away_context else {}
        if recent_form.get('total_games', 0) > 0:
            st.write(f"Recent Form: {recent_form['wins']}-{recent_form['losses']}")
    
    # Add prediction button
    if st.button("🎯 Make Prediction", type="primary"):
        make_prediction_for_game(game)

def create_advanced_analysis_interface():
    """Create advanced analysis interface"""
    st.header("📊 Advanced Analysis")
    
    st.markdown("""
    ### Available Analysis Tools
    
    - **Model Performance**: Track prediction accuracy and confidence calibration
    - **Team Statistics**: Detailed team performance metrics
    - **Schedule Analysis**: Game frequency and team rest analysis
    - **Prediction History**: View past predictions and outcomes
    """)
    
    # Analysis options
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 Model Performance Dashboard"):
            show_model_performance()
        
        if st.button("🏀 Team Statistics"):
            show_team_statistics()
    
    with col2:
        if st.button("📅 Schedule Analysis"):
            show_schedule_analysis()
        
        if st.button("📋 Prediction History"):
            show_prediction_history()

def show_team_statistics():
    """Show team statistics dashboard"""
    st.subheader("🏀 Team Statistics Dashboard")
    
    # Get all teams
    teams = get_team_list()
    if not teams:
        st.warning("No teams found in database.")
        return
    
    # Team selector
    selected_team = st.selectbox("Select Team", teams)
    
    if selected_team:
        # Get team context
        context = get_team_context_data(selected_team)
        
        if context:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Team Stats**")
                if context.get('team_stats'):
                    stats = context['team_stats']
                    st.metric("Wins", stats.get('Wins', 0))
                    st.metric("Losses", stats.get('Losses', 0))
                    st.metric("Points For", stats.get('PointsFor', 0))
                    st.metric("Points Against", stats.get('PointsAgainst', 0))
            
            with col2:
                st.write("**Recent Form**")
                recent_form = context.get('recent_form', {})
                if recent_form.get('total_games', 0) > 0:
                    st.metric("Recent Wins", recent_form['wins'])
                    st.metric("Recent Losses", recent_form['losses'])
                    st.metric("Win %", f"{recent_form['win_percentage']:.1%}")
                else:
                    st.info("No recent form data available")

def show_schedule_analysis():
    """Show schedule analysis"""
    st.subheader("📅 Schedule Analysis")
    
    # Get upcoming games
    games = get_upcoming_games(50)
    
    if not games:
        st.warning("No upcoming games found.")
        return
    
    # Games by date
    st.write("**Upcoming Games by Date**")
    for game in games[:10]:  # Show first 10
        st.write(f"{str(game['Date'])} - {game['AwayTeam']} @ {game['HomeTeam']}")

def show_prediction_history():
    """Show prediction history"""
    st.subheader("📋 Prediction History")
    
    try:
        from database_prediction import load_model_performance
        performance = load_model_performance()
        
        if not performance['predictions']:
            st.info("No predictions made yet.")
            return
        
        # Show recent predictions
        recent_predictions = performance['predictions'][-20:]  # Last 20
        
        for pred in reversed(recent_predictions):
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{pred['away_team']} @ {pred['home_team']}**")
                    st.write(f"Predicted: {pred['predicted_winner']} ({pred['confidence']:.1%})")
                
                with col2:
                    if pred.get('actual_winner'):
                        if pred['is_correct']:
                            st.success("✅ Correct")
                        else:
                            st.error("❌ Incorrect")
                    else:
                        st.info("⏳ Pending")
                
                with col3:
                    st.write(f"Date: {pred['timestamp'][:10]}")
                
                st.divider()
    
    except Exception as e:
        st.error(f"Could not load prediction history: {e}")

def import_schedule():
    """Import NBA schedule for 2025-2026"""
    with st.spinner("Importing NBA schedule for 2025-2026 season..."):
        try:
            # Import the schedule importer
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from nba_schedule_importer import main as import_schedule_main
            
            # Run the import
            import_schedule_main()
            st.success("✅ Schedule imported successfully!")
            
        except Exception as e:
            st.error(f"❌ Failed to import schedule: {e}")

def create_embeddings():
    """Create vector embeddings for teams, players, and matches"""
    with st.spinner("Creating vector embeddings for teams, players, and matches..."):
        try:
            # Import the embedding system
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from vector_embedding_system import NBAVectorEmbeddingSystem
            
            # Create embeddings
            embedding_system = NBAVectorEmbeddingSystem()
            
            if embedding_system.connect_to_database():
                success = embedding_system.create_all_embeddings()
                if success:
                    st.success("✅ Vector embeddings created successfully!")
                    st.info("Teams, players, and matches have been embedded and are ready for enhanced predictions.")
                else:
                    st.error("❌ Some embeddings failed to create. Check the logs for details.")
            else:
                st.error("❌ Failed to connect to database")
                
        except Exception as e:
            st.error(f"❌ Failed to create embeddings: {e}")

def create_chat_interface():
    """Create the chat interface for natural language queries"""
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about NBA matchups..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the query
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your query and extracting entities..."):
                result = process_natural_language_query(prompt)
                
                # Check if result is a tuple (text + chart data) or just text
                if isinstance(result, tuple):
                    response_text, chart_data = result
                    st.markdown(response_text)
                    
                    # Display charts
                    display_prediction_charts(chart_data)
                else:
                    st.markdown(result)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": result if isinstance(result, str) else result[0]})

def process_natural_language_query(query: str) -> str:
    """Process a natural language query and return a response"""
    try:
        # Process the query
        query_data = st.session_state.query_processor.process_query(query)
        
        # Check if it's a valid matchup query
        if query_data['is_valid_matchup']:
            team1 = query_data['team1']
            team2 = query_data['team2']
            
            # Generate prediction
            prediction_result = generate_prediction_response(team1, team2, query_data)
            return prediction_result
        else:
            # Handle non-matchup queries
            return handle_general_query(query_data)
    
    except Exception as e:
        return f"Sorry, I encountered an error processing your query: {str(e)}"

def generate_prediction_response(team1: str, team2: str, query_data: dict) -> str:
    """Generate a comprehensive prediction response for a team matchup"""
    
    # Get team context data
    home_context = get_team_context_data(team1)
    away_context = get_team_context_data(team2)
    
    # Ensure contexts are not None
    if home_context is None:
        home_context = {}
    if away_context is None:
        away_context = {}
    
    # Generate prediction - try vector enhanced first, fallback to traditional
    try:
        # Try to use vector enhanced prediction
        vector_system = load_vector_enhanced_system()
        
        if vector_system and vector_system.team_embeddings:
            # Use vector enhanced prediction
            db_prediction = vector_system.predict_with_vector_enhancement(team1, team2)
            is_vector_enhanced = True
        else:
            # Fallback to traditional prediction
            db_prediction = predict_game_outcome(team1, team2)
            is_vector_enhanced = False
        
        # Create comprehensive response
        response = f"## 🏀 {team1} vs {team2} Prediction\n\n"
        
        # Main prediction with enhanced analysis
        winner = db_prediction['predicted_winner']
        confidence = db_prediction.get('enhanced_confidence', db_prediction.get('confidence', 0))
        
        if winner == team1:
            response += f"**🏠 {winner}** is predicted to win at home\n\n"
        else:
            response += f"**✈️ {winner}** is predicted to win away\n\n"
        
        # Show if vector enhanced
        if is_vector_enhanced:
            vector_boost = db_prediction.get('vector_confidence_boost', 0)
            response += f"🧠 **Vector Enhanced Prediction** (Confidence Boost: +{vector_boost:.1%})\n\n"
        
        # Enhanced confidence display with quality indicators
        confidence_interval = db_prediction.get('confidence_interval', {})
        data_quality = db_prediction.get('data_quality_factors', {})
        
        response += f"**Confidence: {confidence:.1%}**\n"
        if confidence_interval:
            response += f"**Confidence Range: {confidence_interval.get('lower', 0):.1%} - {confidence_interval.get('upper', 0):.1%}**\n"
        
        # Score predictions
        score_predictions = db_prediction.get('score_predictions', {})
        if score_predictions:
            home_score = score_predictions.get('home_score', 0)
            away_score = score_predictions.get('away_score', 0)
            total_points = score_predictions.get('total_points', 0)
            point_spread = score_predictions.get('point_spread', 0)
            
            response += f"\n### 🏀 Predicted Final Score\n\n"
            response += f"**{team1}: {home_score}**\n"
            response += f"**{team2}: {away_score}**\n"
            response += f"**Total Points: {total_points}**\n"
            response += f"**Point Spread: {team1} {point_spread:+d}**\n\n"
        
        # Gambling statistics
        gambling_stats = db_prediction.get('gambling_stats', {})
        if gambling_stats:
            response += f"### 🎰 Gambling Statistics\n\n"
            
            # First half predictions
            first_half_total = gambling_stats.get('first_half_total', 0)
            home_first_half = gambling_stats.get('home_first_half', 0)
            away_first_half = gambling_stats.get('away_first_half', 0)
            
            response += f"**First Half:**\n"
            response += f"- {team1}: {home_first_half}\n"
            response += f"- {team2}: {away_first_half}\n"
            response += f"- **First Half Total: {first_half_total}**\n\n"
            
            # Quarter breakdown
            q1_total = gambling_stats.get('q1_total', 0)
            q2_total = gambling_stats.get('q2_total', 0)
            q3_total = gambling_stats.get('q3_total', 0)
            q4_total = gambling_stats.get('q4_total', 0)
            
            response += f"**Quarter Breakdown:**\n"
            response += f"- Q1 Total: {q1_total}\n"
            response += f"- Q2 Total: {q2_total}\n"
            response += f"- Q3 Total: {q3_total}\n"
            response += f"- Q4 Total: {q4_total}\n\n"
            
            # Team totals
            home_team_total = gambling_stats.get('home_team_total', 0)
            away_team_total = gambling_stats.get('away_team_total', 0)
            
            response += f"**Team Totals:**\n"
            response += f"- {team1} Total: {home_team_total}\n"
            response += f"- {team2} Total: {away_team_total}\n\n"
            
            # Confidence levels for different bets
            bet_confidence = gambling_stats.get('confidence', {})
            if bet_confidence:
                response += f"**Betting Confidence:**\n"
                response += f"- Moneyline: {bet_confidence.get('moneyline', 0):.1%}\n"
                response += f"- Point Spread: {bet_confidence.get('spread', 0):.1%}\n"
                response += f"- Total Points: {bet_confidence.get('total', 0):.1%}\n"
                response += f"- First Half Total: {bet_confidence.get('first_half', 0):.1%}\n\n"
        
        # Data quality indicators
        if data_quality:
            home_quality = data_quality.get('home_data_quality', 0)
            away_quality = data_quality.get('away_data_quality', 0)
            h2h_games = data_quality.get('h2h_games', 0)
            
            response += f"**Data Quality:**\n"
            response += f"- {team1} data quality: {home_quality:.1%}\n"
            response += f"- {team2} data quality: {away_quality:.1%}\n"
            response += f"- Head-to-head games: {h2h_games}\n\n"
        
        # Vector insights (if available)
        if is_vector_enhanced and 'vector_insights' in db_prediction:
            vector_insights = db_prediction['vector_insights']
            response += "### 🧠 Vector Analysis\n\n"
            
            # Team similarity
            team_similarity = vector_insights.get('team_similarity', 0)
            response += f"**Team Similarity:** {team_similarity:.3f}\n"
            
            # Style analysis
            home_style = vector_insights.get('home_team_style', {})
            away_style = vector_insights.get('away_team_style', {})
            
            if home_style.get('similar_teams'):
                response += f"**{team1} Similar Teams:** "
                similar_teams = [f"{team} ({sim:.2f})" for team, sim in home_style['similar_teams'][:3]]
                response += ", ".join(similar_teams) + "\n"
            
            if away_style.get('similar_teams'):
                response += f"**{team2} Similar Teams:** "
                similar_teams = [f"{team} ({sim:.2f})" for team, sim in away_style['similar_teams'][:3]]
                response += ", ".join(similar_teams) + "\n"
            
            # Historical match similarity
            hist_similarity = vector_insights.get('historical_match_similarity', {})
            if hist_similarity.get('avg_similarity', 0) > 0:
                response += f"**Historical Match Similarity:** {hist_similarity['avg_similarity']:.3f}\n"
                similar_matches = hist_similarity.get('similar_matches', [])
                if similar_matches:
                    response += f"**Similar Past Games:** {len(similar_matches)} found\n"
            
            response += "\n"
        
        # Enhanced team analysis with news sentiment
        response += "### 📊 Comprehensive Team Analysis\n\n"
        
        # Home team detailed analysis
        response += f"#### 🏠 {team1} Analysis\n"
        if home_context and home_context.get('team_stats'):
            stats = home_context['team_stats']
            response += f"- **Season Record:** {stats.get('Wins', 0)}-{stats.get('Losses', 0)}\n"
            response += f"- **Team Strength:** {db_prediction['home_strength']:.3f}\n"
            if stats.get('PointsFor', 0) > 0:
                response += f"- **Points Per Game:** {stats.get('PointsFor', 0) / 82:.1f}\n"
                response += f"- **Points Allowed:** {stats.get('PointsAgainst', 0) / 82:.1f}\n"
        else:
            response += "- Limited statistical data available\n"
        
        # Home team news analysis
        home_news = home_context.get('news', []) if home_context else []
        if home_news:
            response += f"- **Recent News:** {len(home_news)} articles analyzed\n"
            response += f"- **Latest Headlines:**\n"
            for i, article in enumerate(home_news[:3]):
                news_id = article.get('NewsID')
                title_text = article.get('Title', 'No title')
                display_url = f"/?news_id={news_id}"
                
                response += f"  • [{title_text[:60]}...]({display_url})\n"
        else:
            response += "- No recent news articles found\n"
        
        # Away team detailed analysis
        response += f"\n#### ✈️ {team2} Analysis\n"
        if away_context and away_context.get('team_stats'):
            stats = away_context['team_stats']
            response += f"- **Season Record:** {stats.get('Wins', 0)}-{stats.get('Losses', 0)}\n"
            response += f"- **Team Strength:** {db_prediction['away_strength']:.3f}\n"
            if stats.get('PointsFor', 0) > 0:
                response += f"- **Points Per Game:** {stats.get('PointsFor', 0) / 82:.1f}\n"
                response += f"- **Points Allowed:** {stats.get('PointsAgainst', 0) / 82:.1f}\n"
        else:
            response += "- Limited statistical data available\n"
        
        # Away team news analysis
        away_news = away_context.get('news', []) if away_context else []
        if away_news:
            response += f"- **Recent News:** {len(away_news)} articles analyzed\n"
            response += f"- **Latest Headlines:**\n"
            for i, article in enumerate(away_news[:3]):
                news_id = article.get('NewsID')
                title_text = article.get('Title', 'No title')
                display_url = f"/?news_id={news_id}"
                
                response += f"  • [{title_text[:60]}...]({display_url})\n"
        else:
            response += "- No recent news articles found\n"
        
        # Recent form analysis
        response += "\n### 📈 Recent Performance Analysis\n\n"
        home_form = db_prediction.get('home_form', {})
        away_form = db_prediction.get('away_form', {})
        
        if home_form.get('total_games', 0) > 0:
            response += f"**{team1} Last 10 Games:** {home_form['wins']}-{home_form['losses']} ({home_form['win_percentage']:.1%})\n"
            if home_form.get('win_percentage', 0) > 0.6:
                response += f"  🔥 {team1} is on a hot streak!\n"
            elif home_form.get('win_percentage', 0) < 0.4:
                response += f"  ❄️ {team1} has been struggling recently\n"
        else:
            response += f"**{team1}:** No recent game data available\n"
        
        if away_form.get('total_games', 0) > 0:
            response += f"**{team2} Last 10 Games:** {away_form['wins']}-{away_form['losses']} ({away_form['win_percentage']:.1%})\n"
            if away_form.get('win_percentage', 0) > 0.6:
                response += f"  🔥 {team2} is on a hot streak!\n"
            elif away_form.get('win_percentage', 0) < 0.4:
                response += f"  ❄️ {team2} has been struggling recently\n"
        else:
            response += f"**{team2}:** No recent game data available\n"
        
        # Head-to-head analysis
        h2h = db_prediction.get('head_to_head', {})
        if h2h.get('total_games', 0) > 0:
            response += f"\n### ⚔️ Head-to-Head Analysis\n"
            response += f"**Last {h2h['total_games']} meetings:** {team1} {h2h['team1_wins']}-{h2h['team2_wins']} {team2}\n"
            
            if h2h['team1_wins'] > h2h['team2_wins']:
                response += f"  📊 {team1} has the historical advantage\n"
            elif h2h['team2_wins'] > h2h['team1_wins']:
                response += f"  📊 {team2} has the historical advantage\n"
            else:
                response += f"  ⚖️ Teams are evenly matched historically\n"
        
        # Key factors analysis
        response += "\n### 🎯 Key Factors Analysis\n\n"
        
        # Strength comparison
        home_strength = db_prediction.get('home_strength', 0)
        away_strength = db_prediction.get('away_strength', 0)
        
        if home_strength > away_strength:
            strength_diff = home_strength - away_strength
            response += f"**Team Strength Advantage:** {team1} (+{strength_diff:.3f})\n"
        else:
            strength_diff = away_strength - home_strength
            response += f"**Team Strength Advantage:** {team2} (+{strength_diff:.3f})\n"
        
        # Home court advantage
        response += f"**Home Court Advantage:** {team1} playing at home\n"
        
        # Confidence analysis
        if confidence > 0.7:
            response += f"**Prediction Confidence:** High ({confidence:.1%}) - Strong data support\n"
        elif confidence > 0.5:
            response += f"**Prediction Confidence:** Medium ({confidence:.1%}) - Moderate data support\n"
        else:
            response += f"**Prediction Confidence:** Low ({confidence:.1%}) - Limited data available\n"
        
        # Entity extraction insights
        if query_data['entities']:
            response += "\n### 🔍 Extracted Context Information\n\n"
            
            # Categorize entities
            teams = [e for e in query_data['entities'] if e.get('type') == 'team']
            players = [e for e in query_data['entities'] if e.get('type') == 'player']
            stats = [e for e in query_data['entities'] if e.get('type') == 'stat']
            injuries = [e for e in query_data['entities'] if e.get('type') == 'injury']
            penalties = [e for e in query_data['entities'] if e.get('type') == 'penalty']
            
            if teams:
                response += f"**Teams Mentioned:** {', '.join([e.get('name', '') for e in teams])}\n"
            if players:
                response += f"**Players Mentioned:** {', '.join([e.get('name', '') for e in players])}\n"
            if stats:
                response += f"**Statistics:** {', '.join([e.get('name', '') for e in stats])}\n"
            if injuries:
                response += f"**Injury Concerns:** {', '.join([e.get('name', '') for e in injuries])}\n"
            if penalties:
                response += f"**Disciplinary Issues:** {', '.join([e.get('name', '') for e in penalties])}\n"
        
        # Final recommendation
        response += "\n### 💡 Final Recommendation\n\n"
        if confidence > 0.6:
            response += f"Based on comprehensive analysis of team statistics, recent form, head-to-head records, and news sentiment, **{winner}** is the clear favorite to win this matchup.\n\n"
        else:
            response += f"Based on available data, **{winner}** has a slight edge, but this could be a close game. Consider recent form and any injury updates before making final decisions.\n\n"
        
        response += "**Note:** This prediction is based on historical data and current team statistics. Actual game outcomes may vary due to factors like injuries, lineup changes, and game-day performance."
        
        return response, {
            'team1': team1,
            'team2': team2,
            'winner': winner,
            'confidence': confidence,
            'home_strength': db_prediction.get('home_strength', 0),
            'away_strength': db_prediction.get('away_strength', 0),
            'home_form': home_form,
            'away_form': away_form,
            'h2h': h2h,
            'home_news_count': len(home_news),
            'away_news_count': len(away_news),
            'entities': query_data['entities'],
            'score_predictions': db_prediction.get('score_predictions', {}),
            'gambling_stats': db_prediction.get('gambling_stats', {})
        }
    
    except Exception as e:
        return f"Sorry, I couldn't generate a comprehensive prediction for {team1} vs {team2}. Error: {str(e)}"

def display_prediction_charts(chart_data: dict):
    """Display interactive charts for the prediction analysis"""
    
    st.markdown("### 📊 Visual Analysis")
    
    # Create tabs for different chart types
    chart_tab1, chart_tab2, chart_tab3, chart_tab4, chart_tab5 = st.tabs([
        "Team Comparison", "Performance Trends", "Entity Analysis", "Confidence Breakdown", "Gambling Stats"
    ])
    
    with chart_tab1:
        # Team strength comparison chart
        st.subheader("Team Strength Comparison")
        
        teams = [chart_data['team1'], chart_data['team2']]
        strengths = [chart_data['home_strength'], chart_data['away_strength']]
        colors = ['#1f77b4', '#ff7f0e']
        
        fig = px.bar(
            x=teams,
            y=strengths,
            title="Team Strength Comparison",
            color=teams,
            color_discrete_sequence=colors
        )
        fig.update_layout(
            xaxis_title="Teams",
            yaxis_title="Strength Score",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Win probability pie chart
        st.subheader("Win Probability")
        winner = chart_data['winner']
        confidence = chart_data['confidence']
        
        if winner == chart_data['team1']:
            home_prob = confidence
            away_prob = 1 - confidence
        else:
            home_prob = 1 - confidence
            away_prob = confidence
        
        fig_pie = px.pie(
            values=[home_prob, away_prob],
            names=[chart_data['team1'], chart_data['team2']],
            title="Predicted Win Probability",
            color_discrete_sequence=colors
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with chart_tab2:
        # Recent form comparison
        st.subheader("Recent Performance (Last 10 Games)")
        
        home_form = chart_data['home_form']
        away_form = chart_data['away_form']
        
        if home_form.get('total_games', 0) > 0 and away_form.get('total_games', 0) > 0:
            form_data = {
                'Team': [chart_data['team1'], chart_data['team2']],
                'Wins': [home_form.get('wins', 0), away_form.get('wins', 0)],
                'Losses': [home_form.get('losses', 0), away_form.get('losses', 0)],
                'Win %': [home_form.get('win_percentage', 0), away_form.get('win_percentage', 0)]
            }
            
            # Win percentage comparison
            fig_win_pct = px.bar(
                x=form_data['Team'],
                y=form_data['Win %'],
                title="Recent Win Percentage",
                color=form_data['Team'],
                color_discrete_sequence=colors
            )
            fig_win_pct.update_layout(
                xaxis_title="Teams",
                yaxis_title="Win Percentage",
                showlegend=False
            )
            st.plotly_chart(fig_win_pct, use_container_width=True)
            
            # Wins vs Losses stacked bar
            fig_wins_losses = go.Figure(data=[
                go.Bar(name='Wins', x=form_data['Team'], y=form_data['Wins'], marker_color='green'),
                go.Bar(name='Losses', x=form_data['Team'], y=form_data['Losses'], marker_color='red')
            ])
            fig_wins_losses.update_layout(
                title="Recent Games: Wins vs Losses",
                xaxis_title="Teams",
                yaxis_title="Number of Games",
                barmode='stack'
            )
            st.plotly_chart(fig_wins_losses, use_container_width=True)
        else:
            st.info("No recent performance data available for chart display.")
    
    with chart_tab3:
        # Entity analysis charts
        st.subheader("Extracted Entity Analysis")
        
        entities = chart_data['entities']
        if entities:
            # Entity type distribution
            entity_types = {}
            for entity in entities:
                entity_type = entity.get('type', 'Unknown')
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
            
            if entity_types:
                fig_entities = px.pie(
                    values=list(entity_types.values()),
                    names=list(entity_types.keys()),
                    title="Entity Types Distribution"
                )
                st.plotly_chart(fig_entities, use_container_width=True)
                
                # Entity count bar chart
                fig_entity_count = px.bar(
                    x=list(entity_types.keys()),
                    y=list(entity_types.values()),
                    title="Entity Count by Type",
                    color=list(entity_types.keys())
                )
                fig_entity_count.update_layout(
                    xaxis_title="Entity Type",
                    yaxis_title="Count",
                    showlegend=False
                )
                st.plotly_chart(fig_entity_count, use_container_width=True)
        else:
            st.info("No entities extracted for chart display.")
    
    with chart_tab4:
        # Confidence and data quality analysis
        st.subheader("Prediction Confidence & Data Quality")
        
        # Confidence level indicator
        confidence = chart_data['confidence']
        confidence_level = "High" if confidence > 0.7 else "Medium" if confidence > 0.5 else "Low"
        
        fig_confidence = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = confidence * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Prediction Confidence ({confidence_level})"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_confidence.update_layout(height=400)
        st.plotly_chart(fig_confidence, use_container_width=True)
        
        # Data availability chart
        data_availability = {
            'Team Stats': 1 if chart_data['home_strength'] > 0 or chart_data['away_strength'] > 0 else 0,
            'Recent Form': 1 if (chart_data['home_form'].get('total_games', 0) > 0 or 
                               chart_data['away_form'].get('total_games', 0) > 0) else 0,
            'Head-to-Head': 1 if chart_data['h2h'].get('total_games', 0) > 0 else 0,
            'News Analysis': 1 if (chart_data['home_news_count'] > 0 or 
                                 chart_data['away_news_count'] > 0) else 0,
            'Entity Extraction': 1 if len(chart_data['entities']) > 0 else 0
        }
        
        fig_data = px.bar(
            x=list(data_availability.keys()),
            y=list(data_availability.values()),
            title="Data Availability by Source",
            color=list(data_availability.values()),
            color_discrete_map={0: 'red', 1: 'green'}
        )
        fig_data.update_layout(
            xaxis_title="Data Source",
            yaxis_title="Available (1) / Not Available (0)",
            showlegend=False
        )
        st.plotly_chart(fig_data, use_container_width=True)
    
    with chart_tab5:
        # Gambling statistics charts
        st.subheader("Gambling Statistics Analysis")
        
        # Get gambling stats from chart data
        gambling_stats = chart_data.get('gambling_stats', {})
        
        if gambling_stats:
            # Score prediction chart
            st.subheader("Predicted Scores")
            
            teams = [chart_data['team1'], chart_data['team2']]
            home_score = gambling_stats.get('home_score', 0)
            away_score = gambling_stats.get('away_score', 0)
            
            fig_scores = px.bar(
                x=teams,
                y=[home_score, away_score],
                title="Predicted Final Scores",
                color=teams,
                color_discrete_sequence=['#1f77b4', '#ff7f0e']
            )
            fig_scores.update_layout(
                xaxis_title="Teams",
                yaxis_title="Points",
                showlegend=False
            )
            st.plotly_chart(fig_scores, use_container_width=True)
            
            # First half vs second half
            st.subheader("First Half vs Second Half")
            
            first_half_total = gambling_stats.get('first_half_total', 0)
            second_half_total = gambling_stats.get('second_half_total', 0)
            
            fig_halves = px.bar(
                x=['First Half', 'Second Half'],
                y=[first_half_total, second_half_total],
                title="Predicted Points by Half",
                color=['First Half', 'Second Half'],
                color_discrete_sequence=['#2ca02c', '#d62728']
            )
            fig_halves.update_layout(
                xaxis_title="Half",
                yaxis_title="Total Points",
                showlegend=False
            )
            st.plotly_chart(fig_halves, use_container_width=True)
            
            # Quarter breakdown
            st.subheader("Quarter Breakdown")
            
            quarters = ['Q1', 'Q2', 'Q3', 'Q4']
            quarter_totals = [
                gambling_stats.get('q1_total', 0),
                gambling_stats.get('q2_total', 0),
                gambling_stats.get('q3_total', 0),
                gambling_stats.get('q4_total', 0)
            ]
            
            fig_quarters = px.bar(
                x=quarters,
                y=quarter_totals,
                title="Predicted Points by Quarter",
                color=quarters,
                color_discrete_sequence=['#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            )
            fig_quarters.update_layout(
                xaxis_title="Quarter",
                yaxis_title="Total Points",
                showlegend=False
            )
            st.plotly_chart(fig_quarters, use_container_width=True)
            
            # Betting confidence levels
            st.subheader("Betting Confidence Levels")
            
            bet_confidence = gambling_stats.get('confidence', {})
            if bet_confidence:
                bet_types = list(bet_confidence.keys())
                confidence_values = [bet_confidence[bet] * 100 for bet in bet_types]
                
                fig_bets = px.bar(
                    x=bet_types,
                    y=confidence_values,
                    title="Confidence Levels for Different Bet Types",
                    color=confidence_values,
                    color_continuous_scale='RdYlGn'
                )
                fig_bets.update_layout(
                    xaxis_title="Bet Type",
                    yaxis_title="Confidence (%)",
                    showlegend=False
                )
                st.plotly_chart(fig_bets, use_container_width=True)
            
            # Team totals comparison
            st.subheader("Team Totals")
            
            home_team_total = gambling_stats.get('home_team_total', 0)
            away_team_total = gambling_stats.get('away_team_total', 0)
            
            fig_totals = px.bar(
                x=teams,
                y=[home_team_total, away_team_total],
                title="Predicted Team Totals",
                color=teams,
                color_discrete_sequence=['#1f77b4', '#ff7f0e']
            )
            fig_totals.update_layout(
                xaxis_title="Teams",
                yaxis_title="Total Points",
                showlegend=False
            )
            st.plotly_chart(fig_totals, use_container_width=True)
            
            # Summary statistics table
            st.subheader("Summary Statistics")
            
            summary_data = {
                'Metric': [
                    'Final Score (Home)',
                    'Final Score (Away)',
                    'Total Points',
                    'Point Spread',
                    'First Half Total',
                    'Second Half Total',
                    'Q1 Total',
                    'Q2 Total',
                    'Q3 Total',
                    'Q4 Total',
                    'Margin of Victory',
                    'Overtime Probability'
                ],
                'Value': [
                    home_score,
                    away_score,
                    gambling_stats.get('total_points', 0),
                    gambling_stats.get('point_spread', 0),
                    first_half_total,
                    second_half_total,
                    gambling_stats.get('q1_total', 0),
                    gambling_stats.get('q2_total', 0),
                    gambling_stats.get('q3_total', 0),
                    gambling_stats.get('q4_total', 0),
                    gambling_stats.get('margin_of_victory', 0),
                    f"{gambling_stats.get('overtime_probability', 0):.1%}"
                ]
            }
            
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True)
        
        else:
            st.info("No gambling statistics available for this prediction.")

def handle_general_query(query_data: dict) -> str:
    """Handle general queries that aren't specific matchups"""
    query_type = query_data['query_type']
    
    if query_type == 'stats':
        return "I can help you with team statistics! Try asking about a specific matchup like 'Boston Celtics vs Atlanta Hawks stats'."
    elif query_type == 'injury':
        return "I can analyze injury information! Try asking about a specific team or matchup."
    elif query_type == 'news':
        return "I can analyze recent news and sentiment! Try asking about a specific team or matchup."
    else:
        return "I'm here to help with NBA predictions! Try asking about a specific matchup like 'Who will win, Boston Celtics or Atlanta Hawks?'"

def create_prediction_interface():
    """Create the main prediction interface"""
    st.header("🏀 NBA Game Predictions - Hybrid Model")
    st.markdown("""
    This hybrid model combines multiple approaches for accurate predictions:
    - **Time Series Analysis**: Historical match trends and patterns
    - **Statistical Modeling**: Player and team performance metrics
    - **Sentiment Analysis**: News sentiment and contextual factors
    - **LLM Enhancement**: AI-powered reasoning and narratives
    """)
    
    # Model status and training controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        model = load_hybrid_model()
        if not model:
            st.error("Model not available. Please check the configuration.")
            return
    
    with col2:
        if st.button("🔄 Retrain Model", help="Retrain the model with fresh data"):
            if 'hybrid_model' in st.session_state:
                del st.session_state.hybrid_model
            st.rerun()
    
    # Sidebar controls
    st.sidebar.header("Model Configuration")
    
    # Weight adjustments
    st.sidebar.subheader("Model Weights")
    time_weight = st.sidebar.slider("Time Series Weight", 0.0, 1.0, 0.3, 0.05)
    stat_weight = st.sidebar.slider("Statistical Weight", 0.0, 1.0, 0.4, 0.05)
    sent_weight = st.sidebar.slider("Sentiment Weight", 0.0, 1.0, 0.2, 0.05)
    llm_weight = st.sidebar.slider("LLM Weight", 0.0, 1.0, 0.1, 0.05)
    
    # Normalize weights
    total_weight = time_weight + stat_weight + sent_weight + llm_weight
    if total_weight > 0:
        time_weight /= total_weight
        stat_weight /= total_weight
        sent_weight /= total_weight
        llm_weight /= total_weight
    
    # Update model weights
    model.update_weights({
        'time_series': time_weight,
        'statistical': stat_weight,
        'sentiment': sent_weight,
        'llm': llm_weight
    })
    
    st.sidebar.write(f"**Normalized Weights:**")
    st.sidebar.write(f"Time Series: {time_weight:.3f}")
    st.sidebar.write(f"Statistical: {stat_weight:.3f}")
    st.sidebar.write(f"Sentiment: {sent_weight:.3f}")
    st.sidebar.write(f"LLM: {llm_weight:.3f}")
    
    # Main prediction interface
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Select Teams")
        
        # Get teams from database
        with st.spinner("Loading teams..."):
            teams = get_team_list()
        
        if not teams:
            st.error("No teams found in database. Using default teams.")
            teams = ['Lakers', 'Warriors', 'Celtics', 'Heat', 'Bulls', 'Knicks', 'Nets', 'Suns', 
                    'Bucks', '76ers', 'Raptors', 'Pacers', 'Hawks', 'Hornets', 'Wizards', 'Magic']
        
        home_team = st.selectbox("Home Team", teams, index=0)
        away_team = st.selectbox("Away Team", [t for t in teams if t != home_team], index=1)
        
    with col2:
        # Get team context data for prediction
        home_context = get_team_context_data(home_team)
        away_context = get_team_context_data(away_team)
        
        # Ensure contexts are not None
        if home_context is None:
            home_context = {}
        if away_context is None:
            away_context = {}
    
    # Prediction button
    if st.button("🎯 Generate Prediction", type="primary"):
        with st.spinner("Analyzing data and generating prediction..."):
            try:
                # Use database-driven prediction
                db_prediction = predict_game_outcome(home_team, away_team)
                
                # Also try hybrid model prediction for comparison
                try:
                    context_data = {
                        'player_stats': create_sample_player_stats(home_team, away_team),
                        'recent_form': {
                            home_team: f"W-L: {home_context.get('recent_form', {}).get('wins', 0)}-{home_context.get('recent_form', {}).get('losses', 0)}",
                            away_team: f"W-L: {away_context.get('recent_form', {}).get('wins', 0)}-{away_context.get('recent_form', {}).get('losses', 0)}"
                        },
                        'head_to_head': f"Recent meetings: {home_team} vs {away_team}",
                        'home_advantage': 0.1,  # Default home advantage
                        'rest_days': {
                            'home': 1,  # Default rest days
                            'away': 1
                        }
                    }
                    
                    hybrid_prediction = model.predict_game(home_team, away_team, context_data)
                    
                    # Combine predictions
                    combined_prediction = {
                        'predicted_winner': db_prediction['predicted_winner'],
                        'confidence': (db_prediction['confidence'] + abs(hybrid_prediction['ensemble_score'])) / 2,
                        'ensemble_score': db_prediction['prediction_score'],
                        'time_series': hybrid_prediction.get('time_series', 0),
                        'statistical': hybrid_prediction.get('statistical', 0),
                        'sentiment': hybrid_prediction.get('sentiment', 0),
                        'llm_analysis': hybrid_prediction.get('llm_analysis', 'LLM analysis unavailable'),
                        'home_team': home_team,
                        'away_team': away_team,
                        'db_prediction': db_prediction,
                        'hybrid_prediction': hybrid_prediction
                    }
                    
                except Exception as hybrid_error:
                    st.warning(f"Hybrid model prediction failed: {hybrid_error}")
                    # Use only database prediction
                    combined_prediction = {
                        'predicted_winner': db_prediction['predicted_winner'],
                        'confidence': db_prediction['confidence'],
                        'ensemble_score': db_prediction['prediction_score'],
                        'time_series': 0,
                        'statistical': 0,
                        'sentiment': 0,
                        'llm_analysis': 'LLM analysis unavailable',
                        'home_team': home_team,
                        'away_team': away_team,
                        'db_prediction': db_prediction,
                        'hybrid_prediction': None
                    }
                
                # Display results
                display_prediction_results(combined_prediction, home_team, away_team)
                
            except Exception as e:
                st.error(f"Prediction failed: {e}")
                st.exception(e)

def display_prediction_results(prediction, home_team, away_team):
    """Display the prediction results in an attractive format"""
    st.header("📊 Prediction Results")
    
    # Main prediction result
    winner = prediction['predicted_winner']
    confidence = prediction['confidence']
    
    # Get win probabilities if available
    home_win_prob = prediction.get('home_win_probability', 0.5)
    away_win_prob = prediction.get('away_win_probability', 0.5)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if winner == home_team:
            st.success(f"🏠 **{winner}** wins at home")
        else:
            st.info(f"✈️ **{winner}** wins away")
        
        st.progress(confidence)
        st.write(f"**Confidence: {confidence:.1%}**")
        
        # Display win probabilities
        st.write(f"**Win Probabilities:**")
        st.write(f"🏠 {home_team}: {home_win_prob:.1%}")
        st.write(f"✈️ {away_team}: {away_win_prob:.1%}")
    
    # Database prediction details
    if 'db_prediction' in prediction:
        db_pred = prediction['db_prediction']
        st.subheader("Database Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(f"{home_team} Strength", f"{db_pred['home_strength']:.3f}")
            home_form = db_pred['home_form']
            if home_form.get('total_games', 0) > 0:
                st.metric("Recent Form", f"{home_form['wins']}-{home_form['losses']}")
                st.metric("Recent Win %", f"{home_form['win_percentage']:.1%}")
            else:
                st.info("No recent games in database")
        
        with col2:
            st.metric(f"{away_team} Strength", f"{db_pred['away_strength']:.3f}")
            away_form = db_pred['away_form']
            if away_form.get('total_games', 0) > 0:
                st.metric("Recent Form", f"{away_form['wins']}-{away_form['losses']}")
                st.metric("Recent Win %", f"{away_form['win_percentage']:.1%}")
            else:
                st.info("No recent games in database")
        
        # Show head-to-head if available
        h2h = db_pred.get('head_to_head', {})
        if h2h.get('total_games', 0) > 0:
            st.subheader("Head-to-Head Record (From Database)")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"{home_team} Wins", h2h['team1_wins'])
            with col2:
                st.metric("Total Games", h2h['total_games'])
            with col3:
                st.metric(f"{away_team} Wins", h2h['team2_wins'])
    
    # Hybrid model scores (if available)
    if prediction.get('hybrid_prediction'):
        st.subheader("Hybrid Model Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Time Series Score", f"{prediction['time_series']:.2f}")
        
        with col2:
            st.metric("Statistical Score", f"{prediction['statistical']:.2f}")
        
        with col3:
            st.metric("Sentiment Score", f"{prediction['sentiment']:.2f}")
    
    # Create visualization
    st.subheader("Model Contribution Analysis")
    
    # Prepare data for plotting
    model_scores = {
        'Time Series': prediction['time_series'],
        'Statistical': prediction['statistical'],
        'Sentiment': prediction['sentiment']
    }
    
    # Create bar chart
    fig = px.bar(
        x=list(model_scores.keys()),
        y=list(model_scores.values()),
        title="Individual Model Scores",
        color=list(model_scores.values()),
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(
        xaxis_title="Model Type",
        yaxis_title="Score",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Weighted contribution chart
    st.subheader("Weighted Model Contributions")
    
    weights = st.session_state.hybrid_model.weights
    weighted_contributions = {
        'Time Series': weights['time_series'] * prediction['time_series'],
        'Statistical': weights['statistical'] * prediction['statistical'],
        'Sentiment': weights['sentiment'] * prediction['sentiment']
    }
    
    fig2 = px.pie(
        values=list(weighted_contributions.values()),
        names=list(weighted_contributions.keys()),
        title="Weighted Contributions to Final Prediction"
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Database Information Used
    if 'db_prediction' in prediction:
        st.subheader("📊 Database Information Used")
        
        try:
            # Get fresh team data to show what was actually used
            home_context = get_team_context_data(home_team)
            away_context = get_team_context_data(away_team)
            
            # Ensure contexts are not None
            if home_context is None:
                home_context = {}
            if away_context is None:
                away_context = {}
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{home_team} Data Sources:**")
                if home_context and home_context.get('team_stats'):
                    stats = home_context['team_stats']
                    st.write(f"• Season Record: {stats.get('Wins', 0)}-{stats.get('Losses', 0)}")
                    st.write(f"• Points For: {stats.get('PointsFor', 0)}")
                    st.write(f"• Points Against: {stats.get('PointsAgainst', 0)}")
                
                recent_form = home_context.get('recent_form', {}) if home_context else {}
                if recent_form.get('total_games', 0) > 0:
                    st.write(f"• Recent Games: {recent_form['wins']}-{recent_form['losses']}")
                
                news = home_context.get('news', []) if home_context else []
                if news:
                    st.write(f"• News Articles: {len(news)} analyzed")
                    for i, article in enumerate(news[:2]):
                        st.write(f"  - {article.get('Title', 'No title')[:40]}...")
                else:
                    st.write("• No news articles found")
            
            with col2:
                st.write(f"**{away_team} Data Sources:**")
                if away_context and away_context.get('team_stats'):
                    stats = away_context['team_stats']
                    st.write(f"• Season Record: {stats.get('Wins', 0)}-{stats.get('Losses', 0)}")
                    st.write(f"• Points For: {stats.get('PointsFor', 0)}")
                    st.write(f"• Points Against: {stats.get('PointsAgainst', 0)}")
                
                recent_form = away_context.get('recent_form', {}) if away_context else {}
                if recent_form.get('total_games', 0) > 0:
                    st.write(f"• Recent Games: {recent_form['wins']}-{recent_form['losses']}")
                
                news = away_context.get('news', []) if away_context else []
                if news:
                    st.write(f"• News Articles: {len(news)} analyzed")
                    for i, article in enumerate(news[:2]):
                        st.write(f"  - {article.get('Title', 'No title')[:40]}...")
                else:
                    st.write("• No news articles found")
        
        except Exception as e:
            st.warning(f"Could not load detailed database information: {e}")
    
    # LLM Analysis
    if 'llm_analysis' in prediction and prediction['llm_analysis'] != "LLM analysis unavailable":
        st.subheader("🤖 AI Analysis")
        st.write(prediction['llm_analysis'])
    
    # Prediction explanation
    st.subheader("📝 Prediction Explanation")
    
    if prediction['ensemble_score'] > 0:
        st.success(f"""
        **Prediction Summary**: {home_team} is predicted to win this game.
        
        **Key Factors**:
        - The ensemble model combines multiple data sources for a comprehensive analysis
        - Time series analysis shows historical trends and patterns
        - Statistical modeling considers current player and team performance
        - Sentiment analysis factors in recent news and contextual information
        - LLM enhancement provides narrative context and reasoning
        
        **Confidence Level**: {confidence:.1%}
        """)
    else:
        st.info(f"""
        **Prediction Summary**: {away_team} is predicted to win this game.
        
        **Key Factors**:
        - The ensemble model combines multiple data sources for a comprehensive analysis
        - Time series analysis shows historical trends and patterns
        - Statistical modeling considers current player and team performance
        - Sentiment analysis factors in recent news and contextual information
        - LLM enhancement provides narrative context and reasoning
        
        **Confidence Level**: {confidence:.1%}
        """)

def show_model_insights():
    """Show insights about the hybrid model"""
    st.header("🔍 Model Insights")
    
    st.markdown("""
    ### How the Hybrid Model Works
    
    Our hybrid approach combines four different modeling strategies:
    
    1. **Time Series Analysis (ARIMA)**
       - Analyzes historical game patterns
       - Identifies trends and seasonality
       - Predicts score movements over time
    
    2. **Statistical Modeling (XGBoost/Random Forest)**
       - Uses player and team statistics
       - Considers performance metrics
       - Learns complex non-linear relationships
    
    3. **Sentiment Analysis (TextBlob/NLTK)**
       - Analyzes news sentiment
       - Considers contextual factors
       - Factors in public opinion and media coverage
    
    4. **LLM Enhancement (Ollama)**
       - Provides narrative context
       - Analyzes injury impacts
       - Generates strategic insights
    
    ### Ensemble Strategy
    
    The final prediction is a weighted combination of all models:
    - Weights can be adjusted based on model performance
    - Adaptive weighting based on recent accuracy
    - Confidence scoring for prediction reliability
    """)

def show_model_performance():
    """Show model performance statistics"""
    st.header("📈 Model Performance")
    
    try:
        # Import the performance function
        from database_prediction import get_model_performance_stats
        
        # Get performance statistics
        stats = get_model_performance_stats()
        
        if stats['total_predictions'] == 0:
            st.info("No prediction data available yet. Make some predictions to see performance statistics.")
            return
        
        # Overall performance
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Overall Accuracy",
                f"{stats['overall_accuracy']:.1%}",
                help="Percentage of correct predictions"
            )
        
        with col2:
            st.metric(
                "Total Predictions",
                stats['total_predictions'],
                help="Number of predictions made"
            )
        
        with col3:
            st.metric(
                "Recent Accuracy",
                f"{stats['recent_accuracy']:.1%}",
                help="Accuracy of last 50 predictions"
            )
        
        with col4:
            st.metric(
                "Model Reliability",
                stats['model_reliability'],
                help="Overall model reliability rating"
            )
        
        # Confidence vs Accuracy chart
        if stats['confidence_accuracy']:
            st.subheader("Confidence vs Accuracy")
            
            conf_levels = list(stats['confidence_accuracy'].keys())
            accuracies = [stats['confidence_accuracy'][level]['accuracy'] for level in conf_levels]
            sample_sizes = [stats['confidence_accuracy'][level]['total_predictions'] for level in conf_levels]
            
            # Create DataFrame for plotting
            import pandas as pd
            import plotly.express as px
            
            df = pd.DataFrame({
                'Confidence Level': conf_levels,
                'Accuracy': accuracies,
                'Sample Size': sample_sizes
            })
            
            # Create bubble chart
            fig = px.scatter(
                df, 
                x='Confidence Level', 
                y='Accuracy',
                size='Sample Size',
                title="Prediction Accuracy by Confidence Level",
                labels={'Confidence Level': 'Confidence Level', 'Accuracy': 'Actual Accuracy'}
            )
            
            # Add diagonal line for perfect calibration
            fig.add_shape(
                type="line",
                x0=0, y0=0, x1=1, y1=1,
                line=dict(color="red", width=2, dash="dash"),
                name="Perfect Calibration"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show calibration table
            st.subheader("Confidence Calibration Table")
            st.dataframe(df, use_container_width=True)
        
        # Performance trends
        st.subheader("Performance Analysis")
        
        if stats['overall_accuracy'] >= 0.7:
            st.success("✅ Model is performing well with high accuracy!")
        elif stats['overall_accuracy'] >= 0.6:
            st.warning("⚠️ Model performance is moderate. Consider reviewing data quality.")
        else:
            st.error("❌ Model performance is low. Please check data sources and model configuration.")
        
        # Recommendations
        st.subheader("Recommendations")
        
        if stats['recent_accuracy'] < stats['overall_accuracy'] * 0.8:
            st.info("📉 Recent performance is declining. Consider updating model weights or data sources.")
        
        if stats['model_reliability'] == 'Low':
            st.info("🔧 Model reliability is low. Focus on improving data quality and model calibration.")
        
        if stats['total_predictions'] < 50:
            st.info("📊 More predictions needed for reliable statistics. Continue making predictions to improve calibration.")
    
    except Exception as e:
        st.error(f"Could not load performance statistics: {e}")
        st.info("Make sure the database_prediction module is properly configured.")

def show_configuration():
    """Show configuration options"""
    st.header("⚙️ Model Configuration")
    st.write("Advanced configuration options for the hybrid model.")
    
    # Show current model status
    if 'hybrid_model' in st.session_state:
        st.success("✅ Hybrid model is loaded and ready")
        st.json(st.session_state.hybrid_model.weights)
    else:
        st.warning("⚠️ Hybrid model not yet initialized")
        st.write("Click 'Make Predictions' to initialize the model.")

if __name__ == "__main__":
    app()
