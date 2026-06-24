#!/usr/bin/env python3
"""Remove duplicate JSON keys from AeomTask.json"""
import json
import re
from collections import Counter

path = r'd:\Code\MaaSrc\MaaAssistantArknights\resource\tasks\Temp\AeomTask.json'

# Read file
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
print(f'Original: {len(lines)} lines')

# Find duplicate keys at top level
dup_keys = []
def check_dups(pairs):
    keys = [k for k, v in pairs]
    counts = Counter(keys)
    dups = [k for k, c in counts.items() if c > 1]
    dup_keys.extend(dups)
    return dict(pairs)

with open(path, 'r', encoding='utf-8') as f:
    json.load(f, object_pairs_hook=check_dups)

print(f'Duplicate keys: {len(dup_keys)}')
for dk in dup_keys:
    print(f'  - {dk}')

# Find second occurrence line numbers
second_lines = []
for dk in dup_keys:
    pattern = r'\n(\s*\"' + re.escape(dk) + r'\"\s*:)'
    matches = list(re.finditer(pattern, content))
    if len(matches) >= 2:
        line2 = content[:matches[1].start()].count('\n') + 1
        second_lines.append(line2)
        n1 = content[:matches[0].start()].count('\n') + 1
        print(f'  {dk[:30]}... : 1st=line{n1}, 2nd=line{line2}')

second_lines.sort()
start_line = second_lines[0]
end_line = second_lines[-1]
print(f'\nSecond block starts at line {start_line}')

# Find the end of the last duplicate entry
# The last dup key is 195003, find where its value block ends
last_dup = dup_keys[-1]
# Find the second occurrence of the last dup key
pattern = r'\n(\s*\"' + re.escape(last_dup) + r'\"\s*:)'
matches = list(re.finditer(pattern, content))
if len(matches) >= 2:
    # Find the closing } of this entry
    # Search from the second occurrence onwards for the next top-level key
    start_pos = matches[1].start()
    # Look for the next top-level key after this dup block
    # Find all top-level keys after start_pos
    after = content[start_pos:]
    # Find next \"key\" pattern at top level
    next_keys = list(re.finditer(r'\n\s*\"', after))
    # The second one (first is the current key) should be the next entry
    if len(next_keys) >= 2:
        end_pos = start_pos + next_keys[1].start()
        end_line_num = content[:end_pos].count('\n') + 1
        print(f'Second block ends at line {end_line_num}')
        
        # Extract the block to remove
        block_to_remove = content[start_pos:end_pos]
        print(f'Block to remove: {len(block_to_remove)} chars, {block_to_remove.count(chr(10))} lines')
        
        # Preview first and last 3 lines of block
        block_lines = block_to_remove.split('\n')
        print('\nFirst 3 lines:')
        for l in block_lines[:3]:
            print(f'  {repr(l)}')
        print('Last 3 lines:')
        for l in block_lines[-4:-1]:
            print(f'  {repr(l)}')
        
        # Remove it
        new_content = content[:start_pos] + content[end_pos:]
        
        # Write back
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f'\nNew file: {new_content.count(chr(10))+1} lines')
        
        # Verify
        with open(path, 'r', encoding='utf-8') as f:
            json.load(f)
        print('JSON valid!')
        
        # Check for remaining dupes
        remain_dups = []
        def check2(pairs):
            keys = [k for k,v in pairs]
            counts = Counter(keys)
            for k,c in counts.items():
                if c > 1:
                    remain_dups.append(k)
            return dict(pairs)
        with open(path, 'r', encoding='utf-8') as f:
            json.load(f, object_pairs_hook=check2)
        print(f'Remaining duplicates: {len(remain_dups)}')
        if remain_dups:
            for dk in remain_dups:
                print(f'  - {dk}')
