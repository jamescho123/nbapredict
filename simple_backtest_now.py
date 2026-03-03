#!/usr/bin/env python3
"""
Simple Backtest - Run Now
Quick backtest with current improvements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_prediction import predict_game_outcome
import psycopg2
import pandas as pd

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

def main():
    print("🏀 Simple Backtest with Improvements")
    print("=" * 60)
    
    # Test matchups
    matchups = [
        ("Boston Celtics", "Detroit Pistons"),
        ("Los Angeles Lakers", "Golden State Warriors"),
        ("Miami Heat", "Charlotte Hornets"),
        ("Denver Nuggets", "Portland Trail Blazers"),
        ("Phoenix Suns", "San Antonio Spurs"),
    ]
    
    results = []
    
    for i, (home, away) in enumerate(matchups, 1):
        print(f"\n{'='*60}")
        print(f"🎮 Test {i}/5: {away} @ {home}")
        print(f"{'='*60}")
        
        try:
            prediction = predict_game_outcome(home, away)
            
            if prediction:
                winner = prediction['predicted_winner']
                confidence = prediction['confidence']
                home_strength = prediction['home_strength']
                away_strength = prediction['away_strength']
                home_prob = prediction.get('home_win_probability', 0.5)
                away_prob = prediction.get('away_win_probability', 0.5)
                
                print(f"\n🏆 PREDICTION RESULTS:")
                print(f"   Winner: {winner}")
                print(f"   Confidence: {confidence:.1%}")
                print(f"\n💪 TEAM STRENGTHS:")
                print(f"   {home}: {home_strength:.3f}")
                print(f"   {away}: {away_strength:.3f}")
                print(f"\n🎲 WIN PROBABILITIES:")
                print(f"   {home}: {home_prob:.1%}")
                print(f"   {away}: {away_prob:.1%}")
                
                # Simulate result based on win probability
                import random
                random.seed(i)
                actual_winner = home if random.random() < home_prob else away
                is_correct = (winner == actual_winner)
                
                print(f"\n🎯 SIMULATED RESULT:")
                print(f"   Actual Winner: {actual_winner}")
                print(f"   Prediction: {'✅ CORRECT' if is_correct else '❌ INCORRECT'}")
                
                results.append({
                    'home': home,
                    'away': away,
                    'predicted': winner,
                    'actual': actual_winner,
                    'correct': is_correct,
                    'confidence': confidence,
                    'home_strength': home_strength,
                    'away_strength': away_strength
                })
            else:
                print("❌ No prediction generated")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    if results:
        print(f"\n{'='*60}")
        print(f"📊 BACKTEST SUMMARY")
        print(f"{'='*60}")
        
        correct = sum(1 for r in results if r['correct'])
        total = len(results)
        accuracy = correct / total
        avg_confidence = sum(r['confidence'] for r in results) / total
        
        print(f"Total Games: {total}")
        print(f"Correct Predictions: {correct}")
        print(f"Accuracy: {accuracy:.1%}")
        print(f"Average Confidence: {avg_confidence:.1%}")
        
        # Check if improvements worked
        print(f"\n🔍 IMPROVEMENT CHECKS:")
        
        # Check for variable strengths
        strengths = [r['home_strength'] for r in results] + [r['away_strength'] for r in results]
        unique_strengths = len(set(strengths))
        if unique_strengths > 5:
            print(f"✅ Team strengths are variable ({unique_strengths} unique values)")
        else:
            print(f"⚠️  Team strengths may still be too similar")
        
        # Check confidence range
        confidences = [r['confidence'] for r in results]
        min_conf = min(confidences)
        max_conf = max(confidences)
        if max_conf <= 0.85:
            print(f"✅ Confidence is realistic (max: {max_conf:.1%})")
        else:
            print(f"⚠️  Confidence too high (max: {max_conf:.1%})")
        
        if accuracy >= 0.5:
            print(f"✅ Model shows reasonable performance")
        else:
            print(f"⚠️  Model needs more tuning")
        
    print(f"\n✅ Backtest complete!")

if __name__ == "__main__":
    main()

