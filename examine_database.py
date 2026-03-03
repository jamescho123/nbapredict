#!/usr/bin/env python3
"""
Script to examine the NBA database schema and available data
"""

import psycopg2
import pandas as pd

def examine_database():
    """Examine the NBA database structure and data"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        print("🏀 NBA Database Examination")
        print("=" * 50)
        
        # Get all tables in NBA schema
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'NBA' 
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        print(f"\n📊 Available Tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Examine each table structure and sample data
        for table_name in [table[0] for table in tables]:
            print(f"\n🔍 Table: {table_name}")
            print("-" * 30)
            
            # Get column information
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'NBA' AND table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            columns = cur.fetchall()
            
            print("Columns:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
            # Get row count
            cur.execute(f'SELECT COUNT(*) FROM "NBA"."{table_name}";')
            count = cur.fetchone()[0]
            print(f"Row count: {count}")
            
            # Get sample data (first 3 rows)
            if count > 0:
                cur.execute(f'SELECT * FROM "NBA"."{table_name}" LIMIT 3;')
                sample_data = cur.fetchall()
                print("Sample data:")
                for i, row in enumerate(sample_data, 1):
                    print(f"  Row {i}: {row}")
            
            print()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error examining database: {e}")
        return False

if __name__ == "__main__":
    examine_database()
