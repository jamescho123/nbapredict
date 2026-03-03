#!/usr/bin/env python3
"""
Test the Streamlit hybrid model fix
"""

def test_model_initialization():
    """Test that the model initializes and trains correctly"""
    print("Testing Streamlit hybrid model initialization...")
    
    try:
        from streamlit_hybrid_predict import load_hybrid_model, create_sample_training_data
        
        # Test sample data creation
        print("Creating sample training data...")
        sample_data = create_sample_training_data()
        print(f"✅ Sample data created: {list(sample_data.keys())}")
        
        # Test model loading (this should trigger training)
        print("Loading hybrid model...")
        model = load_hybrid_model()
        
        if model and model.is_fitted:
            print("✅ Model loaded and trained successfully!")
            
            # Test a prediction
            print("Testing prediction...")
            context_data = {
                'player_stats': sample_data['players'][sample_data['players']['Team'].isin(['Lakers', 'Warriors'])],
                'recent_form': {
                    'Lakers': 'W-L: 5-2',
                    'Warriors': 'W-L: 4-3'
                },
                'head_to_head': 'Lakers won 2 of last 3 meetings'
            }
            
            prediction = model.predict_game('Lakers', 'Warriors', context_data)
            print(f"✅ Prediction successful: {prediction['predicted_winner']}")
            print(f"   Ensemble Score: {prediction['ensemble_score']:.3f}")
            
            return True
        else:
            print("❌ Model not properly trained")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test"""
    print("🧪 Testing Streamlit Hybrid Model Fix")
    print("=" * 50)
    
    success = test_model_initialization()
    
    if success:
        print("\n🎉 All tests passed! The Streamlit interface should now work correctly.")
        print("\nYou can now run:")
        print("  py -3.12 run_app.py")
        print("  or")
        print("  streamlit run Home.py")
    else:
        print("\n❌ Tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
