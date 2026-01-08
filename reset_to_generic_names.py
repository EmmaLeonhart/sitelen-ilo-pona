import xml.etree.ElementTree as ET
import re
import io
import sys

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Parse the SVG
ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('sodipodi', 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')
ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')

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
                'element': child,
                'old_id': gid,
                'tx': tx,
                'ty': ty
            })

# Sort by position (ty ascending, then tx ascending)
top_level_groups.sort(key=lambda g: (g['ty'], g['tx']))

print(f"Found {len(top_level_groups)} top-level groups\n")
print("Renaming to generic IDs (symbol_1, symbol_2, ...):\n")
print(f"{'Old ID':<20} {'TX':>8} {'TY':>8} {'New ID':<15}")
print("=" * 60)

# Rename to generic IDs
for i, g in enumerate(top_level_groups, 1):
    new_id = f"symbol_{i}"
    old_id = g['old_id']

    g['element'].set('id', new_id)

    print(f"{old_id:<20} {g['tx']:8.1f} {g['ty']:8.1f} → {new_id:<15}")

# Save
tree.write('Sitelen Pona Sound Symbols.svg', encoding='UTF-8', xml_declaration=True)

print(f"\n✓ All {len(top_level_groups)} groups renamed to generic IDs")
print("✓ SVG saved")
