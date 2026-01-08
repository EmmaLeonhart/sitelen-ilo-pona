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

# Categorize and sort
vowels = sorted([t for t in texts if t['label'] in ['a', 'i', 'u', 'e', 'o']], key=lambda t: t['x'])
consonants = sorted([t for t in texts if t['label'] not in ['a', 'i', 'u', 'e', 'o']], key=lambda t: t['y'])

print("GRID POSITIONS:")
print("\nVowels (X-axis):")
for v in vowels:
    print(f"  {v['label']}: x = {v['x']:.1f}")

print("\nConsonants (Y-axis):")
for c in consonants:
    print(f"  {c['label']}: y = {c['y']:.1f}")

# Calculate midpoints for boundaries
vowel_list = [(v['label'], v['x']) for v in vowels]
consonant_list = [(c['label'], c['y']) for c in consonants]

def find_nearest(value, sorted_list):
    """Find the nearest label in a sorted list of (label, position) tuples"""
    min_dist = float('inf')
    nearest = None

    for label, pos in sorted_list:
        dist = abs(value - pos)
        if dist < min_dist:
            min_dist = dist
            nearest = label

    return nearest

# Find all top-level groups (direct children of root or major container groups)
# Look for groups that have IDs and transforms
groups_to_rename = []

# Get direct children groups with transforms
for group in root.findall('.//svg:g[@id][@transform]', ns):
    gid = group.get('id', '')

    # Only process groups with numeric or simple IDs (the symbol groups)
    # Skip groups that look like sub-components
    if gid and (gid.startswith('g1') or gid.startswith('g2')):
        transform = group.get('transform', '')
        match = re.search(r'translate\(([-\d.]+)[,\s]+([-\d.]+)\)', transform)

        if match:
            tx = float(match.group(1))
            ty = float(match.group(2))

            groups_to_rename.append({
                'element': group,
                'old_id': gid,
                'tx': tx,
                'ty': ty
            })

print(f"\n\nFound {len(groups_to_rename)} groups to rename")
print("\n" + "=" * 80)

# For each group, use ONLY the transform position to determine the grid cell
renamed = []
syllable_counts = defaultdict(int)

# First pass: determine syllables and count
for g in groups_to_rename:
    # The transform typically has an offset, let's look at the actual positions
    # Many have negative Y offsets, so let's adjust
    adjusted_x = g['tx']
    adjusted_y = g['ty'] + 116  # Common offset seems to be -116

    # Find nearest vowel and consonant
    vowel = find_nearest(adjusted_x, vowel_list)
    consonant = find_nearest(adjusted_y, consonant_list)

    syllable = f"{consonant}{vowel}"
    g['syllable'] = syllable
    syllable_counts[syllable] += 1

# Second pass: rename with indices if needed
syllable_indices = defaultdict(int)

for g in sorted(groups_to_rename, key=lambda x: (x['ty'], x['tx'])):
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

    adjusted_y = g['ty'] + 116

    print(f"{old_id:15} at ({g['tx']:6.1f}, {g['ty']:6.1f}) → adjusted Y: {adjusted_y:6.1f} → {new_id:15}")

    renamed.append({
        'old': old_id,
        'new': new_id,
        'syllable': syllable
    })

# Save the modified SVG
tree.write('Sitelen Pona Sound Symbols.svg', encoding='UTF-8', xml_declaration=True)

print(f"\n\n✓ Successfully renamed {len(renamed)} groups!")

# Summary by syllable
print("\n\nGROUPS PER SYLLABLE:")
from collections import Counter
syllable_summary = Counter([r['syllable'] for r in renamed])
for syllable in sorted(syllable_summary.keys()):
    count = syllable_summary[syllable]
    marker = " ⚠️ MULTIPLE" if count > 1 else ""
    print(f"  {syllable}: {count}{marker}")

print(f"\nTotal syllables with multiple groups: {sum(1 for c in syllable_summary.values() if c > 1)}")
