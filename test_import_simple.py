#!/usr/bin/env python3
"""
Simple test to check if we can connect to database and import basic data
"""

import psycopg2
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Database connection successful")
        
        cursor = conn.cursor()
        cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."Teams"')
        team_count = cursor.fetchone()[0]
        print(f"📊 Found {team_count} teams in database")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_import_simple():
    """Test simple data import"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create a simple test table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS "{DB_SCHEMA}"."Test2024_25" (
                "ID" SERIAL PRIMARY KEY,
                "Team" VARCHAR(50),
                "Wins" INTEGER,
                "Losses" INTEGER
            );
        ''')
        
        # Insert test data
        cursor.execute(f'''
            INSERT INTO "{DB_SCHEMA}"."Test2024_25" ("Team", "Wins", "Losses")
            VALUES ('Boston Celtics', 64, 18)
        ''')
        
        conn.commit()
        print("✅ Test data imported successfully")
        
        # Verify data
        cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."Test2024_25"')
        result = cursor.fetchone()
        print(f"📊 Test data: {result}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing 2024-25 Season Import Setup")
    print("=" * 40)
    
    if test_connection():
        if test_import_simple():
            print("\n✅ All tests passed! Ready for full import.")
        else:
            print("\n❌ Import test failed.")
    else:
        print("\n❌ Connection test failed.")
