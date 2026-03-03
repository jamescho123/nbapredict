#!/usr/bin/env python3
"""
NBA Predict App Launcher
Launches the integrated Streamlit app with hybrid model capabilities
"""

import subprocess
import sys
import os

def main():
    """Launch the NBA Predict Streamlit app"""
    print("🏀 Starting NBA Predict App...")
    print("=" * 50)
    print("Features available:")
    print("✅ Basic Predictions")
    print("✅ Hybrid AI Predictions") 
    print("✅ News & Statistics")
    print("✅ Semantic Search")
    print("✅ Team Rankings")
    print("=" * 50)
    print("Opening in your browser...")
    print("Press Ctrl+C to stop the app")
    print("=" * 50)
    
    try:
        # Run the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "Home.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped. Thanks for using NBA Predict!")
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        print("Make sure you have Streamlit installed: pip install streamlit")

if __name__ == "__main__":
    main()
