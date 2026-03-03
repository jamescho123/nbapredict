"""
Clean duplicate teams from NBA.Teams table
Keep the oldest team (earliest From year) for each team name
"""

import psycopg2
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    'host': 'localhost',
    'database': 'James',
    'user': 'postgres',
    'password': 'jcjc1749'
}

DB_SCHEMA = 'NBA'

def clean_duplicate_teams():
    print("="*80)
    print("NBA Teams Table - Remove Duplicates")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # First, check what columns exist
        cursor.execute(f'SELECT * FROM "{DB_SCHEMA}"."Teams" LIMIT 1')
        columns = [desc[0] for desc in cursor.description]
        print(f"Table columns: {columns}\n")
        
        # Find all team names with duplicates
        cursor.execute(f'''
            SELECT "TeamName", COUNT(*) as count
            FROM "{DB_SCHEMA}"."Teams"
            GROUP BY "TeamName"
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC
        ''')
        
        duplicates = cursor.fetchall()
        
        if not duplicates:
            print("✓ No duplicate teams found!")
            return
        
        print(f"Found {len(duplicates)} team names with duplicates:\n")
        
        total_deleted = 0
        
        for team_name, count in duplicates:
            print(f"\n{'='*80}")
            print(f"Team: {team_name} ({count} entries)")
            print(f"{'='*80}")
            
            # Get all entries for this team
            cursor.execute(f'''
                SELECT "TeamID", "TeamName", "From", "To", "Conference", "Division"
                FROM "{DB_SCHEMA}"."Teams"
                WHERE "TeamName" = %s
                ORDER BY "From" ASC NULLS LAST, "TeamID" ASC
            ''', (team_name,))
            
            teams = cursor.fetchall()
            
            # Display all entries
            print("\nAll entries for this team:")
            for i, team in enumerate(teams, 1):
                team_id, name, from_year, to_year, conf, div = team
                from_str = from_year if from_year else "Unknown"
                to_str = to_year if to_year else "Present"
                print(f"  {i}. ID={team_id}, From={from_str}, To={to_str}, "
                      f"Conference={conf}, Division={div}")
            
            # Keep the first one (oldest/earliest from year)
            keep_team = teams[0]
            delete_teams = teams[1:]
            
            keep_id = keep_team[0]
            keep_from = keep_team[2] if keep_team[2] else "Unknown"
            
            print(f"\n✓ KEEPING: TeamID={keep_id}, From={keep_from}")
            print(f"✗ DELETING {len(delete_teams)} duplicate(s):")
            
            # Delete the duplicates
            for team in delete_teams:
                delete_id = team[0]
                delete_from = team[2] if team[2] else "Unknown"
                print(f"  - TeamID={delete_id}, From={delete_from}")
                
                cursor.execute(f'''
                    DELETE FROM "{DB_SCHEMA}"."Teams"
                    WHERE "TeamID" = %s
                ''', (delete_id,))
                
                total_deleted += 1
        
        # Commit changes
        conn.commit()
        
        print(f"\n{'='*80}")
        print("CLEANUP SUMMARY")
        print(f"{'='*80}")
        print(f"Teams with duplicates: {len(duplicates)}")
        print(f"Total entries deleted: {total_deleted}")
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("✓ Changes committed to database!")
        
        # Verify cleanup
        print(f"\n{'='*80}")
        print("VERIFICATION")
        print(f"{'='*80}")
        
        cursor.execute(f'''
            SELECT "TeamName", COUNT(*) as count
            FROM "{DB_SCHEMA}"."Teams"
            GROUP BY "TeamName"
            HAVING COUNT(*) > 1
        ''')
        
        remaining_dupes = cursor.fetchall()
        
        if remaining_dupes:
            print(f"⚠️ Still have {len(remaining_dupes)} teams with duplicates:")
            for team_name, count in remaining_dupes:
                print(f"  - {team_name}: {count} entries")
        else:
            print("✓ No duplicates remaining!")
        
        # Show final team count
        cursor.execute(f'SELECT COUNT(*) FROM "{DB_SCHEMA}"."Teams"')
        total_teams = cursor.fetchone()[0]
        print(f"\nTotal teams in database: {total_teams}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        print("Changes rolled back.")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    clean_duplicate_teams()


