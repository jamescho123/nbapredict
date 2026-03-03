#!/usr/bin/env python3
"""
Test the updated prediction system
Verify that team strengths and win probabilities are realistic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_prediction import predict_game_outcome

def test_prediction_changes():
    """Test the updated prediction system"""
    print("🧪 Testing Updated Prediction System")
    print("=" * 50)
    
    # Test teams
    test_games = [
        ("Boston Celtics", "Detroit Pistons"),  # Strong vs weak team
        ("Los Angeles Lakers", "Golden State Warriors"),  # Similar strength teams
        ("Miami Heat", "Charlotte Hornets"),  # Medium vs weak team
    ]
    
    for i, (home_team, away_team) in enumerate(test_games, 1):
        print(f"\n🎮 Test {i}: {away_team} @ {home_team}")
        print("-" * 40)
        
        try:
            # Make prediction
            prediction = predict_game_outcome(home_team, away_team)
            
            if prediction:
                # Display results
                winner = prediction['predicted_winner']
                confidence = prediction['confidence']
                home_strength = prediction['home_strength']
                away_strength = prediction['away_strength']
                home_win_prob = prediction.get('home_win_probability', 0.5)
                away_win_prob = prediction.get('away_win_probability', 0.5)
                
                print(f"🏆 Predicted Winner: {winner}")
                print(f"📊 Confidence: {confidence:.1%}")
                print(f"💪 Team Strengths:")
                print(f"   {home_team}: {home_strength:.3f}")
                print(f"   {away_team}: {away_strength:.3f}")
                print(f"🎲 Win Probabilities:")
                print(f"   {home_team}: {home_win_prob:.1%}")
                print(f"   {away_team}: {away_win_prob:.1%}")
                
                # Verify realistic values
                if home_strength == away_strength:
                    print("⚠️  WARNING: Team strengths are identical!")
                else:
                    print("✅ Team strengths are different")
                
                if home_win_prob == 0.6 and away_win_prob == 0.4:
                    print("⚠️  WARNING: Win probabilities are fixed at 60%/40%!")
                else:
                    print("✅ Win probabilities are realistic")
                
                # Check if probabilities add up to 100%
                total_prob = home_win_prob + away_win_prob
                if abs(total_prob - 1.0) < 0.01:
                    print("✅ Win probabilities sum to 100%")
                else:
                    print(f"⚠️  Win probabilities sum to {total_prob:.1%}")
                
            else:
                print("❌ No prediction generated")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✅ Prediction system test complete!")

if __name__ == "__main__":
    test_prediction_changes()
