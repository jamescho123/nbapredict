"""Fix indentation in Backtest_Analysis.py"""

# Read the file
with open('pages/Backtest_Analysis.py', 'r', encoding='utf-8') as f:
    lines = f.lines()

# Find lines 644-738 and add 4 spaces to each
fixed_lines = []
in_if_block = False
block_start = 644

for i, line in enumerate(lines, 1):
    if i >= 644 and i <= 738:
        # Add 4 spaces to lines that need more indentation
        if line.strip() and not line.startswith(' ' * 16):
            # Add 12 more spaces (current 4 + 12 = 16 total)
            fixed_lines.append('            ' + line.lstrip())
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Write back
with open('pages/Backtest_Analysis.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Fixed indentation!")








