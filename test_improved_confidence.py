#!/usr/bin/env python3
"""
Test the improved confidence calculation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_prediction import predict_game_outcome

def test_confidence_improvements():
    """Test the improved confidence calculation"""
    print("🎯 Testing Improved Confidence Calculation")
    print("=" * 50)
    
    # Test teams
    test_matchups = [
        ("Los Angeles Lakers", "Golden State Warriors"),
        ("Boston Celtics", "Miami Heat"),
        ("Denver Nuggets", "Phoenix Suns"),
        ("Milwaukee Bucks", "Philadelphia 76ers")
    ]
    
    for home_team, away_team in test_matchups:
        print(f"\n🏀 {away_team} @ {home_team}")
        print("-" * 40)
        
        try:
            prediction = predict_game_outcome(home_team, away_team)
            
            print(f"Predicted Winner: {prediction.get('predicted_winner', 'Unknown')}")
            print(f"Confidence: {prediction.get('confidence', 0):.1%}")
            print(f"Enhanced Confidence: {prediction.get('enhanced_confidence', prediction.get('confidence', 0)):.1%}")
            
            # Show data quality factors
            data_quality = prediction.get('data_quality_factors', {})
            print(f"Data Quality Factors:")
            for factor, value in data_quality.items():
                print(f"  - {factor}: {value:.3f}")
            
            # Show team strengths
            print(f"Team Strengths:")
            print(f"  - {home_team}: {prediction.get('home_strength', 0):.3f}")
            print(f"  - {away_team}: {prediction.get('away_strength', 0):.3f}")
            
            # Show confidence interval
            conf_interval = prediction.get('confidence_interval', {})
            if conf_interval:
                print(f"Confidence Interval: {conf_interval.get('lower', 0):.1%} - {conf_interval.get('upper', 0):.1%}")
            
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
    
    print("\n✅ Confidence test completed!")
    print("\n📊 Summary:")
    print("- Enhanced data quality scoring (minimum 20%)")
    print("- More generous base confidence calculation")
    print("- Better fallback for limited data")
    print("- Improved confidence intervals")

if __name__ == "__main__":
    test_confidence_improvements()
