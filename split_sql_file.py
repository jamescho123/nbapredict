"""
Split large SQL file into smaller chunks for easier upload
"""

import os

input_file = 'nba_manual_export_20251024_201041.sql'
output_prefix = 'nba_export_part'

print("=" * 60)
print("Splitting SQL File")
print("=" * 60)
print()

if not os.path.exists(input_file):
    print(f"[ERROR] File not found: {input_file}")
    exit(1)

print(f"Reading {input_file}...")
with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File size: {len(content):,} characters")
print()

# Split into sections
sections = {
    '1_schema_and_setup': [],
    '2_table_structures': [],
    '3_data_inserts': []
}

lines = content.split('\n')
current_section = 'schema_and_setup'
current_table = None

print("Analyzing content...")
for line in lines:
    line_strip = line.strip()
    
    # Schema and extensions
    if line_strip.startswith('CREATE SCHEMA') or line_strip.startswith('CREATE EXTENSION'):
        sections['1_schema_and_setup'].append(line)
    
    # Table creation
    elif line_strip.startswith('DROP TABLE') or line_strip.startswith('CREATE TABLE'):
        current_section = 'table_structures'
        sections['2_table_structures'].append(line)
    
    # Table structure continuation
    elif current_section == 'table_structures' and not line_strip.startswith('INSERT'):
        sections['2_table_structures'].append(line)
        if line_strip.endswith(');'):
            current_section = 'data_inserts'
    
    # Data inserts
    elif line_strip.startswith('INSERT INTO'):
        sections['3_data_inserts'].append(line)
    
    # Comments and empty lines
    elif line_strip.startswith('--') or not line_strip:
        sections[f'{current_section}'].append(line) if f'{current_section}' in ['1_schema_and_setup', '2_table_structures', '3_data_inserts'] else sections['3_data_inserts'].append(line)

# Write sections to separate files
print()
print("Creating split files...")
file_info = []

for section_name, section_lines in sections.items():
    if not section_lines:
        continue
    
    filename = f"{output_prefix}{section_name}.sql"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(section_lines))
    
    size_kb = os.path.getsize(filename) / 1024
    line_count = len(section_lines)
    file_info.append((filename, size_kb, line_count))
    print(f"[OK] Created: {filename} ({size_kb:.1f} KB, {line_count:,} lines)")

print()
print("=" * 60)
print("Split Complete!")
print("=" * 60)
print()
print("Upload order:")
for i, (filename, size_kb, line_count) in enumerate(file_info, 1):
    print(f"{i}. {filename}")
print()
print("Instructions:")
print("1. Open Supabase SQL Editor:")
print("   https://supabase.com/dashboard/project/mxnpfsiyaqqwdcokukij/sql/new")
print()
print("2. Upload files in order:")
for i, (filename, _, _) in enumerate(file_info, 1):
    print(f"   {i}. Copy contents of {filename}")
    print(f"      Paste and RUN in Supabase")
    print()
print("3. Verify:")
print("   python verify_supabase_migration.py")

