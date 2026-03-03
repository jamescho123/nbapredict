#!/usr/bin/env python3
"""
Test script for the vector embedding system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vector_embedding_system import NBAVectorEmbeddingSystem
from vector_enhanced_prediction import VectorEnhancedPredictionSystem

def test_embedding_creation():
    """Test creating vector embeddings"""
    print("🧠 Testing Vector Embedding Creation")
    print("=" * 50)
    
    embedding_system = NBAVectorEmbeddingSystem()
    
    try:
        if embedding_system.connect_to_database():
            print("✅ Database connection successful")
            
            # Test creating embeddings
            print("\n📊 Creating team embeddings...")
            team_success = embedding_system.create_team_embeddings()
            print(f"Team embeddings: {'✅ Success' if team_success else '❌ Failed'}")
            
            print("\n👥 Creating player embeddings...")
            player_success = embedding_system.create_player_embeddings()
            print(f"Player embeddings: {'✅ Success' if player_success else '❌ Failed'}")
            
            print("\n🏀 Creating match embeddings...")
            match_success = embedding_system.create_match_embeddings()
            print(f"Match embeddings: {'✅ Success' if match_success else '❌ Failed'}")
            
            # Test loading embeddings
            print("\n🔄 Testing embedding loading...")
            load_success = embedding_system.load_embeddings_from_db()
            print(f"Load embeddings: {'✅ Success' if load_success else '❌ Failed'}")
            
            if load_success:
                print(f"Loaded {len(embedding_system.team_embeddings)} team embeddings")
                print(f"Loaded {len(embedding_system.player_embeddings)} player embeddings")
                print(f"Loaded {len(embedding_system.match_embeddings)} match embeddings")
                
                # Test similarity search
                print("\n🔍 Testing similarity search...")
                if embedding_system.team_embeddings:
                    team_names = list(embedding_system.team_embeddings.values())[:3]
                    if team_names:
                        test_team = team_names[0]['name']
                        similar_teams = embedding_system.find_similar_teams(test_team, top_k=3)
                        print(f"Similar teams to {test_team}:")
                        for team, similarity in similar_teams:
                            print(f"  - {team}: {similarity:.3f}")
            
            embedding_system.close_connection()
            return team_success and player_success and match_success
            
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_enhanced_prediction():
    """Test vector-enhanced prediction system"""
    print("\n🎯 Testing Vector-Enhanced Predictions")
    print("=" * 50)
    
    prediction_system = VectorEnhancedPredictionSystem()
    
    try:
        if prediction_system.connect_to_database():
            print("✅ Database connection successful")
            
            # Load embeddings
            print("\n🔄 Loading embeddings...")
            load_success = prediction_system.load_embeddings()
            print(f"Load embeddings: {'✅ Success' if load_success else '❌ Failed'}")
            
            if load_success and prediction_system.team_embeddings:
                # Test prediction
                print("\n🏀 Testing enhanced prediction...")
                home_team = "Los Angeles Lakers"
                away_team = "Golden State Warriors"
                
                prediction = prediction_system.predict_with_vector_enhancement(home_team, away_team)
                
                if prediction:
                    print(f"✅ Enhanced prediction successful!")
                    print(f"Predicted Winner: {prediction.get('predicted_winner', 'Unknown')}")
                    print(f"Traditional Confidence: {prediction.get('confidence', 0):.2%}")
                    print(f"Enhanced Confidence: {prediction.get('enhanced_confidence', 0):.2%}")
                    print(f"Vector Confidence Boost: {prediction.get('vector_confidence_boost', 0):.2%}")
                    
                    # Show vector insights
                    vector_insights = prediction.get('vector_insights', {})
                    if vector_insights:
                        print(f"\n🧠 Vector Insights:")
                        print(f"Team Similarity: {vector_insights.get('team_similarity', 0):.3f}")
                        
                        home_style = vector_insights.get('home_team_style', {})
                        print(f"Home Team Style Confidence: {home_style.get('style_confidence', 0):.3f}")
                        
                        away_style = vector_insights.get('away_team_style', {})
                        print(f"Away Team Style Confidence: {away_style.get('style_confidence', 0):.3f}")
                        
                        hist_similarity = vector_insights.get('historical_match_similarity', {})
                        print(f"Historical Match Similarity: {hist_similarity.get('avg_similarity', 0):.3f}")
                else:
                    print("❌ Enhanced prediction failed")
            else:
                print("⚠️ No embeddings available for prediction testing")
            
            prediction_system.close_connection()
            return True
            
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🏀 NBA Vector Embedding System Test")
    print("=" * 60)
    
    # Test embedding creation
    embedding_success = test_embedding_creation()
    
    # Test enhanced prediction
    prediction_success = test_enhanced_prediction()
    
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Embedding Creation: {'✅ Pass' if embedding_success else '❌ Fail'}")
    print(f"Enhanced Prediction: {'✅ Pass' if prediction_success else '❌ Fail'}")
    
    if embedding_success and prediction_success:
        print("\n🎉 All tests passed! Vector embedding system is ready.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
