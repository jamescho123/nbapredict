import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='James',
    user='postgres',
    password='jcjc1749'
)

cursor = conn.cursor()

# Check for custom types (enums)
cursor.execute("""
    SELECT 
        t.typname,
        string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) as enum_values
    FROM pg_type t
    JOIN pg_enum e ON t.oid = e.enumtypid
    JOIN pg_namespace n ON t.typnamespace = n.oid
    WHERE n.nspname = 'public' OR n.nspname = 'NBA'
    GROUP BY t.typname
    ORDER BY t.typname;
""")

custom_types = cursor.fetchall()

print("=" * 60)
print("Custom Types (ENUM) in Database")
print("=" * 60)

if custom_types:
    for type_name, enum_values in custom_types:
        print(f"\nType: {type_name}")
        print(f"Values: {enum_values}")
        print(f"\nCREATE TYPE statement:")
        values = enum_values.split(', ')
        values_str = ', '.join([f"'{v}'" for v in values])
        print(f"CREATE TYPE {type_name} AS ENUM ({values_str});")
else:
    print("\nNo custom enum types found")

conn.close()

