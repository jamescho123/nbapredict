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
from database_prediction import get_team_list, predict_game_outcome, get_team_context_data

def load_hybrid_model():
    """Load or initialize the hybrid model"""
    if 'hybrid_model' not in st.session_state:
        try:
            # Initialize the model
            st.session_state.hybrid_model = HybridModel(
                weights=ENSEMBLE_CONFIG['default_weights']
            )
            st.success("Hybrid model initialized successfully!")
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
                st.success("Hybrid model trained successfully!")
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
        
        # Show team information from database
        st.subheader("Team Information")
        
        # Get team context data
        home_context = get_team_context_data(home_team)
        away_context = get_team_context_data(away_team)
        
        # Display team stats
        if home_context['team_stats']:
            stats = home_context['team_stats']
            st.metric("Record", f"{stats.get('Wins', 0)}-{stats.get('Losses', 0)}")
            win_pct = stats.get('Wins', 0) / (stats.get('Wins', 0) + stats.get('Losses', 0)) if (stats.get('Wins', 0) + stats.get('Losses', 0)) > 0 else 0
            st.metric("Win %", f"{win_pct:.1%}")
        
        recent_form = home_context['recent_form']
        st.metric("Recent Form", f"{recent_form['wins']}-{recent_form['losses']}")
        
    with col2:
        st.subheader(f"{away_team} Information")
        
        # Display away team stats
        if away_context['team_stats']:
            stats = away_context['team_stats']
            st.metric("Record", f"{stats.get('Wins', 0)}-{stats.get('Losses', 0)}")
            win_pct = stats.get('Wins', 0) / (stats.get('Wins', 0) + stats.get('Losses', 0)) if (stats.get('Wins', 0) + stats.get('Losses', 0)) > 0 else 0
            st.metric("Win %", f"{win_pct:.1%}")
        
        recent_form = away_context['recent_form']
        st.metric("Recent Form", f"{recent_form['wins']}-{recent_form['losses']}")
        
        # Additional context controls
        st.subheader("Advanced Settings")
        home_advantage = st.slider("Home Advantage Factor", 0.0, 0.3, 0.1, 0.01)
        rest_days_home = st.number_input("Home Team Rest Days", min_value=0, max_value=7, value=1)
        rest_days_away = st.number_input("Away Team Rest Days", min_value=0, max_value=7, value=1)
    
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
                            home_team: f"W-L: {home_context['recent_form']['wins']}-{home_context['recent_form']['losses']}",
                            away_team: f"W-L: {away_context['recent_form']['wins']}-{away_context['recent_form']['losses']}"
                        },
                        'head_to_head': f"Recent meetings: {home_team} vs {away_team}",
                        'home_advantage': home_advantage,
                        'rest_days': {
                            'home': rest_days_home,
                            'away': rest_days_away
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

def display_prediction_results(prediction, home_team, away_team):
    """Display the prediction results in an attractive format"""
    st.header("📊 Prediction Results")
    
    # Main prediction result
    winner = prediction['predicted_winner']
    confidence = prediction['confidence']
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if winner == home_team:
            st.success(f"🏠 **{winner}** wins at home")
        else:
            st.info(f"✈️ **{winner}** wins away")
        
        st.progress(confidence)
        st.write(f"**Confidence: {confidence:.1%}**")
    
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
                        news_id = article.get('NewsID')
                        title_text = article.get('Title', 'No Title')
                        display_url = f"/?news_id={news_id}"
                            
                        st.write(f"  - [{title_text[:40]}...]({display_url})")
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
                        news_id = article.get('NewsID')
                        title_text = article.get('Title', 'No Title')
                        display_url = f"/?news_id={news_id}"
                            
                        st.write(f"  - [{title_text[:40]}...]({display_url})")
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

def main():
    """Main function for the Streamlit app"""
    st.set_page_config(
        page_title="NBA Hybrid Predictions",
        page_icon="🏀",
        layout="wide"
    )
    
    # Navigation
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Predictions", "Model Insights", "Configuration"]
    )
    
    if page == "Predictions":
        create_prediction_interface()
    elif page == "Model Insights":
        show_model_insights()
    elif page == "Configuration":
        st.header("⚙️ Model Configuration")
        st.write("Advanced configuration options will be available here.")
        
        # Show current model status
        if 'hybrid_model' in st.session_state:
            st.success("✅ Hybrid model is loaded and ready")
            st.json(st.session_state.hybrid_model.weights)
        else:
            st.warning("⚠️ Hybrid model not yet initialized")

if __name__ == "__main__":
    main()
