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

# Sort by TY (rows), then TX (columns)
groups.sort(key=lambda g: (g['ty'], g['tx']))

# Identify distinct TY values (rows) - these correspond to consonants
distinct_ty = sorted(set(g['ty'] for g in groups))

# Map each distinct TY to a consonant (row)
print("Mapping TY values to consonant rows:")
ty_to_consonant = {}
if len(distinct_ty) <= len(consonants):
    for i, ty in enumerate(distinct_ty):
        ty_to_consonant[ty] = consonants[i]['label']
        print(f"  TY={ty:6.0f} → {consonants[i]['label']}")
else:
    print(f"  ⚠️  More TY values ({len(distinct_ty)}) than consonants ({len(consonants)})!")

# Identify distinct TX values (columns) - these correspond to vowels
distinct_tx = sorted(set(g['tx'] for g in groups))

print(f"\nDistinct TX values (should be 5 for 5 vowels): {distinct_tx}")

# Since we have overlaps (multiple groups at same TX in a row),
# let's enumerate within each row
print(f"\n\nMANUAL GRID MAPPING:")
print(f"Looking at each row and assigning vowels left-to-right...\n")

from collections import defaultdict

row_groups = defaultdict(list)
for g in groups:
    row_groups[g['ty']].append(g)

# Sort groups within each row by TX
for ty in row_groups:
    row_groups[ty].sort(key=lambda g: g['tx'])

# Map each group
result = []
for ty in sorted(row_groups.keys()):
    if ty not in ty_to_consonant:
        print(f"⚠️  TY={ty} has no consonant mapping, skipping")
        continue

    consonant = ty_to_consonant[ty]
    row = row_groups[ty]

    print(f"Row {consonant} (TY={ty}): {len(row)} groups")

    # Assign vowels in order
    for i, g in enumerate(row):
        if i < len(vowels):
            vowel = vowels[i]['label']
            syllable = f"{consonant}{vowel}"

            print(f"  {g['id']:<15} TX={g['tx']:5.0f} → {syllable}")

            result.append({
                'id': g['id'],
                'syllable': syllable
            })
        else:
            print(f"  {g['id']:<15} TX={g['tx']:5.0f} → ⚠️  EXTRA (row has more than 5 groups!)")

print(f"\n\nTotal mapped: {len(result)}/50")
