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

# Find all DIRECT children of root that are groups with transforms
top_level_groups = []

for child in root:
    if child.tag.endswith('g') and child.get('transform'):
        gid = child.get('id', '')
        transform = child.get('transform', '')

        match = re.search(r'translate\(([-\d.]+)[,\s]+([-\d.]+)\)', transform)
        if match:
            tx = float(match.group(1))
            ty = float(match.group(2))

            top_level_groups.append({
                'id': gid,
                'tx': tx,
                'ty': ty
            })

# Sort by position (ty, then tx)
top_level_groups.sort(key=lambda g: (g['ty'], g['tx']))

print(f"Found {len(top_level_groups)} top-level groups:\n")
print(f"{'ID':<20} {'TX':>8} {'TY':>8}")
print("=" * 40)

for g in top_level_groups:
    print(f"{g['id']:<20} {g['tx']:8.1f} {g['ty']:8.1f}")
