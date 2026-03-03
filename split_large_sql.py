import sys

def split_sql_file(filename, max_size_mb=10):
    max_size = max_size_mb * 1024 * 1024
    
    print(f"Splitting {filename} into {max_size_mb}MB chunks...")
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    part_num = 1
    current_size = 0
    current_lines = []
    
    for line in lines:
        line_size = len(line.encode('utf-8'))
        
        if current_size + line_size > max_size and current_lines:
            output_file = f"{filename.rsplit('.', 1)[0]}_part{part_num}.sql"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(current_lines))
            print(f"Created {output_file} ({current_size / 1024 / 1024:.2f}MB)")
            
            part_num += 1
            current_lines = []
            current_size = 0
        
        current_lines.append(line)
        current_size += line_size
    
    if current_lines:
        output_file = f"{filename.rsplit('.', 1)[0]}_part{part_num}.sql"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(current_lines))
        print(f"Created {output_file} ({current_size / 1024 / 1024:.2f}MB)")
    
    print(f"\nCreated {part_num} parts")
    print("Execute each part in Supabase SQL Editor in order")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python split_large_sql.py <sql_file> [max_size_mb]")
        print("Example: python split_large_sql.py nba_export.sql 10")
        sys.exit(1)
    
    filename = sys.argv[1]
    max_size_mb = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    split_sql_file(filename, max_size_mb)

