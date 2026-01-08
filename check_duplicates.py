import io
import sys

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read the rename summary
with open('rename_summary.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

from collections import defaultdict

syllable_positions = defaultdict(list)

for line in lines[3:]:  # Skip header
    if '→' in line:
        parts = line.strip().split()
        if len(parts) >= 5:
            old_id = parts[0]
            new_id = parts[2]
            # Extract base syllable (remove _1, _2, etc.)
            base_syllable = new_id.split('_')[0]

            # Extract position
            pos_str = ' '.join(parts[4:])

            syllable_positions[base_syllable].append({
                'old_id': old_id,
                'new_id': new_id,
                'position': pos_str
            })

# Find duplicates
print("SYLLABLE POSITIONS WITH MULTIPLE GROUPS:")
print("=" * 70)

duplicates = {k: v for k, v in syllable_positions.items() if len(v) > 1}

for syllable in sorted(duplicates.keys()):
    groups = duplicates[syllable]
    print(f"\n{syllable}: {len(groups)} groups")
    for g in groups:
        print(f"  {g['old_id']:15} → {g['new_id']:15} at {g['position']}")

print(f"\n\nTOTAL SYLLABLES WITH DUPLICATES: {len(duplicates)}")
print(f"TOTAL DUPLICATE GROUPS: {sum(len(v) for v in duplicates.values())}")
print(f"\nSYLLABLES WITH SINGLE GROUP: {len([k for k, v in syllable_positions.items() if len(v) == 1])}")
