import psycopg2
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# Check columns
cursor.execute('SELECT * FROM "NBA"."Teams" LIMIT 1')
columns = [desc[0] for desc in cursor.description]
print("Teams table columns:", columns)

# Check for duplicates
cursor.execute('''
    SELECT "Team_Name", COUNT(*) 
    FROM "NBA"."Teams" 
    GROUP BY "Team_Name" 
    HAVING COUNT(*) > 1
''')

duplicates = cursor.fetchall()
print(f"\nDuplicate teams: {len(duplicates)}")
for team, count in duplicates:
    print(f"  {team}: {count} entries")

cursor.close()
conn.close()


