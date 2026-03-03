#!/usr/bin/env python3
"""
Test Data Retrieval
Check what data is actually being found for teams
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_prediction import get_team_context_data, predict_game_outcome

def test_data_retrieval():
    """Test what data is being retrieved for teams"""
    print("🧪 Testing Data Retrieval")
    print("=" * 50)
    
    # Test teams
    test_teams = ["Boston Celtics", "Los Angeles Lakers", "Golden State Warriors"]
    
    for team in test_teams:
        print(f"\n🏀 Testing {team}:")
        print("-" * 30)
        
        try:
            # Get team context
            context = get_team_context_data(team)
            
            if context:
                print(f"✅ Context retrieved successfully")
                
                # Show what data we got
                team_stats = context.get('team_stats', {})
                recent_form = context.get('recent_form', {})
                news = context.get('news', [])
                players = context.get('players', [])
                
                print(f"   Team Stats: {team_stats}")
                print(f"   Recent Form: {recent_form}")
                print(f"   News Articles: {len(news)}")
                print(f"   Players: {len(players)}")
                
                if news:
                    print(f"   Recent News Sample:")
                    for i, article in enumerate(news[:2]):
                        print(f"     {i+1}. {article.get('Title', 'No title')} ({article.get('Date', 'No date')})")
            else:
                print(f"❌ No context retrieved")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test a prediction to see the full flow
    print(f"\n🎯 Testing Full Prediction:")
    print("-" * 30)
    
    try:
        prediction = predict_game_outcome("Boston Celtics", "Detroit Pistons")
        
        if prediction:
            print(f"✅ Prediction generated")
            print(f"   Winner: {prediction.get('predicted_winner', 'Unknown')}")
            print(f"   Confidence: {prediction.get('confidence', 0):.1%}")
            print(f"   Home Strength: {prediction.get('home_strength', 0):.3f}")
            print(f"   Away Strength: {prediction.get('away_strength', 0):.3f}")
        else:
            print(f"❌ No prediction generated")
            
    except Exception as e:
        print(f"❌ Prediction error: {e}")

if __name__ == "__main__":
    test_data_retrieval()
