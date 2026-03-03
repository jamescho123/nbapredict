import psycopg2
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = psycopg2.connect(
    host='localhost',
    database='James',
    user='postgres',
    password='jcjc1749'
)

cursor = conn.cursor()

# Total teams
cursor.execute('SELECT COUNT(*) FROM "NBA"."Teams"')
print(f"✓ Total teams in database: {cursor.fetchone()[0]}")

# Check for any remaining duplicates
cursor.execute('''
    SELECT "TeamName", COUNT(*)
    FROM "NBA"."Teams"
    GROUP BY "TeamName"
    HAVING COUNT(*) > 1
''')
dupes = cursor.fetchall()

if dupes:
    print(f"\n⚠️ Still have {len(dupes)} duplicates:")
    for team, count in dupes:
        print(f"  {team}: {count} entries")
else:
    print("✓ No duplicates - all team names are unique!")

# Check Atlanta Hawks specifically
cursor.execute('''
    SELECT "TeamID", "TeamName", "From", "To"
    FROM "NBA"."Teams"
    WHERE "TeamName" = 'Atlanta Hawks'
''')

hawks = cursor.fetchall()
print(f"\n✓ Atlanta Hawks:")
for team_id, name, from_year, to_year in hawks:
    print(f"  ID={team_id}, From={from_year}, To={to_year}")

cursor.close()
conn.close()


