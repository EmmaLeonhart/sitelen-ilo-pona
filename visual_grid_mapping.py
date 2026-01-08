import xml.etree.ElementTree as ET
import re
import io
import sys

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Parse the SVG
tree = ET.parse('Sitelen Pona Sound Symbols.svg')
root = tree.getroot()

ns = {'svg': 'http://www.w3.org/2000/svg'}

# Get vowel and consonant labels
texts = []
for text_elem in root.findall('.//svg:text', ns):
    x = float(text_elem.get('x', 0))
    y = float(text_elem.get('y', 0))
    tspan = text_elem.find('.//svg:tspan', ns)
    if tspan is not None and tspan.text:
        label = tspan.text.strip()
        texts.append({'label': label, 'x': x, 'y': y})

vowels = sorted([t for t in texts if t['label'] in ['a', 'i', 'u', 'e', 'o']], key=lambda t: t['x'])
consonants = sorted([t for t in texts if t['label'] not in ['a', 'i', 'u', 'e', 'o']], key=lambda t: t['y'])

print("Grid structure:")
print("Vowels (X-axis):", ', '.join([f"{v['label']}@{v['x']:.0f}" for v in vowels]))
print("Consonants (Y-axis):", ', '.join([f"{c['label']}@{c['y']:.0f}" for c in consonants]))

# The symbols' APPROXIMATE visual position is where we should look
# For a group with transform translate(TX, TY), the visual center is roughly at the labels + some offset

# Find all top-level groups
groups = []
for child in root:
    if child.tag.endswith('g') and child.get('transform'):
        gid = child.get('id', '')
        transform = child.get('transform', '')

        match = re.search(r'translate\(([-\d.]+)[,\s]+([-\d.]+)\)', transform)
        if match:
            tx = float(match.group(1))
            ty = float(match.group(2))

            groups.append({
                'id': gid,
                'tx': tx,
                'ty': ty
            })

# Hypothesis: The transform positions them relative to some base pattern
# Let's look at the patterns in the transform values

print(f"\n\nUnique TY values: {sorted(set(g['ty'] for g in groups))}")
print(f"Unique TX values: {sorted(set(g['tx'] for g in groups))}\n")

# The TX values [0, 10, 28, 44] might correspond to columns
# but many rows have 2 symbols at TX=0!
# This suggests the symbols aren't perfectly aligned to transform values alone

# Let's try: sort all groups by (TY, TX) and number them sequentially
# Then map them row-by-row to the grid

groups.sort(key=lambda g: (g['ty'], g['tx']))

print("Mapping groups sequentially (row-by-row, left-to-right):")
print(f"{'#':>3} {'ID':<15} {'TX':>6} {'TY':>8} {'Vowel':>5} {'Cons':>4} → {'Syllable'}")
print("=" * 70)

# Group by rows (TY)
from collections import defaultdict
rows = defaultdict(list)
for g in groups:
    rows[g['ty']].append(g)

# Sort rows by TY
sorted_ty = sorted(rows.keys())

# Assign consonants to rows (top to bottom)
row_to_consonant = {}
if len(sorted_ty) == 11:
    # We have 11 rows but 10 consonants - one row must be incomplete/extra
    # Let's skip the incomplete one (TY=-36 has only 1 symbol)
    consonant_idx = 0
    for ty in sorted_ty:
        if ty == -36.0:  # Skip this incomplete row
            row_to_consonant[ty] = "?"
        else:
            if consonant_idx < len(consonants):
                row_to_consonant[ty] = consonants[consonant_idx]['label']
                consonant_idx += 1

result = []
symbol_num = 0

for ty in sorted_ty:
    row_groups = sorted(rows[ty], key=lambda g: g['tx'])
    consonant = row_to_consonant.get(ty, "?")

    for col_idx, g in enumerate(row_groups):
        symbol_num += 1

        # Assign vowel by position in row (left to right)
        if col_idx < len(vowels):
            vowel = vowels[col_idx]['label']
        else:
            vowel = "?"

        syllable = f"{consonant}{vowel}" if consonant != "?" and vowel != "?" else "??"

        print(f"{symbol_num:3} {g['id']:<15} {g['tx']:6.0f} {ty:8.0f} {vowel:>5} {consonant:>4} → {syllable}")

        result.append({
            'id': g['id'],
            'syllable': syllable
        })

# Check unique syllables
from collections import Counter
syl_counts = Counter([r['syllable'] for r in result])
print(f"\n\nUnique syllables mapped: {len([s for s in syl_counts if s != '??'])}")
duplicates = {s: c for s, c in syl_counts.items() if c > 1 and s != '??'}
if duplicates:
    print(f"Duplicates: {duplicates}")
