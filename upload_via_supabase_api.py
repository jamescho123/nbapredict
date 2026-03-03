"""
Alternative: Upload using Supabase REST API instead of direct PostgreSQL connection
This may work better if PostgreSQL port is blocked
"""

import requests
import json
import psycopg2

SUPABASE_URL = 'https://mxnpfsiyaqqwdcokukij.supabase.co'
# You need to get the service_role key from Supabase dashboard
# Go to: Project Settings > API > service_role key (secret)
SUPABASE_SERVICE_KEY = 'YOUR_SERVICE_ROLE_KEY_HERE'

def get_local_data():
    """Get data from local PostgreSQL"""
    print("Connecting to local database...")
    conn = psycopg2.connect(
        host='localhost',
        database='James',
        user='postgres',
        password='jcjc1749'
    )
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'NBA'
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    data = {}
    for table in tables:
        print(f"Reading {table}...")
        cursor.execute(f'SELECT * FROM "NBA"."{table}";')
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        
        data[table] = {
            'columns': cols,
            'rows': rows
        }
    
    conn.close()
    return data

def upload_to_supabase_api(data):
    """Upload data using Supabase REST API"""
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    for table, table_data in data.items():
        print(f"Uploading {table}...")
        
        # Convert rows to list of dicts
        records = []
        for row in table_data['rows']:
            record = {}
            for i, col in enumerate(table_data['columns']):
                record[col] = row[i]
            records.append(record)
        
        # Upload in batches
        batch_size = 100
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            url = f'{SUPABASE_URL}/rest/v1/NBA.{table}'
            
            try:
                response = requests.post(url, json=batch, headers=headers)
                if response.status_code == 201:
                    print(f"  Uploaded batch {i//batch_size + 1}")
                else:
                    print(f"  Error: {response.text}")
            except Exception as e:
                print(f"  Error: {e}")

def main():
    print("=" * 60)
    print("Upload to Supabase via REST API")
    print("=" * 60)
    print()
    
    if SUPABASE_SERVICE_KEY == 'YOUR_SERVICE_ROLE_KEY_HERE':
        print("[ERROR] Please set your Supabase service_role key")
        print()
        print("Get it from:")
        print("https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/settings/api")
        print()
        print("Look for: service_role (secret)")
        return
    
    # Get local data
    data = get_local_data()
    
    # Upload to Supabase
    upload_to_supabase_api(data)

if __name__ == "__main__":
    main()

