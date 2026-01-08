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

# Get vowel and consonant label positions
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

print("Grid labels:")
print("Vowels:", [f"{v['label']}@{v['x']:.0f}" for v in vowels])
print("Consonants:", [f"{c['label']}@{c['y']:.0f}" for c in consonants])

# Function to get center of content in a group
def get_content_center(group, ns):
    """Get approximate center of all paths/shapes in a group"""
    xs, ys = [], []

    # Check paths
    for path in group.findall('.//svg:path', ns):
        d = path.get('d', '')
        # Extract coordinates from path
        coords = re.findall(r'm\s+([\d.]+)[,\s]+([\d.]+)', d, re.IGNORECASE)
        for x, y in coords:
            xs.append(float(x))
            ys.append(float(y))

    # Check ellipses
    for ellipse in group.findall('.//svg:ellipse', ns):
        cx = float(ellipse.get('cx', 0))
        cy = float(ellipse.get('cy', 0))
        xs.append(cx)
        ys.append(cy)

    if xs and ys:
        return sum(xs) / len(xs), sum(ys) / len(ys)

    return None, None

# Find all top-level groups and calculate their final positions
groups = []
for child in root:
    if child.tag.endswith('g') and child.get('transform'):
        gid = child.get('id', '')
        transform = child.get('transform', '')

        match = re.search(r'translate\(([-\d.]+)[,\s]+([-\d.]+)\)', transform)
        if match:
            tx = float(match.group(1))
            ty = float(match.group(2))

            # Get content center
            cx, cy = get_content_center(child, ns)

            if cx is not None and cy is not None:
                # Apply transform to get final position
                final_x = cx + tx
                final_y = cy + ty

                groups.append({
                    'id': gid,
                    'tx': tx,
                    'ty': ty,
                    'content_x': cx,
                    'content_y': cy,
                    'final_x': final_x,
                    'final_y': final_y
                })

# Map to grid
def find_nearest_label(value, sorted_list):
    """Find nearest label in list of {label, x/y} dicts"""
    min_dist = float('inf')
    nearest = None
    for item in sorted_list:
        pos_key = 'x' if 'x' in item else 'y'
        dist = abs(item[pos_key] - value)
        if dist < min_dist:
            min_dist = dist
            nearest = item['label']
    return nearest, min_dist

print(f"\n\nMAPPING {len(groups)} GROUPS TO GRID:\n")
print(f"{'ID':<15} {'Final X':>8} {'Final Y':>8} {'Vowel':>6} {'Cons':>4} → {'Syllable':<6}")
print("=" * 70)

mapped = []
for g in sorted(groups, key=lambda x: (x['final_y'], x['final_x'])):
    vowel, vdist = find_nearest_label(g['final_x'], vowels)
    consonant, cdist = find_nearest_label(g['final_y'], consonants)

    syllable = f"{consonant}{vowel}"

    print(f"{g['id']:<15} {g['final_x']:8.0f} {g['final_y']:8.0f} {vowel:>6} {consonant:>4} → {syllable:<6}")

    mapped.append({
        'id': g['id'],
        'syllable': syllable
    })

# Check for duplicates
syllable_counts = defaultdict(int)
for m in mapped:
    syllable_counts[m['syllable']] += 1

duplicates = {syl: count for syl, count in syllable_counts.items() if count > 1}

if duplicates:
    print(f"\n\n⚠️  DUPLICATES FOUND:")
    for syl, count in sorted(duplicates.items()):
        print(f"  {syl}: {count} symbols")
else:
    print(f"\n\n✓ No duplicates - perfect 1:1 mapping!")

print(f"\nTotal unique syllables: {len(syllable_counts)}/50")
