#!/usr/bin/env python3
"""
Test script for the NBA Entity Extraction system
"""

import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_database_schema():
    """Test database schema creation"""
    print("=== Testing Database Schema ===")
    try:
        from create_entity_schema import create_entity_schema
        create_entity_schema()
        print("✅ Database schema created successfully")
        return True
    except Exception as e:
        print(f"❌ Database schema creation failed: {e}")
        return False

def test_entity_extractor():
    """Test the entity extractor with sample data"""
    print("\n=== Testing Entity Extractor ===")
    try:
        from nba_entity_extractor import NBAEntityExtractor
        
        extractor = NBAEntityExtractor()
        
        # Test article
        test_article = """
        LeBron James dropped 42 points as the Lakers edged the Warriors 112-108. 
        Draymond Green picked up a technical foul after an altercation with Anthony Davis. 
        Anthony Davis is listed as day-to-day with a hip injury. The game was played at 
        Crypto.com Arena in Los Angeles on January 20, 2025.
        """
        
        print("Testing entity extraction...")
        extracted_data = extractor.extract_entities(test_article, "Lakers Edge Warriors in Thriller")
        
        if extracted_data:
            print("✅ Entity extraction successful")
            print(f"Found {len(extracted_data.get('entities', []))} entities")
            
            # Show sample entities
            entities = extracted_data.get('entities', [])
            for entity in entities[:3]:  # Show first 3
                print(f"  - {entity.get('type')}: {entity.get('name')}")
            
            return True
        else:
            print("❌ Entity extraction failed")
            return False
            
    except Exception as e:
        print(f"❌ Entity extractor test failed: {e}")
        return False

def test_news_processor():
    """Test the news processor"""
    print("\n=== Testing News Processor ===")
    try:
        from news_entity_processor import NewsEntityProcessor
        
        processor = NewsEntityProcessor()
        
        # Test processing a single article
        print("Testing single article processing...")
        success = processor.process_new_article(
            title="Test Article: Lakers Win",
            content="LeBron James scored 30 points as the Lakers defeated the Warriors.",
            source="test"
        )
        
        if success:
            print("✅ Single article processing successful")
        else:
            print("❌ Single article processing failed")
            return False
        
        # Test statistics
        print("Testing statistics retrieval...")
        stats = processor.get_entity_statistics()
        if stats:
            print("✅ Statistics retrieval successful")
            print(f"  - Total news articles: {stats.get('total_news_articles', 0)}")
            print(f"  - Total entities: {stats.get('total_entities', 0)}")
        else:
            print("❌ Statistics retrieval failed")
            return False
        
        # Test entity search
        print("Testing entity search...")
        results = processor.search_entities("LeBron", limit=5)
        if results:
            print("✅ Entity search successful")
            print(f"  - Found {len(results)} results for 'LeBron'")
        else:
            print("⚠️  No search results (this might be normal if no data exists)")
        
        return True
        
    except Exception as e:
        print(f"❌ News processor test failed: {e}")
        return False

def test_queries():
    """Test specific query functions"""
    print("\n=== Testing Query Functions ===")
    try:
        from nba_entity_extractor import NBAEntityExtractor
        
        extractor = NBAEntityExtractor()
        
        # Test injuries query
        print("Testing injuries query...")
        injuries = extractor.get_latest_injuries(limit=5)
        print(f"✅ Injuries query successful - found {len(injuries)} injuries")
        
        # Test technical fouls query
        print("Testing technical fouls query...")
        fouls = extractor.get_technical_fouls(limit=5)
        print(f"✅ Technical fouls query successful - found {len(fouls)} fouls")
        
        # Test team summaries query
        print("Testing team summaries query...")
        summaries = extractor.get_team_game_summaries("Lakers", limit=5)
        print(f"✅ Team summaries query successful - found {len(summaries)} summaries")
        
        return True
        
    except Exception as e:
        print(f"❌ Query functions test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏀 NBA Entity Extraction System Test")
    print("=" * 50)
    
    tests = [
        ("Database Schema", test_database_schema),
        ("Entity Extractor", test_entity_extractor),
        ("News Processor", test_news_processor),
        ("Query Functions", test_queries)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
