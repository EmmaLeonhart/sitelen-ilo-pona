import xml.etree.ElementTree as ET
import re
import io
import sys
from collections import defaultdict

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Parse the SVG
tree = ET.parse('Sitelen Pona Sound Symbols.svg')
root = tree.getroot()

ns = {'svg': 'http://www.w3.org/2000/svg'}

# Find vowel and consonant text labels
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

print("GRID LABELS:")
print("\nVowels (columns):")
for i, v in enumerate(vowels):
    print(f"  Column {i}: {v['label']} at x={v['x']:.1f}")

print("\nConsonants (rows):")
for i, c in enumerate(consonants):
    print(f"  Row {i}: {c['label']} at y={c['y']:.1f}")

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

# Group by TY value to see row structure
rows = defaultdict(list)
for g in groups:
    rows[g['ty']].append(g)

# Sort rows by TY
sorted_rows = sorted(rows.items(), key=lambda x: x[0])

print(f"\n\nGROUP DISTRIBUTION BY ROW (TY value):")
print(f"{'TY':>8} | {'Count':>5} | TX values")
print("=" * 50)

for ty, row_groups in sorted_rows:
    tx_values = sorted([g['tx'] for g in row_groups])
    tx_str = ', '.join([f"{tx:.0f}" for tx in tx_values])
    print(f"{ty:8.0f} | {len(row_groups):5} | {tx_str}")

# Identify unique TX and TY values
unique_tx = sorted(set(g['tx'] for g in groups))
unique_ty = sorted(set(g['ty'] for g in groups))

print(f"\n\nUNIQUE VALUES:")
print(f"TX (columns): {len(unique_tx)} distinct values: {unique_tx}")
print(f"TY (rows): {len(unique_ty)} distinct values")

print(f"\n\nEXPECTED GRID: 10 consonants × 5 vowels = 50 cells")
print(f"ACTUAL GROUPS: {len(groups)}")
print(f"\nNote: Many rows have duplicate TX values, suggesting overlapping symbols")
print("or groups that aren't perfectly aligned to a grid")
