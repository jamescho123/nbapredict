import pandas as pd
import numpy as np
from hybrid_model import HybridModel, prepare_match_data, prepare_player_data, prepare_news_data
import psycopg2
from psycopg2.extras import RealDictCursor
import warnings
warnings.filterwarnings('ignore')

def connect_to_database():
    """Connect to PostgreSQL database"""
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="James",
            user="postgres",
            password="jcjc1749"
        )
        return connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def load_data_from_db():
    """Load data from database tables"""
    connection = connect_to_database()
    if not connection:
        print("Using sample data instead...")
        return create_sample_data()
    
    try:
        # Load matches data
        matches_query = """
        SELECT "Date" as date, "HomeTeamName" as home_team, "VisitorTeamName" as away_team,
               "HomeTeamScore" as home_score, "VisitorPoints" as away_score
        FROM "NBA"."Matches"
        ORDER BY "Date"
        """
        matches_df = pd.read_sql_query(matches_query, connection)
        
        # Load players data - note: actual table doesn't have stats, will use sample data
        players_query = """
        SELECT "PlayerName", "Position", "Height", "Weight"
        FROM "NBA"."Players"
        LIMIT 50
        """
        players_df = pd.read_sql_query(players_query, connection)
        
        # Load teams data
        teams_query = """
        SELECT "TeamName", "Wins", "Losses", "PointsFor", "PointsAgainst"
        FROM "NBA"."Teams"
        """
        teams_df = pd.read_sql_query(teams_query, connection)
        
        # Load news data
        news_query = """
        SELECT "NewsID", "Title", "Content"
        FROM "NBA"."News"
        LIMIT 100
        """
        news_df = pd.read_sql_query(news_query, connection)
        
        connection.close()
        
        print(f"Loaded {len(matches_df)} matches, {len(players_df)} players, {len(teams_df)} teams, {len(news_df)} news articles")
        return matches_df, players_df, teams_df, news_df
        
    except Exception as e:
        print(f"Error loading data: {e}")
        connection.close()
        print("Using sample data instead...")
        return create_sample_data()

def create_sample_data():
    """Create sample data for demonstration"""
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
                'points_per_game': np.random.randint(5, 30) / np.random.randint(20, 82)  # Ensure this column exists
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
    
    return matches_df, players_df, teams_df, news_df

def train_hybrid_model():
    """Train the hybrid model with loaded data"""
    print("Loading data...")
    matches_df, players_df, teams_df, news_df = load_data_from_db()
    
    print("Preparing data...")
    # Prepare data for different models
    prepared_matches = prepare_match_data(matches_df)
    prepared_players = prepare_player_data(players_df)
    prepared_news = prepare_news_data(news_df)
    
    print("Initializing hybrid model...")
    # Initialize hybrid model with custom weights
    hybrid_model = HybridModel(weights={
        'time_series': 0.25,
        'statistical': 0.45,
        'sentiment': 0.20,
        'llm': 0.10
    })
    
    print("Training hybrid model...")
    # Train the model
    hybrid_model.fit(
        matches_data=prepared_matches,
        players_data=prepared_players,
        teams_data=teams_df,
        news_data=prepared_news
    )
    
    return hybrid_model, prepared_matches, prepared_players, teams_df, prepared_news

def make_predictions(hybrid_model, prepared_matches, prepared_players, teams_df):
    """Make predictions using the trained hybrid model"""
    print("\n" + "="*50)
    print("MAKING PREDICTIONS")
    print("="*50)
    
    # Sample prediction context
    sample_teams = ['Lakers', 'Warriors', 'Celtics', 'Heat']
    
    for i in range(3):
        home_team = sample_teams[i % len(sample_teams)]
        away_team = sample_teams[(i + 1) % len(sample_teams)]
        
        print(f"\nPrediction {i+1}: {home_team} vs {away_team}")
        print("-" * 40)
        
        # Create context data for prediction
        context_data = {
            'player_stats': prepared_players[prepared_players['Team'].isin([home_team, away_team])],
            'recent_form': {
                home_team: f"W-L: {teams_df[teams_df['TeamName'] == home_team]['Wins'].iloc[0]}-{teams_df[teams_df['TeamName'] == home_team]['Losses'].iloc[0]}",
                away_team: f"W-L: {teams_df[teams_df['TeamName'] == away_team]['Wins'].iloc[0]}-{teams_df[teams_df['TeamName'] == away_team]['Losses'].iloc[0]}"
            },
            'head_to_head': f"Recent meetings: {home_team} has won 2 of last 3 games"
        }
        
        try:
            # Make prediction
            prediction = hybrid_model.predict_game(home_team, away_team, context_data)
            
            # Display results
            print(f"Time Series Score: {prediction['time_series']:.2f}")
            print(f"Statistical Score: {prediction['statistical']:.2f}")
            print(f"Sentiment Score: {prediction['sentiment']:.2f}")
            print(f"Ensemble Score: {prediction['ensemble_score']:.2f}")
            print(f"Predicted Winner: {prediction['predicted_winner']}")
            
            if 'llm_analysis' in prediction and prediction['llm_analysis'] != "LLM analysis unavailable":
                print(f"\nLLM Analysis:")
                print(prediction['llm_analysis'][:200] + "...")
            
        except Exception as e:
            print(f"Prediction failed: {e}")
    
    # Show feature importance
    try:
        feature_importance = hybrid_model.get_feature_importance()
        if feature_importance:
            print(f"\n" + "="*50)
            print("FEATURE IMPORTANCE")
            print("="*50)
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            for feature, importance in sorted_features[:10]:
                print(f"{feature}: {importance:.4f}")
    except Exception as e:
        print(f"Feature importance not available: {e}")

def main():
    """Main function to run the complete workflow"""
    print("NBA Hybrid Model Training and Prediction")
    print("=" * 50)
    
    try:
        # Train the model
        hybrid_model, prepared_matches, prepared_players, teams_df, prepared_news = train_hybrid_model()
        
        # Make predictions
        make_predictions(hybrid_model, prepared_matches, prepared_players, teams_df)
        
        print(f"\n" + "="*50)
        print("WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*50)
        
        # Save model weights for future use
        print(f"\nModel weights: {hybrid_model.weights}")
        print("You can now use this trained model for predictions!")
        
    except Exception as e:
        print(f"Error in main workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
