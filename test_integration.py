#!/usr/bin/env python3
"""
Integration test for NBA Predict with Hybrid Model
Tests that all components work together properly
"""

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        from streamlit_hybrid_predict import create_prediction_interface, show_model_insights
        print("✅ Hybrid predict functions imported")
    except ImportError as e:
        print(f"❌ Hybrid predict import failed: {e}")
        return False
    
    try:
        from hybrid_model import HybridModel
        print("✅ Hybrid model imported")
    except ImportError as e:
        print(f"❌ Hybrid model import failed: {e}")
        return False
    
    try:
        import Home
        print("✅ Home.py imported")
    except ImportError as e:
        print(f"❌ Home.py import failed: {e}")
        return False
    
    return True

def test_hybrid_model():
    """Test that hybrid model works"""
    print("\nTesting hybrid model...")
    
    try:
        from hybrid_model import HybridModel
        from test_hybrid_model import quick_test
        
        # Run the quick test
        model = quick_test()
        print("✅ Hybrid model test passed")
        return True
    except Exception as e:
        print(f"❌ Hybrid model test failed: {e}")
        return False

def test_streamlit_components():
    """Test that Streamlit components work"""
    print("\nTesting Streamlit components...")
    
    try:
        from streamlit_hybrid_predict import create_prediction_interface, show_model_insights
        
        # Test that functions are callable
        assert callable(create_prediction_interface)
        assert callable(show_model_insights)
        print("✅ Streamlit components are callable")
        return True
    except Exception as e:
        print(f"❌ Streamlit components test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🧪 NBA Predict Integration Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Hybrid Model Test", test_hybrid_model),
        ("Streamlit Components Test", test_streamlit_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Integration is working correctly.")
        print("\n🚀 You can now run the app with:")
        print("   py -3.12 run_app.py")
        print("   or")
        print("   streamlit run Home.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
