#!/usr/bin/env python3
"""
Test Realistic Confidence Levels
Verify that confidence scores are now realistic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_prediction import predict_game_outcome

def test_realistic_confidence():
    """Test that confidence levels are now realistic"""
    print("🎯 Testing Realistic Confidence Levels")
    print("=" * 50)
    
    # Test various team matchups
    test_games = [
        ("Boston Celtics", "Detroit Pistons"),      # Strong vs weak
        ("Los Angeles Lakers", "Golden State Warriors"),  # Similar teams
        ("Miami Heat", "Charlotte Hornets"),        # Medium vs weak
        ("Denver Nuggets", "Portland Trail Blazers"),  # Strong vs weak
        ("Phoenix Suns", "San Antonio Spurs"),      # Medium vs weak
    ]
    
    confidence_scores = []
    
    for i, (home_team, away_team) in enumerate(test_games, 1):
        print(f"\n🎮 Test {i}: {away_team} @ {home_team}")
        print("-" * 40)
        
        try:
            prediction = predict_game_outcome(home_team, away_team)
            
            if prediction:
                winner = prediction['predicted_winner']
                confidence = prediction['confidence']
                home_strength = prediction['home_strength']
                away_strength = prediction['away_strength']
                home_win_prob = prediction.get('home_win_probability', 0.5)
                away_win_prob = prediction.get('away_win_probability', 0.5)
                
                print(f"🏆 Winner: {winner}")
                print(f"📊 Confidence: {confidence:.1%}")
                print(f"💪 Strengths: {home_team} {home_strength:.3f}, {away_team} {away_win_prob:.3f}")
                print(f"🎲 Win Probs: {home_team} {home_win_prob:.1%}, {away_team} {away_win_prob:.1%}")
                
                confidence_scores.append(confidence)
                
                # Check if confidence is realistic
                if confidence > 0.85:
                    print("⚠️  WARNING: Confidence too high (>85%)")
                elif confidence > 0.70:
                    print("✅ High confidence (70-85%)")
                elif confidence > 0.50:
                    print("✅ Moderate confidence (50-70%)")
                else:
                    print("✅ Low confidence (<50%)")
                
            else:
                print("❌ No prediction generated")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Summary statistics
    if confidence_scores:
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        max_confidence = max(confidence_scores)
        min_confidence = min(confidence_scores)
        
        print(f"\n📊 Confidence Summary:")
        print(f"   Average: {avg_confidence:.1%}")
        print(f"   Range: {min_confidence:.1%} - {max_confidence:.1%}")
        print(f"   Count: {len(confidence_scores)} predictions")
        
        # Evaluate if confidence is realistic
        if avg_confidence > 0.80:
            print("⚠️  WARNING: Average confidence too high")
        elif avg_confidence > 0.60:
            print("✅ Realistic average confidence")
        else:
            print("✅ Conservative average confidence")
        
        if max_confidence > 0.90:
            print("⚠️  WARNING: Some predictions have unrealistic confidence (>90%)")
        else:
            print("✅ All predictions have realistic confidence levels")
    
    print(f"\n✅ Confidence test complete!")

if __name__ == "__main__":
    test_realistic_confidence()
