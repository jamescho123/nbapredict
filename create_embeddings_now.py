#!/usr/bin/env python3
"""
Create vector embeddings for NBA data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vector_embedding_system import NBAVectorEmbeddingSystem

def main():
    print("🧠 Creating NBA Vector Embeddings")
    print("=" * 40)
    
    # Initialize the embedding system
    embedding_system = NBAVectorEmbeddingSystem()
    
    try:
        # Connect to database
        if embedding_system.connect_to_database():
            print("✅ Connected to database")
            
            # Create all embeddings
            print("\n📊 Creating embeddings...")
            success = embedding_system.create_all_embeddings()
            
            if success:
                print("\n🎉 Vector embeddings created successfully!")
                print("\n📋 What was created:")
                print(f"  - Team embeddings: {len(embedding_system.team_embeddings)}")
                print(f"  - Player embeddings: {len(embedding_system.player_embeddings)}")
                print(f"  - Match embeddings: {len(embedding_system.match_embeddings)}")
                print("\n✅ You can now use enhanced predictions in the Streamlit app!")
            else:
                print("❌ Some embeddings failed to create")
        else:
            print("❌ Failed to connect to database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        embedding_system.close_connection()

if __name__ == "__main__":
    main()
