#!/usr/bin/env python3
"""
Quick test script for the NBA Hybrid Model
Demonstrates the model's prediction capabilities
"""

import numpy as np
import pandas as pd
from hybrid_model import HybridModel, prepare_match_data, prepare_player_data, prepare_news_data

def quick_test():
    """Quick test of the hybrid model"""
    print("🏀 NBA Hybrid Model Quick Test")
    print("=" * 40)
    
    # Create minimal sample data
    np.random.seed(42)
    
    # Sample matches data
    dates = pd.date_range('2023-01-01', periods=50, freq='D')
    teams = ['Lakers', 'Warriors', 'Celtics', 'Heat']
    
    matches_data = []
    for i in range(50):
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
        for i in range(5):  # 5 players per team
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
    
    # Sample news data
    news_data = []
    for i in range(20):
        team = np.random.choice(teams)
        title = f"{team} shows impressive performance"
        content = f"This is a news article about {team} and their recent performance."
        news_data.append({
            'NewsID': i + 1,
            'Title': title,
            'Content': content
        })
    
    news_df = pd.DataFrame(news_data)
    
    # Prepare data
    print("Preparing data...")
    prepared_matches = prepare_match_data(matches_df)
    prepared_players = prepare_player_data(players_df)
    prepared_news = prepare_news_data(news_df)
    
    # Initialize and train model
    print("Training hybrid model...")
    model = HybridModel(weights={
        'time_series': 0.3,
        'statistical': 0.4,
        'sentiment': 0.2,
        'llm': 0.1
    })
    
    model.fit(prepared_matches, prepared_players, None, prepared_news)
    
    # Make a prediction
    print("\nMaking prediction...")
    context_data = {
        'player_stats': prepared_players[prepared_players['Team'].isin(['Lakers', 'Warriors'])],
        'recent_form': {
            'Lakers': 'W-L: 5-2',
            'Warriors': 'W-L: 4-3'
        },
        'head_to_head': 'Lakers won 2 of last 3 meetings'
    }
    
    prediction = model.predict_game('Lakers', 'Warriors', context_data)
    
    # Display results
    print(f"\n📊 Prediction Results:")
    print(f"Time Series Score: {prediction['time_series']:.3f}")
    print(f"Statistical Score: {prediction['statistical']:.3f}")
    print(f"Sentiment Score: {prediction['sentiment']:.3f}")
    print(f"Ensemble Score: {prediction['ensemble_score']:.3f}")
    print(f"Predicted Winner: {prediction['predicted_winner']}")
    
    if 'llm_analysis' in prediction:
        print(f"\n🤖 LLM Analysis Preview:")
        print(prediction['llm_analysis'][:150] + "...")
    
    # Show feature importance
    try:
        importance = model.get_feature_importance()
        if importance:
            print(f"\n🔍 Top Feature Importance:")
            sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:3]
            for feature, imp in sorted_features:
                print(f"  {feature}: {imp:.4f}")
    except:
        print("\nFeature importance not available")
    
    print(f"\n✅ Test completed successfully!")
    return model

if __name__ == "__main__":
    try:
        model = quick_test()
        print(f"\nModel weights: {model.weights}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

