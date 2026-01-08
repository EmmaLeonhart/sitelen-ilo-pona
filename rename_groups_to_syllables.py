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

# Define namespaces
ns = {
    'svg': 'http://www.w3.org/2000/svg',
    'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
    'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
}

# Extract text positions for vowels and consonants
texts = []
for text_elem in root.findall('.//svg:text', ns):
    x = float(text_elem.get('x', 0))
    y = float(text_elem.get('y', 0))
    tspan = text_elem.find('.//svg:tspan', ns)
    if tspan is not None and tspan.text:
        label = tspan.text.strip()
        texts.append({'label': label, 'x': x, 'y': y})

# Categorize
vowels = [t for t in texts if t['label'] in ['a', 'i', 'u', 'e', 'o']]
consonants = [t for t in texts if t['label'] not in ['a', 'i', 'u', 'e', 'o']]

vowels.sort(key=lambda t: t['x'])
consonants.sort(key=lambda t: t['y'])

# Mapping functions
def map_x_to_vowel(x):
    if x < 250:
        return 'a'
    elif x < 400:
        return 'i'
    elif x < 550:
        return 'u'
    elif x < 700:
        return 'e'
    else:
        return 'o'

def map_y_to_consonant(y):
    if y < 220:
        return 'M'
    elif y < 380:
        return 'N'
    elif y < 520:
        return 'P'
    elif y < 650:
        return 'T'
    elif y < 770:
        return 'K'
    elif y < 870:
        return 'S'
    elif y < 980:
        return 'w'
    elif y < 1090:
        return 'y'
    elif y < 1200:
        return 'l'
    else:
        return 'x'

# Find the bounding box or representative point for a group
def get_group_center(group, ns):
    """Calculate approximate center of a group based on its shapes"""
    coords = []

    # Check all paths in this group
    for path in group.findall('.//svg:path', ns):
        d = path.get('d', '')
        # Extract move commands
        matches = re.findall(r'm\s+([\d.]+)[,\s]+([\d.]+)', d, re.IGNORECASE)
        for m in matches:
            coords.append((float(m[0]), float(m[1])))

    # Check ellipses
    for ellipse in group.findall('.//svg:ellipse', ns):
        cx = float(ellipse.get('cx', 0))
        cy = float(ellipse.get('cy', 0))
        coords.append((cx, cy))

    if coords:
        avg_x = sum(c[0] for c in coords) / len(coords)
        avg_y = sum(c[1] for c in coords) / len(coords)
        return avg_x, avg_y

    return None, None

# Get all top-level groups (those that are direct children of main group containers)
# We want to rename groups that actually contain the symbols
groups_to_rename = []

for group in root.findall('.//svg:g[@id]', ns):
    gid = group.get('id', '')

    # Only process groups that start with 'g1' and are main symbol groups
    # These are the groups with transform attributes at the top level
    if gid.startswith('g1') and group.get('transform'):
        transform = group.get('transform', '')
        match = re.search(r'translate\(([-\d.]+)[,\s]+([-\d.]+)\)', transform)

        if match:
            tx = float(match.group(1))
            ty = float(match.group(2))

            # Get center of shapes in this group
            cx, cy = get_group_center(group, ns)

            if cx is not None and cy is not None:
                # Apply transform to get actual position
                actual_x = cx + tx
                actual_y = cy + ty

                # Map to syllable
                vowel = map_x_to_vowel(actual_x)
                consonant = map_y_to_consonant(actual_y)
                syllable = f"{consonant}{vowel}"

                groups_to_rename.append({
                    'element': group,
                    'old_id': gid,
                    'syllable': syllable,
                    'x': actual_x,
                    'y': actual_y
                })

# Count syllables to handle duplicates
syllable_counts = defaultdict(int)
for g in groups_to_rename:
    syllable_counts[g['syllable']] += 1

# Rename groups
syllable_indices = defaultdict(int)
renamed = []

for g in groups_to_rename:
    syllable = g['syllable']
    old_id = g['old_id']

    # If multiple groups for same syllable, add index
    if syllable_counts[syllable] > 1:
        syllable_indices[syllable] += 1
        new_id = f"{syllable}_{syllable_indices[syllable]}"
    else:
        new_id = syllable

    # Update the ID
    g['element'].set('id', new_id)

    renamed.append({
        'old': old_id,
        'new': new_id,
        'syllable': syllable,
        'position': f"({g['x']:.0f}, {g['y']:.0f})"
    })

    print(f"Renamed: {old_id:15} → {new_id:15} (position: {g['x']:6.0f}, {g['y']:6.0f})")

# Save the modified SVG
tree.write('Sitelen Pona Sound Symbols.svg', encoding='UTF-8', xml_declaration=True)

print(f"\n✓ Successfully renamed {len(renamed)} groups!")
print(f"✓ SVG saved to: Sitelen Pona Sound Symbols.svg")

# Create a summary file
with open('rename_summary.txt', 'w', encoding='utf-8') as f:
    f.write("SVG Group Renaming Summary\n")
    f.write("=" * 60 + "\n\n")

    for item in sorted(renamed, key=lambda x: x['syllable']):
        f.write(f"{item['old']:15} → {item['new']:15} at {item['position']}\n")

    f.write(f"\nTotal: {len(renamed)} groups renamed\n")

print(f"✓ Summary saved to: rename_summary.txt")
