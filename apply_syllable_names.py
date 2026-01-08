import xml.etree.ElementTree as ET
import re
import io
import sys
from collections import defaultdict

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Parse the SVG
ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('sodipodi', 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')
ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')

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
        transform = child.get('transform', '')

        match = re.search(r'translate\(([-\d.]+)[,\s]+([-\d.]+)\)', transform)
        if match:
            tx = float(match.group(1))
            ty = float(match.group(2))

            groups.append({
                'element': child,
                'tx': tx,
                'ty': ty
            })

# Sort by (TY, TX)
groups.sort(key=lambda g: (g['ty'], g['tx']))

# Group by rows (TY)
rows = defaultdict(list)
for g in groups:
    rows[g['ty']].append(g)

# Sort rows by TY
sorted_ty = sorted(rows.keys())

# Assign consonants to rows (skip TY=-36 incomplete row)
row_to_consonant = {}
consonant_idx = 0
for ty in sorted_ty:
    if ty == -36.0:  # Incomplete row
        row_to_consonant[ty] = None
    else:
        if consonant_idx < len(consonants):
            row_to_consonant[ty] = consonants[consonant_idx]['label']
            consonant_idx += 1

# Rename groups
print(f"{'Old ID':<15} {'TX':>6} {'TY':>8} → {'New ID':<15}")
print("=" * 60)

for ty in sorted_ty:
    row_groups = sorted(rows[ty], key=lambda g: g['tx'])
    consonant = row_to_consonant.get(ty)

    for col_idx, g in enumerate(row_groups):
        old_id = g['element'].get('id', '')

        if consonant and col_idx < len(vowels):
            vowel = vowels[col_idx]['label']
            new_id = f"{consonant}{vowel}"
        else:
            new_id = "incomplete_symbol"

        # Update the ID
        g['element'].set('id', new_id)

        print(f"{old_id:<15} {g['tx']:6.0f} {ty:8.0f} → {new_id:<15}")

# Save
tree.write('Sitelen Pona Sound Symbols.svg', encoding='UTF-8', xml_declaration=True)

print(f"\n✓ All groups renamed with syllable names!")
print("✓ SVG saved")
